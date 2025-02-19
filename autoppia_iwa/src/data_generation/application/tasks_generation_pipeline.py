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
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from autoppia_iwa.src.data_generation.application.task_prompt_generator import TaskPromptGenerator
from autoppia_iwa.src.data_generation.application.task_contextual_validator import TaskContextualValidator
from autoppia_iwa.src.llms.domain.interfaces import ILLMService

# Import the test generator
from autoppia_iwa.src.data_generation.application.tests.task_tests_generator import TaskTestGenerator


class TaskGenerationPipeline:
    """
    Coordinates the entire process of:
      1) Running web analysis (via WebAnalysisPipeline),
      2) Building/Updating a WebProject with domain analysis & pages,
      3) Generating tasks (both global & local) via TaskPromptGenerator,
      4) Validating tasks,
      5) Generating tests for each task,
      6) Optionally storing tasks in DB.

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

    def generate(self) -> TasksGenerationOutput:
        start_time = datetime.now()
        output = TasksGenerationOutput(tasks=[], total_phase_time=0.0)

        try:
            # 1) Web analysis must already be completed and stored in web_project.web_analysis
            domain_analysis = self.web_project.web_analysis
            if not domain_analysis:
                raise ValueError("Failed to run web analysis!")

            # 2) Generate tasks
            task_prompt_generator = TaskPromptGenerator(
                web_project=self.web_project,
                llm_service=self.llm_service,
                global_tasks_count=self.task_config.global_tasks_to_generate,
                local_tasks_count_per_url=self.task_config.local_tasks_to_generate_per_url
            )
            all_generated_tasks: List[Task] = task_prompt_generator.generate()

            print("----- Raw Generated Tasks -----")
            for t in all_generated_tasks:
                print(t.model_dump())

            # 3) Validate tasks
            validator = TaskContextualValidator(domain_analysis, self.llm_service)
            valid_tasks = validator.validate_tasks(all_generated_tasks)

            print("----- Validated Tasks -----")
            for t in valid_tasks:
                print(t.model_dump())

            # 4) Generate tests for each valid task
            test_generator = TaskTestGenerator(
                web_project=self.web_project,
                web_analysis=domain_analysis,
                llm_service=self.llm_service
            )
            for t in valid_tasks:
                # Use the task's actual URL if not 'N/A'; otherwise default to domain start_url.
                page_url = t.url if t.url != "N/A" else domain_analysis.start_url
                t.tests = test_generator.generate_task_tests(
                    task_description=t.prompt,
                    page_url=page_url,
                    page_html=None  # or pass a string if needed
                )

            # 5) (Optional) save tasks in DB and build final output
            for t in valid_tasks:
                if self.task_config.save_task_in_db:
                    self.synthetic_task_repository.save(t.model_dump())
                output.tasks.append(t)

            output.total_phase_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            print(f"Tasks generation failed: {e}\n{traceback.format_exc()}")

        return output

    @staticmethod
    def _get_page_html(page) -> str:
        from autoppia_iwa.src.shared.utils import extract_html
        return extract_html(page.page_url) or page.html_source
