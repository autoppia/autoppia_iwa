import json
import re
from typing import List, Dict, Any
from loguru import logger
from pydantic import ValidationError
from dependency_injector.wiring import Provide
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.tests.prompts import (
    TEST_CONTEXT_PROMPT,
    FILTER_PROMPT
)
from autoppia_iwa.src.data_generation.application.tests.schemas import FilterResponse
from .utils import normalize_test_config


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

    async def _filter_generated_tests(
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

        Returns the "valid_tests" from the final LLM response.
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

        # Build a user prompt for the LLM-based filter
        current_domain = self._extract_domain(task.url)
        tests_json = json.dumps(filtered_duplicates, indent=2)

        user_prompt = (
            f"Given these proposed tests for task validation:\n"
            f"{tests_json}\n\n"
            f"Task Details:\n"
            f"- URL: {task.url}\n"
            f"- Domain: {current_domain}\n"
            f"- Prompt: {task.prompt}\n"
            f"- Success Criteria: {task.success_criteria}\n\n"
            f"HTML Context (truncated):\n{truncated_html[:500]}...\n\n"
            f"Return JSON with 'filtering_decisions' and 'valid_tests'."
        )

        # 2) Ask LLM for filtering
        try:
            filter_response_text = await self.llm_service.async_predict(
                messages=[
                    {"role": "system", "content": FILTER_PROMPT + TEST_CONTEXT_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                json_format=True,
                schema=FilterResponse.model_json_schema()  # {filtering_decisions: [...], valid_tests: [...]}
            )
            logger.debug(f"Filter step raw response: {filter_response_text}")

            # Parse the filter response
            try:
                filter_result = FilterResponse.parse_raw(filter_response_text)
                # Optional: log the decisions
                for decision in filter_result.filtering_decisions:
                    logger.debug(f"Filtering decision: {decision}")

                # Flatten & normalize each valid test
                valid_tests = []
                for vt in filter_result.valid_tests:
                    t_dict = vt.dict()
                    t_dict = normalize_test_config(t_dict)
                    valid_tests.append(t_dict)

                if not valid_tests and filtered_duplicates:
                    logger.warning("LLM filtering returned no valid tests; using duplicates-filtered set.")
                    return filtered_duplicates

                return valid_tests

            except ValidationError as e:
                logger.error(f"Error parsing FilterResponse from LLM: {e}")
                # Fallback to just the duplicates-filtered set
                return filtered_duplicates

        except Exception as e:
            logger.error(f"LLM call for test filtering failed: {e}")
            return filtered_duplicates

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from a full URL."""
        if not url:
            return ""
        pattern = re.compile(r"https?://([^/]+)")
        match = pattern.match(url)
        return match.group(1).lower() if match else ""
