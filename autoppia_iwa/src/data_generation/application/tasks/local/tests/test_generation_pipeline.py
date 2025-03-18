import json
import re
import time
from typing import Any

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckUrlTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer

# LLM & domain imports
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements

from .prompts import TEST_GENERATION_PROMPT


class LocalTestGenerationPipeline:
    """A pipeline that:
    1) Gathers context (HTML, screenshot info, etc.) for each Task.
    2) Uses LLM to generate appropriate tests in a single call.
    3) Instantiates the test objects and adds them to the task.
    4) (Optionally) generates a logic function for the entire set of tests."""

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

        # Real webs dont have backend tests
        if web_project.is_web_real:
            self.test_class_map = {
                # "CheckUrlTest": CheckUrlTest,
                # "FindInHtmlTest": FindInHtmlTest,
                "JudgeBaseOnHTML": JudgeBaseOnHTML,
                "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
            }
        else:
            self.test_class_map = {
                "CheckUrlTest": CheckUrlTest,
                "CheckEventTest": CheckEventTest,
                "FindInHtmlTest": FindInHtmlTest,
                # "JudgeBaseOnHTML": JudgeBaseOnHTML,
                # "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot
            }

        # Map for extra data needed for specific test classes
        self.test_class_extra_data = {
            "CheckUrlTest": "Use this CheckUrlTest test for changes in the url. Very useful to check navigation or where the agent is.",
            "FindInHtmlTest": "Use this FindInHtmlTest test to check for strings that you expect to appear after the task is completed. very useful for tasks that trigger UI updates",
            "CheckEventTest": "For CheckEventTest pls select event_name from this List of allowed event names: " + json.dumps([event.__name__ for event in web_project.events]),
            "JudgeBaseOnHTML": "Use this JudgeBaseOnHTML test to evaluate whether a task was successfully completed based on HTML changes before and after a list actions. Best for verifying interactions that modify page structure.",
            "JudgeBaseOnScreenshot": "Use this JudgeBaseOnScreenshot test to evaluate whether a task was successfully completed based on screenshot comparisons. Best for visual verification tasks where UI changes occur but HTML modifications might be minimal.",
        }

    async def add_tests_to_tasks(self, tasks: list[Task]) -> list[Task]:
        """
        Main pipeline function that adds appropriate tests to each task
        """
        for task in tasks:
            try:
                # STEP 1: Generate tests using LLM (single call for all test classes)
                all_tests = await self._generate_tests(task)
                if not all_tests:
                    logger.warning(f"No tests generated for task {task.id}")
                    continue

                # STEP 2: Instantiate and add the test objects to the task
                await self._instantiate_tests(task, all_tests)

                # STEP 3: Optionally generate a logic function that references these tests
                if task.tests:
                    pass
                    # task.logic_function = await self.logic_generator.generate_logic(
                    #     task=task,
                    #     tests=task.tests
                    # )
                    # logger.info(f"Generated logic function for task {task.id}")
            except Exception as e:
                logger.error(f"Failed to generate tests for task={task.id}: {e!s}")
                logger.debug(f"Exception details: {type(e).__name__}, {e!r}")
                raise e

        return tasks

    async def _generate_tests(self, task: Task) -> list[dict[str, Any]]:
        """
        Generate test definitions for all test classes in a single LLM call
        with retry logic for handling JSON parsing errors
        """
        # Gather contextual data needed for the prompt
        cleaned_html = task.clean_html[: self.truncate_html_chars] if task.clean_html else ""
        screenshot_desc = task.screenshot_description or ""
        interactive_elements = detect_interactive_elements(cleaned_html)
        # domain_analysis = self.web_project.domain_analysis

        # Prepare schemas for all test classes
        test_class_schemas = {}
        for test_class_name, test_class in self.test_class_map.items():
            try:
                if hasattr(test_class, "model_json_schema"):
                    test_class_schemas[test_class_name] = json.dumps(test_class.model_json_schema(), indent=2)
                elif hasattr(test_class, "schema"):
                    test_class_schemas[test_class_name] = json.dumps(test_class.schema(), indent=2)
                else:
                    # Create a basic schema for non-pydantic classes
                    test_class_schemas[test_class_name] = json.dumps(
                        {"title": test_class_name, "type": "object", "properties": {"type": {"type": "string", "enum": [test_class_name]}, "description": {"type": "string"}}, "required": ["type"]},
                        indent=2,
                    )
            except Exception as e:
                logger.warning(f"Could not get schema for {test_class_name}: {e}")
                # Create a basic schema
                test_class_schemas[test_class_name] = json.dumps(
                    {"title": test_class_name, "type": "object", "properties": {"type": {"type": "string", "enum": [test_class_name]}, "description": {"type": "string"}}, "required": ["type"]},
                    indent=2,
                )

        # Build a unified prompt for all test classes
        system_prompt = TEST_GENERATION_PROMPT.format(
            task_prompt=task.prompt,
            success_criteria=task.success_criteria or "N/A",
            current_url=task.url,
            truncated_html=cleaned_html,
            screenshot_desc=screenshot_desc,
            interactive_elements=json.dumps(interactive_elements, indent=2),
            events=self.web_project.events,
            test_classes_info="\n\n".join([f"### {test_class_name}\n{schema}\n{self.test_class_extra_data.get(test_class_name, '')}" for test_class_name, schema in test_class_schemas.items()]),
        )

        # Implement retry logic for LLM calls and JSON parsing
        retry_count = 0
        last_error = None
        last_response = None

        while retry_count < self.max_retries:
            try:
                # Call the LLM
                response = await self.llm_service.async_predict(
                    messages=[{"role": "system", "content": system_prompt}],
                    json_format=True,
                )

                last_response = response
                # Parse the response
                all_tests = self._parse_llm_response(response)
                if all_tests:
                    logger.info(f"Successfully generated {len(all_tests)} tests for task {task.id} on attempt {retry_count + 1}")
                    return all_tests

                # If we got an empty list but no exception, we should retry with a modified prompt
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.warning(f"Got empty test list on attempt {retry_count}, retrying...")
                    # Add an emphasis on proper JSON format in the retry
                    system_prompt += "\n\nIMPORTANT: Return ONLY a valid JSON array of test objects. Each test must have a 'type' field matching one of the provided test classes."
                    time.sleep(self.retry_delay)

            except Exception as e:
                retry_count += 1
                last_error = e

                if retry_count < self.max_retries:
                    logger.warning(f"Attempt {retry_count} failed: {e!s}. Retrying in {self.retry_delay} seconds...")
                    # Add an emphasis on proper JSON format in the retry
                    system_prompt += "\n\nIMPORTANT: Return ONLY a valid JSON array of test objects. Each test must have a 'type' field matching one of the provided test classes."
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed. Last error: {e!s}")
                    logger.debug(f"Last response received: {last_response}")

        # All retries failed
        if last_error:
            logger.error(f"Failed to generate tests after {self.max_retries} attempts: {last_error!s}")
            logger.debug(f"Exception details: {type(last_error).__name__}, {last_error!r}")
        else:
            logger.error(f"Failed to generate valid tests after {self.max_retries} attempts")

        return []

    def _parse_llm_response(self, response: Any) -> list[dict[str, Any]]:
        """
        Parse and validate the LLM response, extracting valid test definitions
        """
        all_tests = []
        response_data = None

        # If the response is already a list, use it directly
        if isinstance(response, list):
            response_data = response
        # If it's a string, try to parse it as JSON
        elif isinstance(response, str):
            try:
                # First, try parsing the raw response
                response_data = json.loads(response.strip())
            except json.JSONDecodeError:
                # If that fails, try to extract a JSON array using regex
                json_array_pattern = r"\[\s*{.*}\s*\]"
                matches = re.search(json_array_pattern, response, re.DOTALL)

                if matches:
                    try:
                        potential_json = matches.group(0)
                        response_data = json.loads(potential_json)
                    except json.JSONDecodeError:
                        # If regex extraction fails, try manual search for array brackets
                        start_idx = response.find("[")
                        end_idx = response.rfind("]")

                        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                            try:
                                json_str = response[start_idx : end_idx + 1]
                                response_data = json.loads(json_str)
                            except json.JSONDecodeError:
                                logger.error("Failed to extract JSON array after multiple attempts")
                                return []
                else:
                    logger.error("Could not find JSON array pattern in response")
                    return []
        # If it's a dict, it might be wrapped incorrectly
        elif isinstance(response, dict):
            # Check if there's a field that contains the array
            for _key, value in response.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    response_data = value
                    break

            if response_data is None:
                # Just use the dict itself if it has a 'type' field (single test case)
                if "type" in response and response["type"] in self.test_class_map:
                    return [response]
                logger.warning(f"Response is a dict but doesn't contain a test array: {response}")
                return []
        else:
            logger.warning(f"Unexpected response type: {type(response)}")
            return []

        # Ensure we have a list at this point
        if not isinstance(response_data, list):
            logger.warning(f"Expected a JSON array of tests, got: {type(response_data)}")
            return []

        # Validate each test
        for test in response_data:
            if isinstance(test, dict):
                test_type = test.get("type")
                if test_type in self.test_class_map:
                    all_tests.append(test)
                    logger.debug(f"Validated test of type {test_type}")
                else:
                    logger.warning(f"Test has invalid type: {test_type}")
            else:
                logger.warning(f"Test is not a dictionary: {test}")

        return all_tests

    async def _instantiate_tests(self, task: Task, valid_tests: list[dict[str, Any]]) -> None:
        """
        Instantiate test objects and add them to the task
        """
        for test_def in valid_tests:
            try:
                # Create a copy of the test definition to avoid modifying the original
                test_def_copy = test_def.copy()

                # Extract test type
                test_type = test_def_copy.get("type")
                if not test_type:
                    logger.warning(f"Test definition missing type: {test_def}")
                    continue

                # Get corresponding test class
                test_class = self.test_class_map.get(test_type)
                if not test_class:
                    logger.warning(f"Unknown test type: {test_type}")
                    continue

                # Instantiate the test object
                test_instance = test_class(**test_def_copy)
                task.tests.append(test_instance)
                logger.info(f"Added {test_type} to task {task.id}")
            except Exception as e:
                logger.error(f"Failed to instantiate test {test_def}: {e!s}")
                logger.debug(f"Exception details: {type(e).__name__}, {e!r}")
