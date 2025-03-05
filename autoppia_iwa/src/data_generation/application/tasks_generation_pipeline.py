# file: task_generation_pipeline.py

import random
from datetime import datetime
from typing import List

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import TestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


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
        self.local_pipeline = LocalTaskGenerationPipeline(web_project=web_project)

    async def generate_tasks_for_url(self, url: str) -> List[Task]:
        logger.info("Processing page: {}", url)
        tasks = await self.local_pipeline.generate(url)
        logger.debug("Generated {} local tasks for page: {}", len(tasks), url)
        return tasks

    async def generate(self) -> List[Task]:
        start_time = datetime.now()
        logger.info("Starting task generation pipeline")
        all_tasks = []

        try:
            domain_analysis: DomainAnalysis = self.web_project.domain_analysis
            if not domain_analysis:
                raise ValueError("No domain analysis found in WebProject")

            logger.info("Domain analysis found, processing {} page analyses", len(domain_analysis.page_analyses))

            # Select pages based on configuration
            selected_pages = domain_analysis.page_analyses
            if self.task_config.random_urls:
                random.shuffle(selected_pages)

            selected_pages = selected_pages[: self.task_config.num_of_urls]

            # Generate local tasks for each page
            for page_info in selected_pages:
                url = page_info.page_url
                local_tasks = await self.generate_tasks_for_url(url)
                all_tasks.extend(local_tasks[: self.task_config.prompts_per_url])

            # Additional global tasks can be added here if needed
            if self.task_config.save_task_in_db:
                for task in all_tasks:
                    self.synthetic_task_repository.save(task.model_dump())
                    logger.info("Task saved to DB: {}", task)

            # Add tests to tasks
            test_pipeline = TestGenerationPipeline(web_project=self.web_project)
            tasks_with_tests = await test_pipeline.add_tests_to_tasks(all_tasks)

            # Filter out tasks without tests
            tasks_with_tests = [task for task in tasks_with_tests if task.tests]

            total_time = (datetime.now() - start_time).total_seconds()
            logger.info("Task generation completed in {:.2f} seconds", total_time)

            return tasks_with_tests

        except Exception as e:
            logger.exception("Task generation failed: {}", e)
            return []
