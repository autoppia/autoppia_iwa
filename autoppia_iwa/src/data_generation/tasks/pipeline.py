import random
from datetime import datetime

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.simple.global_task_generation import SimpleTaskGenerator
from autoppia_iwa.src.data_generation.tests.simple.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer

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

        # Initialize pipelines
        self.global_pipeline = SimpleTaskGenerator(web_project=web_project, llm_service=llm_service)

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
            # 1) Generate global tasks if configured
            if self.task_config.generate_global_tasks:
                _log_task_generation("Generating global tasks")
                global_tasks = await self.global_pipeline.generate(
                    prompts_per_use_case=self.task_config.prompts_per_use_case, num_use_cases=self.task_config.num_use_cases, use_cases=self.task_config.use_cases, dynamic=self.task_config.dynamic
                )

                _log_task_generation(f"Generated {len(global_tasks)} global tasks")

                # Add tests to tasks
                global_tasks_with_tests = await self.global_test_pipeline.add_tests_to_tasks(global_tasks)
                all_tasks.extend(global_tasks_with_tests)

                # Visualize tasks with their tests
                visualizer = SubnetVisualizer()
                for task in global_tasks_with_tests:
                    visualizer.show_task_with_tests(task)

            # Apply final task limit if configured
            if self.task_config.final_task_limit and len(all_tasks) > self.task_config.final_task_limit:
                random.shuffle(all_tasks)
                all_tasks = all_tasks[: self.task_config.final_task_limit]
                _log_task_generation(f"Applied final task limit: {len(all_tasks)} tasks", context="LIMIT")

            # Log completion
            total_time = (datetime.now() - start_time).total_seconds()
            _log_task_generation(f"Task generation completed in {total_time:.2f} seconds. Generated {len(all_tasks)} tasks.")
            return all_tasks

        except Exception as e:
            logger.exception(f"Task generation failed: {e}")
            return []
