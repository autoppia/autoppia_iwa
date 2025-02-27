import json
from typing import Any, Dict, List

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.application.tests.logic.logic_function_generator import TestLogicGenerator
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import CheckEventTest, CheckPageViewEventTest, CheckUrlTest, JudgeBaseOnHTML
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer

# LLM & domain imports
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements

from .prompts import TEST_FILTERING_PROMPT, TEST_GENERATION_PER_CLASS_SYSTEM_PROMPT


class TestGenerationPipeline:
    """A pipeline that:
    1) Gathers context (HTML, screenshot info, etc.) for each Task.
    2) Uses LLM to generate appropriate tests for each test class (one LLM request per class).
    3) Filters the generated tests (optional).
    4) Instantiates the test objects and adds them to the task.
    5) (Optionally) generates a logic function for the entire set of tests."""

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500,
    ):
        self.web_project = web_project
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars
        self.logic_generator = TestLogicGenerator()

        # Real webs dont have backend tests
        if web_project.is_web_real:
            self.test_class_map = {
                "CheckUrlTest": CheckUrlTest,
                # "FindInHtmlTest": FindInHtmlTest,
                # "JudgeBaseOnHTML": JudgeBaseOnHTML,
                # "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot
            }
        else:
            self.test_class_map = {
                "CheckUrlTest": CheckUrlTest,
                "CheckPageViewEventTest": CheckPageViewEventTest,
                # "FindInHtmlTest": FindInHtmlTest,
                # "CheckEventTest": CheckEventTest,
                # "JudgeBaseOnHTML": JudgeBaseOnHTML,
                # "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot
            }

        # Map for extra data needed for specific test classes
        self.test_class_extra_data = {
            "CheckEventTest": "For CheckEventTest pls select event_name from this List of allowed event names: " + json.dumps(web_project.events),
        }

    async def add_tests_to_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Main pipeline function that adds appropriate tests to each task
        """
        for task in tasks:
            try:
                # STEP 1: Generate raw tests using LLM (one call per test class)
                raw_tests = await self._generate_tests(task)
                if not raw_tests:
                    logger.warning(f"No tests generated for task {task.id}")
                    continue
                # STEP 2: Optionally filter tests
                valid_tests = await self._filter_tests(task, raw_tests)
                # STEP 3: Instantiate and add the test objects to the task
                await self._instantiate_tests(task, valid_tests)
                # STEP 4: Optionally generate a logic function that references these tests
                if task.tests:
                    task.logic_function = await self.logic_generator.generate_logic(task=task, tests=task.tests)
                    logger.info(f"Generated logic function for task {task.id}")
            except Exception as e:
                logger.error(f"Failed to generate tests for task={task.id}: {str(e)}")
                logger.debug(f"Exception details: {type(e).__name__}, {repr(e)}")
        return tasks

    async def _generate_tests(self, task: Task) -> List[Dict[str, Any]]:
        """
        Generate test definitions by checking each test class individually
        """
        all_tests = []
        # Gather contextual data needed for the prompt
        cleaned_html = task.clean_html[: self.truncate_html_chars] if task.clean_html else ""
        screenshot_desc = task.screenshot_description or ""
        interactive_elements = detect_interactive_elements(cleaned_html)
        domain_analysis = self.web_project.domain_analysis or {}

        # Get serializable domain analysis
        domain_analysis_dict = {}
        if hasattr(domain_analysis, 'dump_excluding_page_analyses'):
            domain_analysis_dict = domain_analysis.dump_excluding_page_analyses()

        for test_class_name, test_class in self.test_class_map.items():
            try:
                # Handle schema safely
                schema_json = "{}"
                try:
                    if hasattr(test_class, 'model_json_schema'):
                        schema_json = json.dumps(test_class.model_json_schema(), indent=2)
                    elif hasattr(test_class, 'schema'):
                        schema_json = json.dumps(test_class.schema(), indent=2)
                    else:
                        # Create a basic schema for non-pydantic classes
                        schema_json = json.dumps(
                            {
                                "title": test_class_name,
                                "type": "object",
                                "properties": {"type": {"type": "string", "enum": [test_class_name]}, "description": {"type": "string"}},
                                "required": ["type"],
                            },
                            indent=2,
                        )
                except Exception as e:
                    logger.warning(f"Could not get schema for {test_class_name}: {e}")
                    # Create a basic schema
                    schema_json = json.dumps(
                        {"title": test_class_name, "type": "object", "properties": {"type": {"type": "string", "enum": [test_class_name]}, "description": {"type": "string"}}, "required": ["type"]},
                        indent=2,
                    )

                # Get extra data for this test class if any
                extra_data = self.test_class_extra_data.get(test_class_name, "{}")

                # Build the per-class system prompt
                system_prompt = TEST_GENERATION_PER_CLASS_SYSTEM_PROMPT.format(
                    test_class_name=test_class_name,
                    schema_json=schema_json,
                    task_prompt=task.prompt,
                    success_criteria=task.success_criteria or "N/A",
                    truncated_html=cleaned_html,
                    screenshot_desc=screenshot_desc,
                    interactive_elements=json.dumps(interactive_elements, indent=2),
                    domain_analysis=domain_analysis_dict,
                    extra_data=extra_data,  # Include the extra data in the prompt
                )

                # Call the LLM
                response = await self.llm_service.async_predict(messages=[{"role": "system", "content": system_prompt}], json_format=True)

                # Parse the response - Fix for JSON parsing error
                response_data = None
                if isinstance(response, str):
                    try:
                        # Clean the response string before parsing
                        cleaned_response = response.strip()
                        # Check if the response starts and ends with brackets
                        if not (cleaned_response.startswith('[') and cleaned_response.endswith(']')):
                            # Try to find valid JSON array within the response
                            start_idx = cleaned_response.find('[')
                            end_idx = cleaned_response.rfind(']')
                            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                                cleaned_response = cleaned_response[start_idx : end_idx + 1]
                        response_data = json.loads(cleaned_response)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse LLM response as JSON: {response}")
                        continue
                else:
                    # If the LLM returned Python dict/list, use as-is
                    response_data = response

                if not isinstance(response_data, list):
                    logger.warning(f"Expected a JSON array for test class {test_class_name}, got: {type(response_data)}")
                    continue

                if len(response_data) == 0:
                    # LLM says "not relevant" or no tests
                    logger.info(f"LLM returned no tests for {test_class_name} on task {task.id}")
                else:
                    # We have some test definitions for this class
                    # Ensure all tests have the correct type
                    for test in response_data:
                        if isinstance(test, dict):
                            # Ensure the type is set correctly
                            if test.get("type") != test_class_name:
                                test["type"] = test_class_name
                                logger.warning(f"Fixed incorrect type in {test_class_name} response")
                            # Add test_type if needed (for backward compatibility)
                            if "test_type" not in test:
                                test["test_type"] = test_class_name
                    logger.info(f"LLM returned {len(response_data)} tests for {test_class_name} on task {task.id}")
                    all_tests.extend(response_data)
            except Exception as e:
                logger.error(f"Error generating tests for {test_class_name} in task {task.id}: {str(e)}")
                logger.debug(f"Exception details: {type(e).__name__}, {repr(e)}")
        return all_tests

    async def _filter_tests(self, task: Task, raw_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter tests to ensure they're valid, relevant, and not semantically redundant.
        Uses LLM to make simple keep/discard decisions for each test.
        """
        if not raw_tests:
            return []

        # Step 1: Basic validation to ensure tests have valid types
        valid_type_tests = []
        for test_def in raw_tests:
            # Use either "type" or "test_type" field to determine the test type
            test_type = test_def.get("type") or test_def.get("test_type")
            # Skip tests with invalid test types
            if test_type not in self.test_class_map:
                logger.warning(f"Skipping test with invalid type: {test_type}")
                continue
            valid_type_tests.append(test_def)

        if len(valid_type_tests) <= 1:
            return valid_type_tests  # No need to filter if we have 0 or 1 test

        # Step 2: Use LLM to decide which tests to keep
        try:
            # Create a prompt for the LLM
            task_prompt = task.prompt
            success_criteria = task.success_criteria or "N/A"

            # Prepare test data with indices for reference
            indexed_tests = []
            for i, test in enumerate(valid_type_tests):
                indexed_tests.append({"index": i, "test": test})

            # Convert to JSON for the prompt
            tests_json = json.dumps(indexed_tests, indent=2)

            # Get any extra data needed for filtering
            extra_data_dict = {}
            for test_def in valid_type_tests:
                test_type = test_def.get("type") or test_def.get("test_type")
                if test_type in self.test_class_extra_data and test_type not in extra_data_dict:
                    extra_data_dict[test_type] = self.test_class_extra_data[test_type]

            extra_data = json.dumps(extra_data_dict, indent=2)

            # Use simplified prompt for test filtering
            system_prompt = TEST_FILTERING_PROMPT.format(task_prompt=task_prompt, success_criteria=success_criteria, tests_json=tests_json, extra_data=extra_data)

            # Call the LLM
            response = await self.llm_service.async_predict(messages=[{"role": "system", "content": system_prompt}], json_format=True)

            # Parse the response
            decisions = None
            if isinstance(response, str):
                try:
                    decisions = json.loads(response)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse LLM response as JSON: {response}")
                    return valid_type_tests  # Fall back to keeping all valid tests
            else:
                decisions = response

            # Extract test decisions
            if isinstance(decisions, list):
                filtered_tests = []
                for decision in decisions:
                    if isinstance(decision, dict):
                        index = decision.get("index")
                        keep = decision.get("keep")
                        reason = decision.get("reason", "No reason provided")
                        if index is not None and isinstance(index, int) and index < len(valid_type_tests):
                            if keep:
                                filtered_tests.append(valid_type_tests[index])
                                logger.info(f"Keeping test {index} ({valid_type_tests[index].get('type')}): {reason}")
                            else:
                                logger.info(f"Discarding test {index} ({valid_type_tests[index].get('type')}): {reason}")

                # Make sure we keep at least one test
                if not filtered_tests and valid_type_tests:
                    logger.warning("No tests kept after filtering, keeping the first valid test")
                    filtered_tests.append(valid_type_tests[0])

                logger.info(f"Filtered {len(valid_type_tests)} raw tests down to {len(filtered_tests)} for task {task.id}")
                return filtered_tests
            else:
                logger.warning(f"LLM response is not a list: {decisions}")
                return valid_type_tests  # Fall back to keeping all valid tests
        except Exception as e:
            logger.error(f"Error during filtering of tests: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}, {repr(e)}")
            return valid_type_tests  # Fall back to keeping all valid tests

    async def _instantiate_tests(self, task: Task, valid_tests: List[Dict[str, Any]]) -> None:
        """
        Instantiate test objects and add them to the task
        """
        for test_def in valid_tests:
            try:
                # Create a copy of the test definition to avoid modifying the original
                test_def_copy = test_def.copy()

                # Extract test type (using either "type" or "test_type" field)
                test_type = test_def_copy.pop("type", None) or test_def_copy.pop("test_type", None)
                if not test_type:
                    logger.warning(f"Test definition missing type: {test_def}")
                    continue

                # Get corresponding test class
                test_class = self.test_class_map.get(test_type)
                if not test_class:
                    logger.warning(f"Unknown test type: {test_type}")
                    continue

                # Add back the type field required by the model
                test_def_copy["type"] = test_type

                # Remove any fields that might cause issues with instantiation
                if "test_type" in test_def_copy:
                    test_def_copy.pop("test_type")

                # Instantiate the test object
                test_instance = test_class(**test_def_copy)
                task.tests.append(test_instance)
                logger.info(f"Added {test_type} to task {task.id}")
            except Exception as e:
                logger.error(f"Failed to instantiate test {test_def}: {str(e)}")
                logger.debug(f"Exception details: {type(e).__name__}, {repr(e)}")
