# file: autoppia_iwa/src/data_generation/application/task_generation_pipeline.py

import traceback
from datetime import datetime
from typing import Optional, List
from dependency_injector.wiring import Provide
from autoppia_iwa.src.data_generation.domain.classes import (
    Task,
    TaskGenerationConfig,
    TasksGenerationOutput,
)
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis
from autoppia_iwa.src.backend_demo_web.classes import WebProject
from .task_prompt_generator import TaskPromptGenerator
from .task_contextual_validator import TaskContextualValidator
from autoppia_iwa.src.llms.domain.interfaces import ILLMService


class TaskGenerationPipeline:
    """
    Coordinates the entire process of:
      1) Running web analysis (via WebAnalysisPipeline),
      2) Building/Updating a WebProject with domain analysis & pages,
      3) Generating tasks (both global & local) via TaskPromptGenerator,
      4) Optionally validating and storing tasks in a repository.

    Returns a TasksGenerationOutput object with the final tasks and timing info.
    """

    def __init__(
        self,
        web_project: WebProject,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLMService = Provide[DIContainer.llm_service]

    ):
        """
        :param config: Task generation configuration (contains the WebProject, 
                       desired # of tasks, whether to save them in DB, etc.).
        :param synthetic_task_repository: Repository to store generated tasks in a DB, if desired.
        :param llm_service: LLM service for generation & classification.
        :param web_analysis_repository: Repository used for storing or retrieving analysis data.
        """
        self.web_project:WebProject = web_project
        self.task_config:TaskGenerationConfig = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service:ILLMService = llm_service

    def generate(
        self
    ) -> TasksGenerationOutput:
        """
        Main method. Runs:
          - Web analysis,
          - Task generation,
          - Task validation,
          - (Optional) storage in DB.

        :param task_difficulty_level: (Currently not heavily used) 
                                      Could be used to guide LLM prompts if needed.
        :return: TasksGenerationOutput with the tasks and total_phase_time.
        """
        start_time = datetime.now()
        output = TasksGenerationOutput(tasks=[], total_phase_time=0.0)

        try:
            # 1) Web analysis
            domain_analysis = self.web_project.web_analysis
            if not domain_analysis:
                raise ValueError("Failed to run web analysis!")

            # 2) Generate tasks (both global & local) using TaskPromptGenerator
            task_prompt_generator = TaskPromptGenerator(
                web_project=self.web_project,
                llm_service=self.llm_service,
                # Instead of "n_prompts_per_call", we pass separate counts:
                global_tasks_count=self.task_config.global_tasks_to_generate,
                local_tasks_count_per_url=self.task_config.local_tasks_to_generate_per_url
            )
            all_generated_tasks: List[Task] = task_prompt_generator.generate()

            # 3) Validate tasks if needed
            validator = TaskContextualValidator(domain_analysis, self.llm_service)
            valid_tasks = validator.validate_tasks(all_generated_tasks)

            # 4) (Optional) Save tasks to the repository
            for t in valid_tasks:
                if self.task_config.save_task_in_db:
                    self.synthetic_task_repository.save(t.model_dump())
                output.tasks.append(t)

            output.total_phase_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            print(f"Tasks generation failed: {e}\n{traceback.format_exc()}")

        return output
