import unittest
from typing import List

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig, TasksGenerationOutput
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects


class TestTaskGenerationPipeline(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for the TaskGenerationPipeline.

    Ensures the pipeline generates structured tasks based on the provided input.
    """

    async def asyncSetUp(self) -> None:
        """
        Set up the environment and dependencies for each test.
        """
        self.app_bootstrap = AppBootstrap()
        self.llm_service = self.app_bootstrap.container.llm_service()
        self.task_repo = self.app_bootstrap.container.synthetic_task_repository()

        self.page_url = "http://localhost:8000/"
        self.enable_crawl = False
        self.save_task_in_db = True

    async def test_task_generation_pipeline(self) -> None:
        """
        Test that the TaskGenerationPipeline produces valid structured tasks.

        This includes:
        - Verifying the task generation process does not fail.
        - Ensuring the output contains tasks.
        - Validating the structure of the generated tasks.
        """
        try:
            # Initialize demo web projects
            web_projects: List[WebProject] = await initialize_demo_webs_projects()
            self.assertGreater(len(web_projects), 0, "No demo web projects were initialized.")

            # Create task generation configuration
            task_config = TaskGenerationConfig(
                save_web_analysis_in_db=True,
                number_of_prompts_per_task=3,
            )

            # Run the task generation pipeline
            task_generator = TaskGenerationPipeline(
                web_project=web_projects[0],
                config=task_config,
                llm_service=self.llm_service,
                synthetic_task_repository=self.task_repo,
            )
            task_output: TasksGenerationOutput = await task_generator.generate()

            # Validate the output
            self.assertIsNotNone(task_output, "Task generation pipeline returned None.")
            self.assertIsNotNone(task_output.tasks, "Task generation output has no tasks.")
            self.assertIsInstance(task_output.tasks, list, "Generated tasks should be a list.")
            self.assertGreater(len(task_output.tasks), 0, "Expected at least one task to be generated.")

            # Validate the structure of each task
            for task in task_output.tasks:
                self.assertTrue(hasattr(task, "id"), "Task should have an 'id' attribute.")
                self.assertTrue(hasattr(task, "prompt"), "Task should have a 'prompts' attribute.")
                self.assertTrue(hasattr(task, "url"), "Task should have a 'url' attribute.")
                self.assertIsInstance(task.prompt, str, "Task prompts should be a list.")

            print("Generated Tasks:", task_output.tasks)

        except Exception as e:
            self.fail(f"Test failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
