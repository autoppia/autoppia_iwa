import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

NUM_OF_URLS: int = 1
PROMPTS_PER_URL: int = 5
RANDOM_URLS: bool = False


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
            web_projects: list[WebProject] = await initialize_demo_webs_projects(demo_web_projects)
            self.assertGreater(len(web_projects), 0, "No demo web projects were initialized.")

            # Create task generation configuration
            task_config = TaskGenerationConfig(
                num_of_urls=NUM_OF_URLS,
                prompts_per_url=PROMPTS_PER_URL,
                random_urls=RANDOM_URLS,
                generate_local_tasks=True,
                generate_global_tasks=False,
            )

            # Run the task generation pipeline
            task_generator = TaskGenerationPipeline(
                web_project=web_projects[0],
                config=task_config,
                llm_service=self.llm_service,
                synthetic_task_repository=self.task_repo,
            )
            task_output: list[Task] = await task_generator.generate()

            # Validate the output
            self.assertIsNotNone(task_output, "Task generation pipeline returned None.")
            self.assertIsInstance(task_output, list, "Generated tasks should be a list.")
            self.assertGreater(len(task_output), 0, "Expected at least one task to be generated.")

            # Validate the structure of each task
            for task in task_output:
                self.assertTrue(hasattr(task, "id"), "Task should have an 'id' attribute.")
                self.assertTrue(hasattr(task, "prompt"), "Task should have a 'prompts' attribute.")
                self.assertTrue(hasattr(task, "url"), "Task should have a 'url' attribute.")
                self.assertIsInstance(task.prompt, str, "Task prompts should be a list.")

            print("Generated Tasks:", task_output)

        except Exception as e:
            self.fail(f"Test failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
