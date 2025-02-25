import json
import re
from typing import List, Dict, Any
from loguru import logger
from dependency_injector.wiring import Provide
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.tests.prompts import (
    TEST_CONTEXT_PROMPT,
    FILTER_PROMPT
)


class TestGenerationPipeline:
    """
    A pipeline that, for each Task:
      1) Asks the LLM to propose minimal test definitions referencing relevant test classes.
      2) Filters out guess-based or redundant tests.
      3) Proposes a final Boolean expression referencing x(i,j) for overall success (logic).
    """

    def __init__(
        self,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500,
    ):
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars

    async def filter_generated_tests(
        self,
        proposed_tests: List[Dict[str, Any]],
        truncated_html: str,
        task: Task
    ) -> List[Dict[str, Any]]:
        """
        Uses the LLM to filter out:
          1) Duplicate tests (identical signatures)
          2) Guess-based or domain-mismatch tests
          3) Redundant front-end vs back-end overlaps
          4) Tests that don't align with the task's success criteria
        Returns the valid tests after filtering.
        """
        if not proposed_tests:
            return []

        # 1) Basic duplicate removal using a signature
        filtered_duplicates = []
        seen_signatures = set()
        for test_config in proposed_tests:
            signature = self._create_test_signature(test_config)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                filtered_duplicates.append(test_config)

        if not filtered_duplicates:
            return []

        # Build a user prompt for the LLM-based filter
        current_domain = self._extract_domain(task.url)

        # Number each test for reference
        numbered_tests = []
        for i, test in enumerate(filtered_duplicates):
            numbered_tests.append(f"Test #{i+1}: {json.dumps(test)}")
        tests_formatted = "\n".join(numbered_tests)

        user_prompt = (
            f"Task Details:\n"
            f"- URL: {task.url}\n"
            f"- Domain: {current_domain}\n"
            f"- Prompt: {task.prompt}\n"
            f"- Success Criteria: {task.success_criteria}\n\n"
            f"HTML Context (truncated):\n{truncated_html[:500]}...\n\n"
            f"Here are the proposed tests:\n"
            f"{tests_formatted}\n\n"
            f"Please review each test and respond with ONLY the numbers of tests to keep.\n"
            f"Format your response as: KEEP: 1, 3, 4"
        )

        # 2) Ask LLM for filtering - using the imported FILTER_PROMPT instead of inline prompt
        try:
            filter_response = await self.llm_service.async_predict(
                messages=[
                    {"role": "system", "content": FILTER_PROMPT + TEST_CONTEXT_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                json_format=False  # We're not expecting JSON now
            )
            logger.debug(f"Filter step raw response: {filter_response}")

            # Parse the filter response to extract the test numbers to keep
            try:
                # Extract numbers from "KEEP: 1, 2, 5" format
                keep_pattern = re.compile(r"KEEP:\s*([\d,\s]+)")
                match = keep_pattern.search(filter_response)
                if match:
                    # Get the comma-separated list of numbers
                    numbers_str = match.group(1)
                    # Parse numbers, accounting for potential whitespace
                    keep_indices = [int(n.strip()) - 1 for n in numbers_str.split(',') if n.strip()]
                    # Create the list of tests to keep
                    valid_tests = [filtered_duplicates[i] for i in keep_indices if 0 <= i < len(filtered_duplicates)]
                    logger.info(f"Filtered from {len(filtered_duplicates)} to {len(valid_tests)} tests")
                    if not valid_tests and filtered_duplicates:
                        logger.warning("LLM filtering returned no valid tests; using duplicates-filtered set.")
                        return filtered_duplicates
                    return valid_tests
                else:
                    logger.warning("Could not parse keep indices from LLM response.")
                    return filtered_duplicates
            except Exception as e:
                logger.error(f"Error parsing LLM response for test indices: {e}")
                return filtered_duplicates
        except Exception as e:
            logger.error(f"LLM call for test filtering failed: {e}")
            return filtered_duplicates

    @staticmethod
    def _create_test_signature(test_config: Dict[str, Any]) -> str:
        """
        Create a unique signature for a test config to identify duplicates.
        """
        test_type = test_config.get("test_type", "unknown")

        if test_type == "FindInHtmlTest":
            keywords = test_config.get("keywords", [])
            return f"{test_type}:{','.join(sorted(keywords))}"
        elif test_type == "CheckUrlTest":
            url = test_config.get("url", "")
            return f"{test_type}:{url}"
        elif test_type == "CheckEventEmittedTest":
            event_name = test_config.get("event_name", "")
            return f"{test_type}:{event_name}"
        elif test_type == "CheckPageViewEventTest":
            page_view_url = test_config.get("page_view_url", "")
            return f"{test_type}:{page_view_url}"
        elif test_type in ["JudgeBaseOnHTML", "JudgeBaseOnScreenshot", "OpinionBaseOnScreenshot"]:
            description = test_config.get("description", "")
            # Use first 50 chars of description as part of signature
            desc_signature = description[:50].lower().replace(" ", "")
            return f"{test_type}:{desc_signature}"

        # Fallback for unknown test types
        return f"{test_type}:{hash(json.dumps(test_config, sort_keys=True))}"

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from a full URL."""
        if not url:
            return ""
        pattern = re.compile(r"https?://([^/]+)")
        match = pattern.match(url)
        return match.group(1).lower() if match else ""
