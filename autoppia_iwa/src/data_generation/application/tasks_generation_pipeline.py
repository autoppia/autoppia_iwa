# file: autoppia_iwa/src/data_generation/application/task_generation_pipeline.py

import traceback
from datetime import datetime
from typing import Optional, List

from dependency_injector.wiring import Provide

from autoppia_iwa.src.data_generation.domain.classes import Task, TaskDifficultyLevel, TaskGenerationConfig, TasksGenerationOutput
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.llms.infrastructure.llm_service import ILLMService
from autoppia_iwa.src.shared.infrastructure.databases.base_mongo_repository import BaseMongoRepository
from autoppia_iwa.src.shared.utils import extract_html
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis, SinglePageAnalysis

from .task_prompt_generator import TaskPromptGenerator
# from .task_tests_generator import TaskTestGenerator  # ignoring tests for now
from .task_contextual_validator import TaskContextualValidator


class TaskGenerationPipeline:
    def __init__(
        self,
        config: TaskGenerationConfig,
        synthetic_task_repository: BaseMongoRepository = Provide[DIContainer.synthetic_task_repository],
        llm_service: ILLMService = Provide[DIContainer.llm_service],
        web_analysis_repository: BaseMongoRepository = Provide[DIContainer.analysis_repository],
    ):
        """
        Initializes the task generation pipeline.

        :param config: Task generation input configuration.
        :param synthetic_task_repository: Repository to store generated tasks.
        :param llm_service: Language model service for generating prompts or tests.
        """
        self.task_config = config
        self.synthetic_task_repository = synthetic_task_repository
        self.llm_service = llm_service
        self.web_analysis_repository = web_analysis_repository

    def generate(self, task_difficulty_level: TaskDifficultyLevel = TaskDifficultyLevel.EASY) -> TasksGenerationOutput:
        """
        Main method for task generation. Runs web analysis, generates prompts, and processes tasks.
        """
        start_time = datetime.now()
        global_tasks_output = TasksGenerationOutput(tasks=[], total_phase_time=0.0)

        try:
            # 1) WEB ANALYSIS
            web_analysis = self._run_web_analysis()
            if not web_analysis:
                raise ValueError("Failed to run web analysis!")

            # (Optional) Suppose we set some domain_type or features after analysis:
            # web_analysis.domain_type = "e-commerce"
            # web_analysis.features = ["login", "checkout", "search"] 
            # This would normally come from a domain analysis step or a config file.

            # 2) Initialize TaskGenerators
            task_prompt_generator = TaskPromptGenerator(
                num_prompts_per_url=self.task_config.number_of_prompts_per_task,
                web_analysis=web_analysis,
                llm_service=self.llm_service
            )
            # We'll skip test generation or milestone generation here.

            # 3) Generate Tasks from the LLM
            all_generated_tasks: List[Task] = []

            # We'll generate tasks for each page in domain
            for page_analysis in web_analysis.analyzed_urls:
                current_html = self._get_page_html(page_analysis)

                prompts_for_url = task_prompt_generator.generate_task_prompts_for_url(
                    task_difficulty_level=task_difficulty_level,
                    specific_url=page_analysis.page_url,
                    current_html=current_html,
                )

                # For each text prompt, create a Task object
                for task_prompt_str in prompts_for_url.task_prompts:
                    # We'll set the url to the specific page's URL
                    new_task = Task(
                        prompt=task_prompt_str,
                        url=page_analysis.page_url,
                    )
                    all_generated_tasks.append(new_task)

            # 4) Validate the tasks
            validator = TaskContextualValidator(domain_analysis=web_analysis, llm_service=self.llm_service)
            valid_tasks = validator.validate_tasks(all_generated_tasks)

            # 5) Optionally, save tasks to DB or just return them
            for task_obj in valid_tasks:
                if self.task_config.save_task_in_db:
                    self.synthetic_task_repository.save(task_obj.model_dump())
                global_tasks_output.tasks.append(task_obj)

            global_tasks_output.total_phase_time = (datetime.now() - start_time).total_seconds()
        except Exception as e:
            print(f"Tasks generation failed: {e}\n{traceback.format_exc()}")

        return global_tasks_output

    def _run_web_analysis(self) -> Optional[DomainAnalysis]:
        """
        Executes the web analysis pipeline to gather information from the target page.
        """
        analyzer = WebAnalysisPipeline(
            start_url=self.task_config.web_project.frontend_url, 
            llm_service=self.llm_service, 
            analysis_repository=self.web_analysis_repository
        )
        return analyzer.analyze(
            save_results_in_db=self.task_config.save_web_analysis_in_db,
            enable_crawl=self.task_config.enable_crawl,
        )

    @staticmethod
    def _get_page_html(page_analysis: SinglePageAnalysis) -> str:
        """
        Retrieves the HTML for the current page from analysis or HTML source.
        """
        return extract_html(page_analysis.page_url) or page_analysis.html_source
