import traceback
from datetime import datetime
from typing import List
from dependency_injector.wiring import Provide

from autoppia_iwa.src.data_generation.domain.classes import (
    Task,
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.data_generation.application.task_prompt_generator import TaskPromptGenerator
from autoppia_iwa.src.data_generation.application.tests.task_tests_generator import TaskTestGenerator
from autoppia_iwa.src.llms.domain.interfaces import ILLMService
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository


class TaskGenerationPipeline:
    """
    Coordinates the entire process of:
      1) Running web analysis (via WebAnalysisPipeline),
      2) Building/Updating a WebProject with domain analysis & pages,
      3) Generating tasks (both global & local) via TaskPromptGenerator,
      4) Generating tests for each task,
      5) Optionally storing tasks in DB.

    Returns a TasksGenerationOutput object with the final tasks and timing info.
    """

    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLMService = Provide[DIContainer.llm_service]
    ):
        self.web_project: WebProject = web_project
        self.task_config: TaskGenerationConfig = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service: ILLMService = llm_service

    async def generate(self) -> TasksGenerationOutput:
        start_time = datetime.now()
        output = TasksGenerationOutput(tasks=[], total_phase_time=0.0)

        try:
            domain_analysis = self.web_project.web_analysis
            if not domain_analysis:
                raise ValueError("Failed to run web analysis!")

            # Generate tasks (including internal verifications/filters)
            task_prompt_generator = TaskPromptGenerator(
                web_project=self.web_project,
                llm_service=self.llm_service,
                global_tasks_count=self.task_config.global_tasks_to_generate,
                local_tasks_count_per_url=self.task_config.local_tasks_to_generate_per_url
            )
            generated_tasks: List[Task] = await task_prompt_generator.generate()

            # Generate tests for each valid task
            test_generator = TaskTestGenerator(
                web_project=self.web_project,
                web_analysis=domain_analysis,
                llm_service=self.llm_service
            )
            for t in generated_tasks:
                page_url = t.url if t.url != "N/A" else domain_analysis.start_url
                t.tests = await test_generator.generate_task_tests(
                    task_description=t.prompt,
                    page_url=page_url,
                    page_html=None
                )

            # Store tasks if requested
            for t in generated_tasks:
                if self.task_config.save_task_in_db:
                    self.synthetic_task_repository.save(t.model_dump())
                output.tasks.append(t)

            output.total_phase_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            print(f"Tasks generation failed: {e}\n{traceback.format_exc()}")

        return output
