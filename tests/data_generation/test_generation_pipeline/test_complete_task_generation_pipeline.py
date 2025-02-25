import asyncio
import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import TaskGenerationConfig, WebProject
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED


class TestTaskGenerationPipeline(unittest.TestCase):
    """
    Unit tests for the TaskGenerationPipeline.

    Ensures the pipeline generates structured tasks based on the provided input.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the environment and dependencies once for all tests."""
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.task_repo = cls.app_bootstrap.container.synthetic_task_repository()
        cls.analysis_repo = cls.app_bootstrap.container.analysis_repository()

        cls.web_project = WebProject(
            backend_url="http://localhost:8000/",
            frontend_url="http://localhost:8000/",
            name="jobs",
            events_to_check=EVENTS_ALLOWED,
        )

        cls.task_config = TaskGenerationConfig(web_project=cls.web_project, save_web_analysis_in_db=True, save_task_in_db=True)

        cls.loop = asyncio.get_event_loop()

    def _run_async(self, coro):
        """Helper function to run async functions inside synchronous test methods."""
        return self.loop.run_until_complete(coro)

    def test_task_generation_pipeline(self) -> None:
        """
        Test that the TaskGenerationPipeline produces valid structured tasks.

        Validates:
        - The task generation process does not fail.
        - The output contains at least one task.
        """

        # Run the task generation pipeline
        task_generator = TaskGenerationPipeline(config=self.task_config, llm_service=self.llm_service, synthetic_task_repository=self.task_repo, web_analysis_repository=self.analysis_repo)

        task_output = self._run_async(task_generator.generate())

        # Validate the output
        self.assertIsNotNone(task_output, "Task generation pipeline returned None.")
        self.assertIsNotNone(task_output.tasks, "Task generation output has no tasks.")
        self.assertIsInstance(task_output.tasks, list, "Generated tasks should be a list.")
        self.assertGreater(len(task_output.tasks), 0, "Expected at least one task to be generated.")

        print(f"Generated {len(task_output.tasks)} tasks: {task_output.tasks}")

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up resources after tests."""
        cls.loop.close()


if __name__ == "__main__":
    unittest.main()
