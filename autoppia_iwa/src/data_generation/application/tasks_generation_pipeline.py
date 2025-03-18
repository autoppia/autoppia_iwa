import random
from datetime import datetime

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.globals.tests.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository


class TaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.web_project = web_project
        self.task_config = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service = llm_service

        # Initialize pipelines
        self.local_pipeline = LocalTaskGenerationPipeline(web_project=web_project)
        self.global_pipeline = GlobalTaskGenerationPipeline(web_project=web_project, llm_service=llm_service)
        self.local_test_pipeline = LocalTestGenerationPipeline(web_project=web_project)
        self.global_test_pipeline = GlobalTestGenerationPipeline(web_project=web_project)

    async def generate(self) -> list[Task]:
        """
        Main method to generate tasks for the web project.
        Delegates URL handling to the specific pipelines.

        Returns:
            List of Task objects with added tests
        """
        start_time = datetime.now()
        logger.info("Starting combined task generation pipeline")
        all_tasks = []

        try:
            # 1) Generate local tasks if configured
            if self.task_config.generate_local_tasks:
                # We generate 15 prompts for each url
                logger.info("Generating local tasks")
                local_tasks = await self.local_pipeline.generate(number_of_prompts_per_url=3, max_urls=5, random_urls=True)
                logger.info(f"Generated {len(local_tasks)} local tasks")

                # Add tests to tasks
                local_tasks_with_tests = await self.local_test_pipeline.add_tests_to_tasks(local_tasks)
                all_tasks.extend(local_tasks_with_tests)

            # 2) Generate global tasks if configured
            if self.task_config.generate_global_tasks:
                logger.info("Generating global tasks")
                global_tasks = await self.global_pipeline.generate(prompts_per_use_case=self.task_config.prompts_per_use_case)
                logger.info(f"Generated {len(global_tasks)} global tasks")

                # Add tests to tasks
                global_tasks_with_tests = await self.global_test_pipeline.add_tests_to_tasks(global_tasks)
                all_tasks.extend(global_tasks_with_tests)

            # Apply final task limit if configured
            if self.task_config.final_task_limit and len(all_tasks) > self.task_config.final_task_limit:
                random.shuffle(all_tasks)
                all_tasks = all_tasks[: self.task_config.final_task_limit]
                logger.info(f"Applied final task limit: {len(all_tasks)} tasks")

            # Save tasks in DB if configured
            if self.task_config.save_task_in_db and all_tasks:
                for task in all_tasks:
                    self.synthetic_task_repository.save(task.model_dump())
                logger.info(f"Saved {len(all_tasks)} tasks to database")

            # Log completion
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task generation completed in {total_time:.2f} seconds. Generated {len(all_tasks)} tasks.")
            return all_tasks

        except Exception as e:
            logger.exception(f"Task generation failed: {e}")
            return []
