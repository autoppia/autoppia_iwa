# file: task_generation_pipeline.py

import random
from datetime import datetime
from typing import List

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline
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

        # Pipelines
        self.local_pipeline = LocalTaskGenerationPipeline(web_project=web_project)
        self.global_pipeline = GlobalTaskGenerationPipeline(web_project=web_project, llm_service=llm_service)

    async def generate_local_tasks_for_url(self, url: str) -> List[Task]:
        """
        Generate local tasks for a specific page URL using the LocalTaskGenerationPipeline.
        """
        logger.debug("Generating LOCAL tasks for URL: {}", url)
        tasks = await self.local_pipeline.generate(url)
        return tasks

    async def generate_global_tasks_for_url(self, url: str) -> List[Task]:
        """
        Generate global tasks for a specific page URL using the GlobalTaskGenerationPipeline.
        Although 'global' tasks typically do not depend on an individual URL,
        you can still pass the URL if it's required by your scenario/config.

        In many cases, 'global' tasks may be generated only once (not per URL).
        But this method demonstrates how to do it for each URL if needed.
        """
        logger.debug("Generating GLOBAL tasks for URL: {}", url)
        # Example: if you have specific global use cases defined in your config
        # that you want to generate for each page visited
        all_global_tasks = []

        if getattr(self.task_config, "global_use_cases", None):
            for use_case_name, num_prompts in self.task_config.global_use_cases.items():
                logger.debug("Generating {} global tasks for use case: {} on URL: {}", 
                             num_prompts, use_case_name, url)
                global_tasks = await self.global_pipeline.generate_tasks(
                    use_case_name=use_case_name,
                    num_prompts=num_prompts
                )
                all_global_tasks.extend(global_tasks)

        return all_global_tasks

    async def generate_tasks_for_url(self, url: str) -> List[Task]:
        """
        Orchestrates generation of both local and global tasks for a specific URL,
        conditioned on config flags.
        """
        tasks_for_url = []

        # 1) Local tasks
        if self.task_config.generate_local_tasks:
            local_tasks = await self.generate_local_tasks_for_url(url)
            tasks_for_url.extend(local_tasks)

        # 2) Global tasks
        if self.task_config.generate_global_tasks:
            global_tasks = await self.generate_global_tasks_for_url(url)
            tasks_for_url.extend(global_tasks)

        return tasks_for_url

    async def generate(self) -> List[Task]:
        start_time = datetime.now()
        logger.info("Starting combined task generation pipeline")
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

            selected_pages = selected_pages[: self.task_config.num_or_urls]

            # Generate tasks (local + global) for each page
            for page_info in selected_pages:
                url = page_info.page_url
                tasks_for_url = await self.generate_tasks_for_url(url)

                # If prompts_per_url is set, limit the total tasks for each URL
                tasks_for_url = tasks_for_url[: self.task_config.prompts_per_url]

                all_tasks.extend(tasks_for_url)

            # (Optional) Save tasks in DB
            if self.task_config.save_task_in_db:
                for task in all_tasks:
                    self.synthetic_task_repository.save(task.model_dump())
                    logger.info("Task saved to DB: {}", task)

            # (Optional) Add or unify tests
            test_pipeline = TestGenerationPipeline(web_project=self.web_project)
            tasks_with_tests = await test_pipeline.add_tests_to_tasks(all_tasks)

            # Filter out tasks that end up without tests (if desired)
            tasks_with_tests = [t for t in tasks_with_tests if t.tests]

            total_time = (datetime.now() - start_time).total_seconds()
            logger.info("Task generation completed in {:.2f} seconds", total_time)
            return tasks_with_tests

        except Exception as e:
            logger.exception("Task generation failed: {}", e)
            return []
