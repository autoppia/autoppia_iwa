import json
import time
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM

from .prompts import CHECK_EVENT_TEST_GENERATION_SYSTEM_PROMPT, CHECK_EVENT_TEST_GENERATION_USER_PROMPT
from .utils import clean_examples


class GlobalTestGenerationPipeline:
    """
    Simplified pipeline that:
      - Iterates over tasks with a defined UseCase
      - Generates only CheckEventTest from the LLM
      - Attaches them to the task
    """

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        truncate_html_chars: int = 1500,
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.truncate_html_chars = truncate_html_chars

    async def add_tests_to_tasks(self, tasks: list[Task]) -> list[Task]:
        """
        Main function. For each task that has a use_case, generate CheckEventTest objects via LLM.
        """
        for task in tasks:
            if not task.use_case:
                logger.debug(f"Task {task.id} has no UseCase. Skipping global test generation.")
                continue

            if task.use_case.constraints_generator is False:
                logger.debug(f"Skipping task {task.id}: UseCase has no constraints.")
                only_name_event = {"event_name": task.use_case.name}
                task.tests = [CheckEventTest(**only_name_event)]
                continue

            try:
                # Generate test definitions
                test_definitions = await self._generate_check_event_tests(task)
                if not test_definitions:
                    logger.warning(f"No tests generated for Task {task.id} (UseCase={task.use_case.name}).")
                    continue

                # Instantiate and add tests to task
                self._instantiate_tests(task, test_definitions)

            except Exception as e:
                logger.error(f"Failed to generate tests for Task={task.id}: {e!s}")
                logger.debug(f"Exception details: {type(e).__name__}, {e!r}")
                raise e

        return tasks

    async def _generate_check_event_tests(self, task: Task) -> list[dict[str, Any]]:
        """
        Build the LLM prompt and parse the response as a list of CheckEventTest definitions.
        """
        # 1) Extract relevant info
        use_case: UseCase = task.use_case
        truncated_html = task.clean_html[: self.truncate_html_chars] if task.clean_html else ""
        screenshot_desc = task.screenshot_description or ""
        interactive_elements = task.interactive_elements or "[]"

        # Convert test_examples to a JSON string for the prompt
        cleaned_examples = clean_examples(use_case.examples)
        examples = json.dumps(cleaned_examples, indent=2)
        # 2) Prepare the LLM prompt
        user_input_prompt = CHECK_EVENT_TEST_GENERATION_USER_PROMPT.format(
            use_case_name=use_case.name,
            use_case_description=use_case.description,
            task_prompt=task.prompt,
            examples=examples,
            event_source_code=use_case.event_source_code,
            truncated_html=truncated_html,
            screenshot_desc=screenshot_desc,
            interactive_elements=str(interactive_elements),
        )

        # 3) Call the LLM with retries
        for attempt in range(self.max_retries):
            try:
                response = await self.llm_service.async_predict(
                    messages=[{"role": "system", "content": CHECK_EVENT_TEST_GENERATION_SYSTEM_PROMPT}, {"role": "user", "content": user_input_prompt}],
                    json_format=True,
                )
                # 4) Parse the JSON array of test defs
                test_dicts = self._parse_llm_response(response)
                if test_dicts:
                    logger.info(f"Generated {len(test_dicts)} CheckEventTest(s) for task {task.id} on attempt {attempt + 1}.")
                    return test_dicts

                logger.warning(f"Attempt {attempt + 1}: Received empty or invalid test list for Task {task.id}. Retrying...")
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for Task {task.id}: {e!s}. Retrying...")
                time.sleep(self.retry_delay)

        # If we reach here, all attempts failed
        logger.error(f"All {self.max_retries} attempts to generate tests for Task {task.id} have failed.")
        return []

    def _parse_llm_response(self, response: Any) -> list[dict[str, Any]]:
        """
        Parse the LLM response as a JSON array of "CheckEventTest" definitions and
        restructure the event_criteria if it has nested 'value' keys.
        Return a list of dictionaries if successful, otherwise an empty list.
        """
        test_list = []

        if isinstance(response, list):
            test_list = response
        elif isinstance(response, dict):
            if response.get("type") == "CheckEventTest":
                test_list = [response]
            elif "tests" in response and isinstance(response["tests"], list):
                test_list = response["tests"]
        elif isinstance(response, str):
            try:
                data = json.loads(response.strip())
                if isinstance(data, list):
                    test_list = data
                elif isinstance(data, dict) and data.get("type") == "CheckEventTest":
                    test_list = [data]
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response as JSON.")

        validated_tests = []
        for test_item in test_list:
            if not isinstance(test_item, dict) or test_item.get("type") != "CheckEventTest":
                continue

            event_criteria = test_item.get("event_criteria")
            if isinstance(event_criteria, dict):
                restructured_criteria = {}
                for key, value in event_criteria.items():
                    if isinstance(value, dict) and "value" in value and isinstance(value["value"], dict) and "operator" in value["value"] and "value" in value["value"]:
                        # Found the nested structure, restructure it
                        restructured_criteria[key] = {
                            "operator": value["value"].get("operator"),
                            "value": value["value"].get("value"),
                        }
                    elif isinstance(value, dict) and "operator" in value and "value" in value:
                        # Already in the correct format
                        restructured_criteria[key] = value
                    elif isinstance(value, dict) and "value" in value and not isinstance(value["value"], dict) and "operator" in value:
                        # Handle cases where 'value' directly contains the value and 'operator' is at the same level
                        restructured_criteria[key] = {"operator": value.get("operator"), "value": value.get("value")}
                    else:
                        restructured_criteria[key] = value  # Keep as is if not the expected nested structure
                test_item["event_criteria"] = restructured_criteria
            validated_tests.append(test_item)

        return self._validate_test_list(validated_tests)

    def _validate_test_list(self, test_list: list[Any]) -> list[dict[str, Any]]:
        """
        Ensure each item is a dict with "type" == "CheckEventTest" after potential restructuring.
        """
        valid_tests = []
        for test_item in test_list:
            if isinstance(test_item, dict) and test_item.get("type") == "CheckEventTest":
                valid_tests.append(test_item)
        return valid_tests

    def _instantiate_tests(self, task: Task, test_definitions: list[dict[str, Any]]) -> None:
        """
        Create CheckEventTest objects from the validated definitions and add them to the Task.
        """
        for test_def in test_definitions:
            try:
                # For Pydantic-based class:
                check_event_test = CheckEventTest(**test_def)
                task.tests.append(check_event_test)
                logger.debug(f"Added CheckEventTest to Task {task.id}: {check_event_test.event_name}")
            except Exception as e:
                logger.error(f"Failed to instantiate CheckEventTest for Task {task.id}: {e!s}")
