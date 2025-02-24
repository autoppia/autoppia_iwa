import json
from typing import List, Any, Dict

from loguru import logger
from pydantic import ValidationError

# Dependency injection / LLM interface
from dependency_injector.wiring import Provide
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.di_container import DIContainer

# Domain & data models
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import WebProject

# Utility code
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements
from .utils import normalize_test_config

# Prompts and logic
from autoppia_iwa.src.data_generation.application.tests.prompts import (
    TEST_CONTEXT_PROMPT,
    TEST_GENERATION_SYSTEM_PROMPT,
)
from autoppia_iwa.src.data_generation.application.tests.logic.logic_function_generator import (
    TestLogicGenerator
)

# Schemas (see above snippet or your actual imports)
from autoppia_iwa.src.data_generation.application.tests.schemas import (
    ProposedTestList,
    ProposedTestDefinition
)


class TestGenerationPipeline:
    """
    A pipeline that, for each Task:
      1) Asks the LLM to propose minimal test definitions referencing relevant test classes.
      2) Filters out guess-based or redundant tests (via `_filter_generated_tests`).
      3) Proposes a final Boolean expression referencing x(i,j) for overall success (logic).
    """

    def __init__(
        self,
        web_project: WebProject,
        llm_service: ILLM = Provide[DIContainer.llm_service],
        truncate_html_chars: int = 1500,
    ):
        self.llm_service = llm_service
        self.truncate_html_chars = truncate_html_chars
        self.web_project = web_project
        self.logic_generator = TestLogicGenerator()

    async def add_tests_to_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Iterates over tasks, calls the LLM to generate test definitions,
        filters and normalizes them, and finally generates a logic function for success.
        """
        for task in tasks:
            try:
                # Gather contextual data
                cleaned_html = task.clean_html or ""
                screenshot_desc = task.screenshot_description or ""
                interactive_elements = detect_interactive_elements(cleaned_html)
                domain_analysis = self.web_project.domain_analysis
                page_analysis = domain_analysis.get_page_analysis(url=task.url)

                # STEP 1: Prompt the LLM for raw tests
                generation_user_content = (
                    f"Task Prompt: {task.prompt}\n\n"
                    f"Success Criteria: {task.success_criteria or 'N/A'}\n\n"
                    f"Cleaned HTML:\n{cleaned_html}\n\n"
                    f"Screenshot summary:\n{screenshot_desc}\n\n"
                    f"Interactive elements:\n{json.dumps(interactive_elements, indent=2)}\n\n"
                    f"Project context:\n{TEST_CONTEXT_PROMPT}\n\n"
                    "Return an array of test definitions. Each must have 'test_type' and optional fields."
                )

                test_generation_response = await self.llm_service.async_predict(
                    messages=[
                        {"role": "system", "content": TEST_GENERATION_SYSTEM_PROMPT},
                        {"role": "user", "content": generation_user_content},
                    ],
                    json_format=True,
                    schema=ProposedTestList.model_json_schema()
                )
                logger.debug(f"LLM raw response (test generation): {test_generation_response}")
                print("test_generation_response", test_generation_response)

                # STEP 2: Parse, validate and normalize the returned JSON into dictionaries
                normalized_tests = []
                try:
                    response_obj = json.loads(test_generation_response)
                    test_list = response_obj.get("ProposedTestList", [])

                    print("test_list", test_list)
                    # Parse the raw test list using your schema
                    parsed_tests = ProposedTestList.parse_obj(test_list)
                    tests = parsed_tests.root

                    print("tests", tests)
                    for test_item in tests:
                        try:
                            # Ensure test_item is a dictionary
                            if not isinstance(test_item, dict):
                                test_item = ProposedTestDefinition.parse_obj(test_item).dict()
                            # If "fields" key doesn't exist, move non-test_type keys into it
                            if "fields" not in test_item:
                                fields = {}
                                for key, value in list(test_item.items()):
                                    if key != "test_type":
                                        fields[key] = value
                                        test_item.pop(key)
                                test_item["fields"] = fields

                            # Parse again to enforce schema, then convert to dict
                            test_def = ProposedTestDefinition.parse_obj(test_item)
                            # Normalize (flatten fields and remap test_type)
                            config = normalize_test_config(test_def.dict())
                            print("config", config)
                            normalized_tests.append(config)
                        except ValidationError as e:
                            logger.warning(f"Failed to parse individual test definition: {e}")
                except json.JSONDecodeError as e:
                    logger.warning(f"LLM returned invalid JSON: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error parsing ProposedTestList: {e}")

                # STEP 3: Filter the generated tests (if necessary)
                filtered_tests = await self._filter_generated_tests(
                    normalized_tests,
                    cleaned_html[: self.truncate_html_chars],
                    task
                )
                # Ensure every test is a dictionary
                filtered_tests = [test if isinstance(test, dict) else test.dict() for test in filtered_tests]
                logger.debug(f"Filtered tests for task {task.id}: {filtered_tests}")

                # Convert the final test dicts into actual BaseTaskTest instances
                test_objects = BaseTaskTest.assign_tests(filtered_tests)
                task.tests.extend(test_objects)

                # STEP 4: Generate logic function for the entire set of tests
                logic_generator = TestLogicGenerator(llm_service=self.llm_service)
                task.logic_function = await logic_generator.generate_logic(
                    task=task,
                    tests=test_objects
                )

            except Exception as e:
                logger.error(f"Failed to generate tests/logic for task {task.id}: {e}")
                raise e

        return tasks

    async def _filter_generated_tests(
        self,
        proposed_tests: List[Dict[str, Any]],
        partial_cleaned_html: str,
        task: Task
    ) -> List[Dict[str, Any]]:
        return proposed_tests
        # Convert the proposed test dictionaries into BaseTaskTest objects
        tests = BaseTaskTest.assign_tests(proposed_tests)

        # Generate a logic expression based on the task and the complete test configurations
        logic_expr = await self.logic_generator.generate_logic(task, tests)

        # Log the generated logic expression for debugging/verification
        logger.info(f"Generated logic expression: {json.dumps(logic_expr, indent=2)}")

        # In a real implementation, you might now use the logic_expr to filter tests based
        # on additional criteria (e.g. removing duplicates, guess-based tests, etc.)
        return proposed_tests
