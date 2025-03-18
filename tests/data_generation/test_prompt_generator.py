import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.local_task_generation import LocalTaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects

START_URL = "http://localhost:8000/login"
RELEVANT_DATA = {"authorization": {"email": "employee@employee.com", "password": "employee"}}


class TestTaskPromptGenerator(unittest.IsolatedAsyncioTestCase):
    """Unit tests for TaskPromptGenerator."""

    async def asyncSetUp(self):
        """Set up test dependencies for each test."""
        self.app_bootstrap = AppBootstrap()
        self.llm_service = self.app_bootstrap.container.llm_service()

    async def test_generate_prompts_for_url(self):
        """Test the generation of prompts for a URL."""
        try:
            # Initialize demo web project and set relevant data
            web_project = await initialize_demo_webs_projects(demo_web_projects)
            web_project[0].relevant_data = RELEVANT_DATA

            # Create task generator
            generator = LocalTaskGenerationPipeline(web_project[0], llm_service=self.llm_service)

            # Generate tasks
            tasks = await generator.generate_per_url(START_URL)

            # Assertions
            self.assertIsNotNone(tasks, "Tasks should not be None.")
            self.assertIsInstance(tasks, list, "Tasks should be a list.")
            self.assertTrue(all(isinstance(task, Task) for task in tasks), "All items in tasks should be instances of Task.")
            self.assertTrue(all(hasattr(task, "prompt") for task in tasks), "All tasks should have a 'prompts' attribute.")
            self.assertTrue(all(hasattr(task, "url") for task in tasks), "All tasks should have a 'url' attribute.")

            print(f"Generated Tasks: {tasks}")

        except Exception as e:
            self.fail(f"Test failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
