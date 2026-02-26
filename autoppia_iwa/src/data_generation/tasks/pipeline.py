from datetime import datetime

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.data_generation.tests.simple.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM

TASK_GENERATION_LEVEL_NAME = "TASK_GENERATION"
TASK_GENERATION_LEVEL_NO = 23


def _ensure_task_generation_level() -> None:
    """Register the TASK_GENERATION level if it's missing."""
    try:
        logger.level(TASK_GENERATION_LEVEL_NAME)
    except ValueError:
        logger.level(TASK_GENERATION_LEVEL_NAME, TASK_GENERATION_LEVEL_NO)


def _log_task_generation(message: str, context: str = "TASK_GENERATION") -> None:
    """Helper to log task generation events using the TASK_GENERATION level."""
    try:
        from autoppia_iwa.entrypoints.benchmark.utils.logging import log_task_generation_event

        log_task_generation_event(message, context=context)
    except ImportError:
        _ensure_task_generation_level()
        prefix = "" if context == "TASK_GENERATION" else f"[{context}] "
        logger.log(TASK_GENERATION_LEVEL_NAME, f"{prefix}{message}")


class TaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.web_project = web_project
        self.task_config = config
        self.llm_service = llm_service

        # Initialize task generator and test pipeline
        self.task_generator = SimpleTaskGenerator(web_project=web_project, llm_service=llm_service)
        self.global_test_pipeline = GlobalTestGenerationPipeline()

    async def generate(self) -> list[Task]:
        """
        Main method to generate tasks for the web project.
        Delegates URL handling to the specific pipelines.

        Returns:
            List of Task objects with added tests
        """
        start_time = datetime.now()
        _log_task_generation("Starting combined task generation pipeline")
        all_tasks = []

        try:
            # Generate tasks
            tasks = await self.task_generator.generate(prompts_per_use_case=self.task_config.prompts_per_use_case, use_cases=self.task_config.use_cases, dynamic=self.task_config.dynamic)

            _log_task_generation(f"Generated {len(tasks)} tasks")

            # Add tests to tasks
            tasks_with_tests = self.global_test_pipeline.add_tests_to_tasks(tasks)
            all_tasks.extend(tasks_with_tests)

            # Log completion
            total_time = (datetime.now() - start_time).total_seconds()
            _log_task_generation(f"Task generation completed in {total_time:.2f} seconds. Generated {len(all_tasks)} tasks.")
            return all_tasks

        except Exception as e:
            logger.exception(f"Task generation failed: {e}")
            return []
