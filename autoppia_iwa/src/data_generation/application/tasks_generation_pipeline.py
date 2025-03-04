import random
from datetime import datetime
from typing import List
from dependency_injector.wiring import Provide
from loguru import logger
from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
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
        # Initialize pipelines
        self.local_pipeline = LocalTaskGenerationPipeline(web_project=web_project)
        self.global_pipeline = GlobalTaskGenerationPipeline(
            web_project=web_project, 
            llm_service=llm_service
        )

    async def generate_local_tasks_for_url(self, url: str) -> List[Task]:
        """Generate local tasks for a specific page URL"""
        logger.debug(f"Generating LOCAL tasks for URL: {url}")
        tasks = await self.local_pipeline.generate(url)
        return tasks

    async def generate_global_tasks_for_url(self, url: str) -> List[Task]:
        """
        Generate global tasks for a specific page URL
        Although global tasks typically don't depend on an individual URL,
        this method allows generating them in the context of a URL if needed.
        """
        logger.debug(f"Generating GLOBAL tasks for URL: {url}")
        all_global_tasks = []

        # Check if we have use cases in the web project
        if not self.web_project.use_cases:
            logger.warning("No use cases found in web project")
            return all_global_tasks

        # Generate tasks for each use case directly from web_project
        for use_case_name, use_case in self.web_project.use_cases.items():
            # Determine number of prompts per use case from config
            num_prompts = self.task_config.tasks_per_use_case

            logger.debug(f"Generating {num_prompts} global tasks for use case: {use_case_name}")
            global_tasks = await self.global_pipeline.generate_tasks_for_use_case(
                use_case=use_case,
                num_prompts=num_prompts
            )
            all_global_tasks.extend(global_tasks)

        logger.info(f"Generated {len(all_global_tasks)} global tasks across all use cases")
        return all_global_tasks

    async def generate_tasks_for_url(self, url: str) -> List[Task]:
        """
        Orchestrates generation of both local and global tasks for a specific URL,
        conditioned on config flags.
        """
        tasks_for_url = []
        # 1) Local tasks - page-specific tasks
        if self.task_config.generate_local_tasks:
            local_tasks = await self.generate_local_tasks_for_url(url)
            tasks_for_url.extend(local_tasks)
        # 2) Global tasks - use case based tasks
        if self.task_config.generate_global_tasks:
            global_tasks = await self.generate_global_tasks_for_url(url)
            tasks_for_url.extend(global_tasks)
        # Limit tasks per URL if configured
        if self.task_config.prompts_per_url and len(tasks_for_url) > self.task_config.prompts_per_url:
            # Shuffle to ensure random selection
            random.shuffle(tasks_for_url)
            tasks_for_url = tasks_for_url[:self.task_config.prompts_per_url]
        return tasks_for_url

    async def generate(self) -> List[Task]:
        """
        Main method to generate tasks for the web project.
        Returns:
            List of Task objects with added tests
        """
        start_time = datetime.now()
        logger.info("Starting combined task generation pipeline")
        all_tasks = []
        try:
            # Ensure we have domain analysis
            domain_analysis: DomainAnalysis = self.web_project.domain_analysis
            if not domain_analysis:
                raise ValueError("No domain analysis found in WebProject")
            logger.info(f"Domain analysis found, processing {len(domain_analysis.page_analyses)} page analyses")
            # Select pages based on configuration
            selected_pages = domain_analysis.page_analyses
            # Randomize if configured
            if self.task_config.random_urls:
                random.shuffle(selected_pages)
            # Limit to configured number of URLs
            if self.task_config.num_of_urls:
                selected_pages = selected_pages[:self.task_config.num_of_urls]
            # Generate tasks for selected pages
            for page_info in selected_pages:
                url = page_info.page_url
                tasks_for_url = await self.generate_tasks_for_url(url)
                all_tasks.extend(tasks_for_url)
            # Apply final task limit if configured
            if self.task_config.final_task_limit and len(all_tasks) > self.task_config.final_task_limit:
                random.shuffle(all_tasks)
                all_tasks = all_tasks[:self.task_config.final_task_limit]
            # Save tasks in DB if configured
            if self.task_config.save_task_in_db:
                for task in all_tasks:
                    self.synthetic_task_repository.save(task.model_dump())
                    logger.info(f"Task saved to DB: {task}")
            # Add tests to tasks
            test_pipeline = LocalTestGenerationPipeline(web_project=self.web_project)
            tasks_with_tests = await test_pipeline.add_tests_to_tasks(all_tasks)
            # Filter out tasks without tests if needed
            tasks_with_tests = [t for t in tasks_with_tests if t.tests]
            # Log completion
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task generation completed in {total_time:.2f} seconds. Generated {len(tasks_with_tests)} tasks.")
            return tasks_with_tests
        except Exception as e:
            logger.exception(f"Task generation failed: {e}")
            return []
