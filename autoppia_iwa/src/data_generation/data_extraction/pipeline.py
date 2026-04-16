from datetime import datetime

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tests.simple.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.interfaces import ILLM

from .generator import DataExtractionTaskGenerator


class DataExtractionTaskGenerationPipeline:
    """Dedicated pipeline for DataExtraction task generation."""

    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.web_project = web_project
        self.task_config = config
        self.llm_service = llm_service

        self.task_generator = DataExtractionTaskGenerator(web_project=web_project, llm_service=llm_service)
        self.global_test_pipeline = GlobalTestGenerationPipeline()

    async def generate(self) -> list[Task]:
        start_time = datetime.now()
        all_tasks: list[Task] = []

        try:
            tasks = await self.task_generator.generate(
                prompts_per_use_case=self.task_config.prompts_per_use_case,
                use_cases=self.task_config.use_cases,
                dynamic=self.task_config.dynamic,
                test_types="data_extraction_only",
                data_extraction_use_cases=self.task_config.data_extraction_use_cases,
            )

            tasks_with_tests = self.global_test_pipeline.add_tests_to_tasks(
                tasks,
                test_types="data_extraction_only",
                data_extraction_use_cases=self.task_config.data_extraction_use_cases,
            )
            all_tasks.extend(tasks_with_tests)

            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"[DATA_EXTRACTION] DE task generation completed in {total_time:.2f} seconds. Generated {len(all_tasks)} tasks.")
            return all_tasks
        except Exception as e:
            logger.exception(f"[DATA_EXTRACTION] DE task generation failed: {e}")
            return []
