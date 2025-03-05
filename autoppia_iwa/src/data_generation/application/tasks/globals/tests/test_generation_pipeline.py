import json
import re
import time
from typing import Any, Dict, List, Optional

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements

# Import your new prompt
from .prompts import USE_CASE_TEST_GENERATION_PROMPT


class GlobalTestGenerationPipeline:
    """A pipeline that:
    1) Iterates over global tasks that have a reference to a UseCase.
    2) Uses the LLM to generate test definitions specific to that UseCase.
    3) Instantiates and attaches test objects to each Task.
    """

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Map of test_class "type" strings to actual classes
        self.test_class_map = {
            "CheckEventTest": CheckEventTest,
            "CheckUrlTest": CheckUrlTest,
            "FindInHtmlTest": FindInHtmlTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
        }

    async def add_tests_to_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Main function that adds appropriate tests to each task.
        Only tasks which reference a recognized UseCase will get tests.
        """
        for task in tasks:
            try:
                # 1) Identify the use case from the task
                if not hasattr(task, "use_case_name") or not task.use_case_name:
                    logger.warning(f"Task {task.id} has no 'use_case_name', skipping test generation.")
                    continue

                use_case = self._find_use_case_by_name(task.use_case_name)
                if not use_case:
                    logger.warning(f"Could not find UseCase '{task.use_case_name}' for task {task.id}, skipping.")
                    continue

                # 2) Generate tests using LLM
                generated_test_defs = await self._generate_tests_for_use_case(task, use_case)
                if not generated_test_defs:
                    logger.warning(f"No tests generated for task {task.id} / useCase '{use_case.name}'.")
                    continue

                # 3) Instantiate and add the test objects to the task
                self._instantiate_tests(task, generated_test_defs)

            except Exception as e:
                logger.error(f"Failed to generate tests for task={task.id}: {str(e)}")
                logger.debug(f"Exception details: {type(e).__name__}, {repr(e)}")
                # Optionally continue or re-raise
                # raise e

        return tasks

    def _find_use_case_by_name(self, use_case_name: str) -> Optional[UseCase]:
        """
        Look up a UseCase in web_project.use_cases by matching the name field.
        Adjust as needed if you store them differently.
        """
        if not self.web_project.use_cases:
            return None
        for uc in self.web_project.use_cases:
            if uc.name.lower() == use_case_name.lower():
                return uc
        return None

    async def _generate_tests_for_use_case(self, task: Task, use_case: UseCase) -> List[Dict[str, Any]]:
        """
        Build the specialized prompt for the given Task & UseCase,
        call the LLM to produce test definitions, then parse the JSON.
        """
        # 1) Gather relevant context
        truncated_html = task.clean_html[: self.truncate_html_chars] if task.clean_html else ""
        screenshot_desc = task.screenshot_description or ""
        interactive_elements = detect_interactive_elements(truncated_html) or []
        event_code = ""
        if hasattr(use_case.event, "code") and callable(use_case.event.code):
            event_code = use_case.event.code()

        # Convert test_examples to a JSON string or bullet list
        # so the LLM sees typical examples for that use case
        use_case_test_examples_str = json.dumps(use_case.test_examples, indent=2)

        # 2) Format the LLM prompt
        llm_prompt = USE_CASE_TEST_GENERATION_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            task_prompt=task.prompt,
            use_case_test_examples=use_case_test_examples_str,
            event_code=event_code,
            html=truncated_html,
            screenshot_desc=screenshot_desc,
            interactive_elements=json.dumps(interactive_elements, indent=2),
        )

        # 3) Invoke LLM with retry
        for attempt in range(self.max_retries):
            try:
                response = await self.llm_service.async_predict(messages=[{"role": "system", "content": llm_prompt}], json_format=True)

                # 4) Parse the LLM response as JSON array
                test_defs = self._parse_llm_response(response)
                if test_defs:
                    logger.info(f"Successfully generated {len(test_defs)} tests for task {task.id} (useCase={use_case.name}) " f"on attempt {attempt + 1}.")
                    return test_defs

                # If empty or invalid, try again (with a small tweak to the prompt)
                logger.warning(f"Attempt {attempt + 1}: Got empty or invalid test list. Retrying...")
                time.sleep(self.retry_delay)

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(self.retry_delay)

        # If all retries failed
        logger.error(f"All {self.max_retries} attempts to generate tests for task {task.id} have failed.")
        return []

    def _parse_llm_response(self, response: Any) -> List[Dict[str, Any]]:
        """
        Parse the LLM response (which should be a JSON array of test objects).
        Return a list of test dicts if successful, otherwise [].
        """
        if isinstance(response, list):
            # If the LLM already returned a Python list, just validate test objects
            return self._validate_test_list(response)

        if isinstance(response, dict):
            # Possibly a single test or a dict containing the array
            if "type" in response:
                # It's likely a single test, wrap in list
                return self._validate_test_list([response])
            # Or search if there's a key containing the array
            for v in response.values():
                if isinstance(v, list):
                    return self._validate_test_list(v)
            return []

        if isinstance(response, str):
            # Try to parse as JSON
            try:
                data = json.loads(response.strip())
                if isinstance(data, list):
                    return self._validate_test_list(data)
                elif isinstance(data, dict):
                    # Single test or nested structure
                    if "type" in data:
                        return self._validate_test_list([data])
                    # or search sub-fields
                    for v in data.values():
                        if isinstance(v, list):
                            return self._validate_test_list(v)
            except json.JSONDecodeError:
                # Try regex extraction of JSON array
                match = re.search(r"\[\s*{.*}\s*\]", response, re.DOTALL)
                if match:
                    try:
                        array_str = match.group(0)
                        data = json.loads(array_str)
                        if isinstance(data, list):
                            return self._validate_test_list(data)
                    except json.JSONDecodeError:
                        pass
            return []

        logger.warning(f"Unexpected LLM response type: {type(response)}. Cannot parse tests.")
        return []

    def _validate_test_list(self, test_list: List[Any]) -> List[Dict[str, Any]]:
        """
        Ensure each item in `test_list` is a dict with a valid "type"
        recognized by `self.test_class_map`.
        """
        valid_tests = []
        for test_item in test_list:
            if not isinstance(test_item, dict):
                continue
            ttype = test_item.get("type")
            if ttype in self.test_class_map:
                valid_tests.append(test_item)
            else:
                logger.warning(f"Skipping unknown test type: {ttype}")
        return valid_tests

    def _instantiate_tests(self, task: Task, test_defs: List[Dict[str, Any]]) -> None:
        """
        Given raw test definitions (dicts with 'type' etc.), instantiate the
        corresponding test classes and append them to `task.tests`.
        """
        for test_def in test_defs:
            ttype = test_def.get("type")
            if not ttype:
                logger.warning(f"Test definition missing 'type': {test_def}")
                continue

            test_class = self.test_class_map.get(ttype)
            if not test_class:
                logger.warning(f"Unknown test type '{ttype}' encountered.")
                continue

            try:
                # Some of your test classes might be Pydantic-based,
                # so you can do something like: test_instance = test_class(**test_def)
                # If they're not, adapt accordingly.
                test_instance = test_class(**test_def)
                task.tests.append(test_instance)
                logger.debug(f"Appended test '{ttype}' to Task {task.id}.")
            except Exception as e:
                logger.error(f"Failed to instantiate test {ttype} for Task {task.id}: {str(e)}")
