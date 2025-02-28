# file: task_generation_pipeline.py

import traceback
from datetime import datetime
from typing import List
from dependency_injector.wiring import Provide
from loguru import logger
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import TestGenerationPipeline


class TaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLM = Provide[DIContainer.llm_service],
    ):
        self.web_project: WebProject = web_project
        self.task_config: TaskGenerationConfig = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service: ILLM = llm_service
        self.local_pipeline = LocalTaskGenerationPipeline(web_project=web_project)

    async def generate_tasks_for_url(self, url: str) -> List[Task]:
        logger.info("Processing page: {}", url)
        local_tasks = await self.local_pipeline.generate(url)
        logger.debug("Generated {} local tasks for page: {}", len(local_tasks), url)
        return local_tasks

    async def generate(self) -> List[Task]:
        start_time = datetime.now()
        all_tasks: List[Task] = []
        logger.info("Starting task generation pipeline")

        try:
            domain_analysis: DomainAnalysis = self.web_project.domain_analysis
            if not domain_analysis:
                raise ValueError("No domain analysis found in WebProject")

            logger.info("Domain analysis found, processing {} page analyses", len(domain_analysis.page_analyses))

            # Randomly select page analyses instead of sequential processing
            import random

            available_pages = domain_analysis.page_analyses.copy()
            random.shuffle(available_pages)

            # Take only the number specified in the configuration
            selected_pages = available_pages[: self.task_config.num_or_urls]

            # Generate local tasks for each randomly selected page
            for page_info in selected_pages:
                url = page_info.page_url
                local_tasks = await self.generate_tasks_for_url(url)
                all_tasks.extend(local_tasks)

            # Additional global tasks can be added here if needed
            if self.task_config.save_task_in_db:
                for t in all_tasks:
                    self.synthetic_task_repository.save(t.model_dump())
                    logger.info(f"Task saved to DB: {t}")

            test_pipeline = TestGenerationPipeline(llm_service=self.llm_service, web_project=self.web_project)
            all_tasks = await test_pipeline.add_tests_to_tasks(all_tasks)

            total_phase_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task generation completed in {total_phase_time} seconds")
        except Exception as e:
            logger.error("Task generation failed: {} \n{}", e, traceback.format_exc())
        return all_tasks
