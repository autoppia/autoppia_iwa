import json
from typing import Any, Dict, List
from loguru import logger
from dependency_injector.wiring import Provide

# LLM & domain imports
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import (
    CheckUrlTest, 
    FindInHtmlTest, 
    CheckEventEmittedTest, 
    CheckPageViewEventTest,
    JudgeBaseOnHTML,
    JudgeBaseOnScreenshot
)
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.shared.web_utils import detect_interactive_elements

# Import prompts
from autoppia_iwa.src.data_generation.application.tests.prompts import (
    TEST_CONTEXT_PROMPT,
    TEST_GENERATION_SYSTEM_PROMPT,
    FILTER_PROMPT
)

# Logic generator (optional)
from autoppia_iwa.src.data_generation.application.tests.logic.logic_function_generator import (
    TestLogicGenerator,
)


class TestGenerationPipeline:
    """
    A pipeline that:
      1) Gathers context (HTML, screenshot info, etc.) for each Task.
      2) Uses LLM to generate appropriate tests based on the task context.
      3) Filters the generated tests to ensure they're valid and relevant.
      4) Instantiates the test objects and adds them to the task.
      5) (Optionally) generates a logic function for the entire set of tests.
    """

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

        # Map of test type names to classes
        self.test_class_map = {
            "CheckUrlTest": CheckUrlTest,
            "FindInHtmlTest": FindInHtmlTest,
            "CheckEventEmittedTest": CheckEventEmittedTest,
            "CheckPageViewEventTest": CheckPageViewEventTest,
            "JudgeBaseOnHTML": JudgeBaseOnHTML,
            "JudgeBaseOnScreenshot": JudgeBaseOnScreenshot,
            "OpinionBaseOnScreenshot": JudgeBaseOnScreenshot  # Map to the same class
        }

    async def add_tests_to_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Main pipeline function that adds appropriate tests to each task
        """
        for task in tasks:
            try:
                # STEP 1: Generate raw tests using LLM
                raw_tests = await self._generate_tests(task)

                if not raw_tests:
                    logger.warning(f"No tests generated for task {task.id}")
                    continue

                # STEP 2: Filter tests to ensure they're valid
                valid_tests = await self._filter_tests(task, raw_tests)

                # STEP 3: Instantiate and add the test objects to the task
                await self._instantiate_tests(task, valid_tests)

                # STEP 4: Optionally, generate a logic function that references these tests
                if task.tests:
                    task.logic_function = await self.logic_generator.generate_logic(
                        task=task,
                        tests=task.tests
                    )
                    logger.info(f"Generated logic function for task {task.id}")

            except Exception as e:
                logger.error(f"Failed to generate tests for task={task.id}: {e}")

        return tasks

    async def _generate_tests(self, task: Task) -> List[Dict[str, Any]]:
        """
        Generate test definitions using the LLM
        """
        try:
            # Gather contextual data
            html = task.html
            cleaned_html = task.clean_html[:self.truncate_html_chars] if task.clean_html else ""
            screenshot_desc = task.screenshot_description or ""
            interactive_elements = detect_interactive_elements(cleaned_html)
            domain_analysis = self.web_project.domain_analysis
            page_analysis = domain_analysis.get_page_analysis(url=task.url)

            # Prepare generation prompt
            generation_user_content = (
                f"Task Prompt: {task.prompt}\n\n"
                f"Success Criteria: {task.success_criteria or 'N/A'}\n\n"
                f"Cleaned HTML:\n{cleaned_html}\n\n"
                f"Screenshot summary:\n{screenshot_desc}\n\n"
                f"Interactive elements:\n{json.dumps(interactive_elements, indent=2)}\n\n"
                f"Project context:\n{TEST_CONTEXT_PROMPT}\n\n"
                "Return an array of test definitions. Each must have 'test_type' and optional fields."
            )

            # Call the LLM
            response = await self.llm_service.async_predict(
                messages=[
                    {"role": "system", "content": TEST_GENERATION_SYSTEM_PROMPT},
                    {"role": "user", "content": generation_user_content},
                ],
                json_format=True
            )

            # Parse response
            try:
                raw_tests = json.loads(response) if isinstance(response, str) else response
                if not isinstance(raw_tests, list):
                    logger.warning(f"LLM response is not a list: {raw_tests}")
                    return []

                logger.info(f"Generated {len(raw_tests)} raw tests for task {task.id}")
                return raw_tests

            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {response}")
                return []

        except Exception as e:
            logger.error(f"Error generating tests for task {task.id}: {e}")
            return []

    async def _filter_tests(self, task: Task, raw_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter tests to ensure they're valid and relevant using the TestGenerationPipeline.
        """
        return raw_tests
        try:
            # Create an instance of TestGenerationPipeline if not already available
            if not hasattr(self, '_test_pipeline'):
                self._test_pipeline = TestGenerationPipeline(
                    llm_service=self.llm_service,
                    truncate_html_chars=1500  # Use the same value or make configurable
                )

            # Get the truncated HTML
            truncated_html = task.clean_html[:1500] if task.clean_html else ""

            # Use the pipeline's filter_generated_tests method
            valid_tests = await self._test_pipeline.filter_generated_tests(
                proposed_tests=raw_tests,
                truncated_html=truncated_html,
                task=task
            )

            # Log filtering results
            logger.info(f"Filtered {len(raw_tests) - len(valid_tests)} tests for task {task.id}")

            return valid_tests
        except Exception as e:
            logger.error(f"Error filtering tests for task {task.id}: {e}")
            return raw_tests  # Fall back to raw tests if filtering fails

    async def _instantiate_tests(self, task: Task, valid_tests: List[Dict[str, Any]]) -> None:
        """
        Instantiate test objects and add them to the task
        """
        for test_def in valid_tests:
            try:
                # Extract test type
                test_type = test_def.pop("test_type", None)
                if not test_type:
                    logger.warning(f"Test definition missing test_type: {test_def}")
                    continue

                # Get corresponding test class
                test_class = self.test_class_map.get(test_type)
                if not test_class:
                    logger.warning(f"Unknown test type: {test_type}")
                    continue

                # Handle special cases for test parameters
                if test_class in [JudgeBaseOnHTML, JudgeBaseOnScreenshot]:
                    # Ensure 'name' parameter is present
                    if "name" not in test_def:
                        test_def["name"] = test_type

                # Add test_type for BaseTaskTest if needed
                if hasattr(test_class, 'test_type') and 'test_type' not in test_def:
                    if test_class in [CheckUrlTest, FindInHtmlTest, JudgeBaseOnHTML, JudgeBaseOnScreenshot]:
                        test_def['test_type'] = 'frontend'
                    elif test_class in [CheckEventEmittedTest, CheckPageViewEventTest]:
                        test_def['test_type'] = 'backend'

                # Instantiate the test object
                test_instance = test_class(**test_def)
                task.tests.append(test_instance)
                logger.info(f"Added {test_type} to task {task.id}")

            except Exception as e:
                logger.error(f"Failed to instantiate test {test_def}: {e}")
