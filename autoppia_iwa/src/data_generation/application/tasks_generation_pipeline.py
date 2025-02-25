# file: task_generation_pipeline.py

import traceback
from datetime import datetime
from typing import List
from dependency_injector.wiring import Provide
from loguru import logger
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.data_generation.domain.classes import (
    Task,
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.llms.domain.interfaces import ILLM
from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.di_container import DIContainer


class TaskGenerationPipeline:
    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLM = Provide[DIContainer.llm_service]
    ):
        self.web_project: WebProject = web_project
        self.task_config: TaskGenerationConfig = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service: ILLM = llm_service
        self.local_pipeline = LocalTaskGenerationPipeline(self.llm_service)

    async def generate_tasks_for_url(self, url: str) -> List[Task]:
        logger.info("Processing page: {}", url)
        local_tasks = await self.local_pipeline.generate(url)
        logger.debug("Generated {} local tasks for page: {}", len(local_tasks), url)
        return local_tasks

    async def generate(self) -> TasksGenerationOutput:
        start_time = datetime.now()
        output = TasksGenerationOutput(tasks=[], total_phase_time=0.0)
        logger.info("Starting task generation pipeline")

        try:
            domain_analysis: DomainAnalysis = self.web_project.domain_analysis
            if not domain_analysis:
                raise ValueError("No domain analysis found in WebProject")
            logger.info("Domain analysis found, processing {} page analyses", len(domain_analysis.page_analyses))

            all_tasks: List[Task] = []

            # Generate local tasks for each page using the helper method
            for index, page_info in enumerate(domain_analysis.page_analyses):
                if index >= self.task_config.num_or_urls:
                    break
                url = page_info.page_url
                local_tasks = await self.generate_tasks_for_url(url)
                all_tasks.extend(local_tasks)

            # Additional global tasks can be added here if needed

            for t in all_tasks:
                if self.task_config.save_task_in_db:
                    self.synthetic_task_repository.save(t.model_dump())
                    logger.info("Task saved to DB: {}", t)
                output.tasks.append(t)

            output.total_phase_time = (datetime.now() - start_time).total_seconds()
            logger.info("Task generation completed in {} seconds", output.total_phase_time)

        except Exception as e:
            logger.error("Task generation failed: {} \n{}", e, traceback.format_exc())

        return output
