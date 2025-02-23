# file: test_generation_pipeline.py
import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from pydantic import ValidationError

# Depending on your project structure, adjust these imports:
from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.shared.utils import get_html_and_screenshot, detect_interactive_elements
from dependency_injector.wiring import Provide
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.shared.utils import extract_json_in_markdown
from autoppia_iwa.src.data_generation.application.tests.logic_function_generator import (
    TestLogicGenerator)


################################################################################
# PART 2: PROMPTS
################################################################################
# Test Context and Generation System Prompts
TEST_CONTEXT_PROMPT = """
Context:
You are responsible for generating, refining, and validating **multi-step, single-page user tasks** for a website through a structured process. This process is inspired by advanced autonomous evaluation frameworks like Infinite Web Arena (IWA) and consists of the following phases:

1. Draft Generation
   - **What:** Create initial task drafts using generative AI techniques to simulate realistic user interactions (e.g., navigation, search, filtering, and transactions) on a single-page interface.
   - **Why:** To generate a **diverse set of scenarios** that challenge web agents by mimicking dynamic, real-world website behaviors.
   - **How:** Leverage meta-programming and LLMs to produce a broad range of tasks covering both common and edge-case interactions.

2. Feasibility & Success Criteria Filtering
   - **What:** Evaluate each task draft against predefined feasibility metrics and success criteria.
   - **Why:** To ensure every task is **executable within a real browser environment** and that success can be objectively measured through both frontend (DOM analysis, network monitoring, visual verification) and backend (event tracking, state validation) tests.
   - **How:** Automatically filter out tasks that do not meet the criteria, refining the list to include only those with clear, testable outcomes.

3. Concept and Off-Topic Filtering
   - **What:** Review the refined tasks for conceptual coherence and alignment with the website's objectives.
   - **Why:** To eliminate tasks that are off-topic or that fail to contribute meaningfully to evaluating user-agent interactions, ensuring the focus remains on **realistic and valuable** web scenarios.
   - **How:** Apply logical checks and thematic filtering to validate that each task contributes to a **robust, scalable evaluation** framework, similar to how IWA continuously introduces novel challenges to prevent overfitting and memorization.

Overall, your role is to create **high-quality, executable tasks** that:
- Reflect the complexities of modern web environments.
- Are grounded in both synthetic generation and logical validation.
- Provide clear, measurable outcomes for autonomous testing.

Remember, tasks must be broken down into multiple steps when needed. This ensures that each step of a multi-step task can be tested properly.
"""

TEST_GENERATION_SYSTEM_PROMPT = """
You are a TEST-generation expert, essential for our web agents benchmark.
Below is our **planned workflow** for validating whether a web agent (the automated solver) truly completes each **multi-step** task:

1) **Generate tasks**  
2) **Send tasks to the agent**  
3) The agent returns a List[Action] as a response (these Actions are the steps it will take).  
4) We execute them on a fresh browser instance at the URL of the task.  
5) After each action, we capture a **BrowserSnapshot** (which includes current HTML, screenshot, and recorded backend events).  
6) We run a set of **tests** over each snapshot. If there are N actions, we get N snapshots. The tests produce pass/fail results (booleans).

Finally, we apply a logic function **F** on these results to decide if the agent truly completed the task.

---
### What We Need from You
We want you to **generate 1 or 2 minimal tests** that together confirm the *exact* success criteria of the user instruction. If the success criteria reference a backend event (e.g., "User purchased X product"), we typically add a `CheckEventEmittedTest`. If it's purely front-end (e.g., "user sees a message in the UI"), we might only need a `FindInHtmlTest` or an `OpinionBaseOnHTML`.

**Important**:  
- Multi-step tasks may have different success criteria at each step (e.g., "First fill the form, then click 'Submit', then confirm the success message appears").  
- Even if **one** test can partially confirm the previous step, we may still need additional tests for subsequent steps.  
- Keep tests minimal and specific to the *stated success criteria*, so we avoid confusion or overlapping checks.

---
### Additional Note on Post-Generation Filtering
After your generation, we will **automatically** remove:
- Redundant tests (multiple tests that verify the exact same condition).
- Tests that reference an HTML snippet we do not have (e.g., for a redirect to a different domain).
- `FindInHtmlTest` with keywords that appear to be pure guesses and do **not** actually appear in the provided HTML snippet.

So please **only** propose each test if it is truly needed and if the HTML snippet or success criteria explicitly support it.

---
### Available Test Classes
We have these classes available to validate success. Each test can examine either the **frontend** or the **backend** side:

1. **FindInHtmlTest**  
   - `test_type = "frontend"`  
   - Fields:  
     ```json
     {
       "keywords": [...],
       "description": "..."
     }
     ```
   - Passes if **at least one** of the given keywords is found in the HTML.

2. **CheckEventEmittedTest**  
   - `test_type = "backend"`  
   - Fields:  
     ```json
     {
       "event_name": "...",
       "description": "..."
     }
     ```
   - Passes if an event with `event_name` was captured in backend logs.

3. **CheckPageViewEventTest**  
   - `test_type = "backend"`  
   - Fields:  
     ```json
     {
       "page_view_url": "...",
       "description": "..."
     }
     ```
   - Passes if a page view event with the given URL was captured.

4. **OpinionBaseOnHTML**  
   - `test_type = "frontend"`  
   - Fields:  
     ```json
     {
       "name": "OpinionBaseOnHTML",
       "description": "..."
     }
     ```
   - Runs an LLM-based analysis comparing previous HTML to the current HTML to decide if the step was successful.

5. **OpinionBaseOnScreenshot**  
   - `test_type = "frontend"`  
   - Fields:  
     ```json
     {
       "name": "OpinionBaseOnScreenshot",
       "task": "...",
       "description": "..."
     }
     ```
   - Runs an LLM-based analysis on screenshots before/after the action to determine if the step was successful.

---
### Output Requirements
When you generate tests, **return a strictly valid JSON array** with no extra keys. Each item in the array must match one of the classes above. For example:
```json
[
  {
    "test_type": "frontend",
    "keywords": ["Welcome to the Home page"],
    "description": "Check for homepage content"
  }
]
```
"""

FINAL_LOGIC_SYSTEM_PROMPT = """
You are an expert at composing minimal logic expressions over a pass/fail matrix x(i,j).

- We have N actions (i = 1..N).
- We have M tests (j = 1..M).
- x(i,j) is True if test j passes after action i, else False.

We want a minimal expression that, when evaluated, determines if the Task was completed successfully.

Use these notations:
- T1_i means "test #1 passes at action i"
- T2_i means "test #2 passes at action i"
- You can combine them with AND / OR
- For existential: "∃ i in [1..N]: T1_i AND T2_i" or something similar

Return valid JSON: 
```json
{"logic": "some expression here"}
```

Example formula patterns:
  "∃ i in [1..N]: T1_i AND T2_i"
  "T1_N AND T2_N"
  "∃ i in [1..N]: (T1_i OR T2_i)"
  "T1_1"
"""

################################################################################
# PART 3: Normalizing LLM's output
################################################################################


def normalize_test_config(test_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts LLM-produced test_config like:
      {"test_type": "FindInHtmlTest", "fields": {"keywords": [...], "description": "..."}}
    into the standard shape your pipeline expects:
      {"test_type": "frontend", "keywords": [...], "description": "..."}
    """
    raw_test_type = test_config.get("test_type")

    # If there's a "fields" dict, flatten it
    if "fields" in test_config and isinstance(test_config["fields"], dict):
        fields = test_config.pop("fields")
        test_config.update(fields)

    # Normalize test types
    test_type_mapping = {
        "FindInHtmlTest": "frontend",
        "CheckEventEmittedTest": "backend",
        "CheckPageViewEventTest": "backend",
        "OpinionBaseOnHTML": "frontend",
        "OpinionBaseOnScreenshot": "frontend"
    }

    if raw_test_type in test_type_mapping:
        test_config["test_type"] = test_type_mapping[raw_test_type]

        # Add name field for opinion-based tests
        if raw_test_type in ["OpinionBaseOnHTML", "OpinionBaseOnScreenshot"]:
            test_config["name"] = raw_test_type

    return test_config

################################################################################
# PART 4: TestGenerationPipeline
################################################################################


class TestGenerationPipeline:
    """
    A pipeline that, for each Task, uses an LLM to:
      1) Propose 1–2 minimal test definitions referencing the relevant test classes.
      2) Propose a final Boolean expression referencing x(i,j) for overall success.
      3) Filter out guess-based or redundant tests.
    """

    def __init__(
        self,
        llm_service: ILLMService = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500
    ):
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars

    async def add_tests_to_tasks(
        self,
        tasks: List[Task],
        domain_analysis: Optional[DomainAnalysis] = None,
        project_context: Optional[Dict[str, Any]] = None,
    ) -> List[Task]:
        """
        Given a list of tasks, generate a minimal set of tests for each task
        that confirm the user completed the scenario described in the prompt
        (according to the success criteria). Then filter out guess-based or 
        redundant tests, and finally propose a logic expression.
        """
        for task in tasks:
            try:
                # Get page analysis or fetch HTML directly
                page_analysis = None
                if domain_analysis and domain_analysis.page_analyses:
                    page_analysis = next(
                        (p for p in domain_analysis.page_analyses if p.page_url == task.url),
                        None
                    )

                if page_analysis:
                    truncated_html = page_analysis.clean_html[:self.truncate_html_chars]
                    screenshot_desc = page_analysis.screenshot_description or ""
                    interactive_summary = detect_interactive_elements(page_analysis.clean_html)
                else:
                    fetched_html, fetched_screenshot_desc = await get_html_and_screenshot(task.url)
                    truncated_html = fetched_html[:self.truncate_html_chars]
                    screenshot_desc = fetched_screenshot_desc
                    interactive_summary = detect_interactive_elements(fetched_html)

                # Prepare context data
                context_data = project_context or {}
                context_json = json.dumps(context_data, indent=2)

                # Generate tests
                generation_user_content = (
                    f"Task Prompt: {task.prompt}\n\n"
                    f"Success Criteria: {task.success_criteria or 'N/A'}\n\n"
                    f"HTML snippet:\n{truncated_html}\n\n"
                    f"Screenshot summary:\n{screenshot_desc}\n\n"
                    f"Interactive elements:\n{json.dumps(interactive_summary, indent=2)}\n\n"
                    f"Project context:\n{context_json}\n\n"
                    "Return strictly valid JSON array of minimal test definitions."
                )

                test_generation_response = await self._call_llm(
                    TEST_GENERATION_SYSTEM_PROMPT,
                    generation_user_content
                )

                # Parse and process tests
                raw_json = extract_json_in_markdown(test_generation_response)
                proposed_tests = self._parse_test_definitions(raw_json)
                filtered_tests = await self._filter_generated_tests(proposed_tests, truncated_html, task)
                test_objects = BaseTaskTest.assign_tests(filtered_tests)
                task.tests.extend(test_objects)

                task.logic_function = await TestLogicGenerator().generate_logic(task=task, tests=test_objects)

            except Exception as e:
                raise e
                logger.error(f"Failed to generate tests/logic for task {task.id}: {e}")

        return tasks

    async def _call_llm(self, system_prompt: str, user_content: str) -> str:
        """Make an async call to the LLM service."""
        message_payload = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        response = await self.llm_service.async_make_request(
            message_payload=message_payload,
            chat_completion_kwargs={"temperature": 0.7, "max_tokens": 1200}
        )
        return response

    def _parse_test_definitions(self, text: str) -> List[Dict[str, Any]]:
        """Parse and normalize test definitions from LLM response."""
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [normalize_test_config(item) for item in parsed]
        except (ValueError, TypeError, ValidationError) as e:
            logger.warning(f"Error parsing test definitions: {e}")
        return []

    async def _filter_generated_tests(
        self,
        proposed_tests: List[Dict[str, Any]],
        truncated_html: str,
        task: Task
    ) -> List[Dict[str, Any]]:
        """
        Uses LLM to filter out:
        1) Duplicate tests (identical signatures)
        2) Guess-based frontend tests whose keywords don't match the HTML
        3) Tests referencing a different domain
        4) Frontend tests redundant with backend tests
        5) Tests that don't align with task objectives or success criteria
        """
        if not proposed_tests:
            return []

        # First do basic duplicate removal using signatures
        filtered_duplicates = []
        seen_signatures = set()
        for test_config in proposed_tests:
            signature = self._create_test_signature(test_config)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                filtered_duplicates.append(test_config)

        # Prepare context for LLM evaluation
        current_domain = self._extract_domain(task.url)
        tests_json = json.dumps(filtered_duplicates, indent=2)

        # Create the filter prompt without f-string for the example
        filter_prompt = f"""
                {TEST_CONTEXT_PROMPT}

                Given these proposed tests for task validation:
                {tests_json}

                Task Details:
                - URL: {task.url}
                - Domain: {current_domain}
                - Prompt: {task.prompt}
                - Success Criteria: {task.success_criteria}

                HTML Context (truncated):
                {truncated_html[:500]}...

                For each test, evaluate:
                1. Accuracy: For frontend tests, do the keywords actually appear in the HTML? If not, the test is invalid.
                2. Domain Relevance: For backend tests, do URLs/events match the current domain?
                3. Redundancy: Is this test redundant given other tests? (e.g., backend tests may supersede frontend tests)
                4. Success Criteria Alignment: Does this test genuinely validate the task's success criteria?

                Return a JSON array of the valid tests, removing any that fail these criteria. 
                Explain your filtering decisions in the "filtering_reason" field for each test.
                
                Example format:
                {{
                    "valid_tests": [],
                    "filtering_decisions": [
                        {{
                            "test": {{"test_type": "frontend", "keywords": ["example"]}},
                            "kept": false,
                            "reason": "Keywords not found in HTML"
                        }}
                    ]
                }}"""

        try:
            # Get LLM's filtering analysis
            filter_response = await self._call_llm(
                system_prompt="You are an expert at validating and filtering test cases for web automation. Be thorough but conservative in filtering - only remove tests if there's a clear reason.",
                user_content=filter_prompt
            )

            # Parse LLM response
            filter_result = json.loads(extract_json_in_markdown(filter_response))

            # Log filtering decisions for debugging
            for decision in filter_result.get("filtering_decisions", []):
                logger.debug(f"Test filtering decision: {decision}")

            # Return the filtered tests
            valid_tests = filter_result.get("valid_tests", [])

            # Fallback to original tests if LLM filtering fails
            if not valid_tests and filtered_duplicates:
                logger.warning("LLM filtering returned no valid tests, using duplicate-filtered set")
                return filtered_duplicates

            return valid_tests

        except Exception as e:
            logger.error(f"Error during LLM test filtering: {e}")
            # Fallback to duplicate-filtered tests on error
            return filtered_duplicates

    def _create_test_signature(self, test_config: Dict[str, Any]) -> str:
        """Create a unique signature for a test configuration."""
        parts = [test_config.get("test_type", "")]

        if "keywords" in test_config:
            parts.append(",".join(sorted(test_config["keywords"])))
        if "event_name" in test_config:
            parts.append(test_config["event_name"])
        if "page_view_url" in test_config:
            parts.append(test_config["page_view_url"])

        return "|".join(parts)

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ""

        pattern = re.compile(r"https?://([^/]+)")
        match = pattern.match(url)
        return match.group(1).lower() if match else ""

    def _parse_logic_expression(self, text: str) -> Optional[str]:
        """Parse the logic expression from LLM response."""
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "logic" in data:
                return data["logic"]
        except (ValueError, TypeError, ValidationError) as e:
            logger.warning(f"Error parsing logic expression: {e}")
        return "T1"
