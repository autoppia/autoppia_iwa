import random
from datetime import datetime

from dependency_injector.wiring import Provide
from loguru import logger

from autoppia_iwa.src.data_generation.application.tasks.globals.global_task_generation import GlobalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks.globals.tests.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.domain.interfaces import ILLM


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
        self.global_pipeline = GlobalTaskGenerationPipeline(web_project=web_project, llm_service=llm_service)

        self.global_test_pipeline = GlobalTestGenerationPipeline()

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
            # 1) Generate global tasks if configured
            if self.task_config.generate_global_tasks:
                logger.info("Generating global tasks")
                global_tasks = await self.global_pipeline.generate(
                    prompts_per_use_case=self.task_config.prompts_per_use_case, 
                    num_use_cases=self.task_config.num_use_cases
                    )

                logger.info(f"Generated {len(global_tasks)} global tasks")

                # Add tests to tasks
                global_tasks_with_tests = await self.global_test_pipeline.add_tests_to_tasks(global_tasks)
                all_tasks.extend(global_tasks_with_tests)

                for task in global_tasks_with_tests:
                    print("Prompt: ", task.prompt)
                    for _i, _test in enumerate(task.tests):
                        print(f"Test: {_i}")
                        from pprint import pprint

                        pprint(_test.model_dump())
                #         pass

            # Apply final task limit if configured
            if self.task_config.final_task_limit and len(all_tasks) > self.task_config.final_task_limit:
                random.shuffle(all_tasks)
                all_tasks = all_tasks[: self.task_config.final_task_limit]
                logger.info(f"Applied final task limit: {len(all_tasks)} tasks")

            # Log completion
            total_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task generation completed in {total_time:.2f} seconds. Generated {len(all_tasks)} tasks.")
            return all_tasks

        except Exception as e:
            logger.exception(f"Task generation failed: {e}")
            return []
