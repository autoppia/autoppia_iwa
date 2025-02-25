import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from tests import test_container


class TestActionGeneration(unittest.TestCase):
    """
    Unit tests for validating action generation based on task configurations.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources for all tests in the class.
        """
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.web_agent: ApifiedWebAgent = test_container.web_agent()
        cls.task = cls._initialize_task()

    @staticmethod
    def _initialize_task():
        """
        Initializes and returns a Task instance with predefined task data.

        Returns:
            Task: A configured Task instance.
        """
        task_data = {
            "prompt": "Click on the 'Login' link in the header, fill credentials, and login.",
            "url": "http://localhost:8000/",
            "tests": [
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "page_view", "app_type": "jobs"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["email"]},
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "login", "app_type": "jobs"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["logout"]},
            ],
            "milestones": None,
            "web_analysis": None,
            "relevant_data": {"authorization": {"email": "employee@employee.com", "password": "employee"}},
        }

        tests = BaseTaskTest.assign_tests(task_data["tests"])

        return Task(
            prompt=task_data["prompt"],
            url=task_data["url"],
            tests=tests,
            milestones=task_data["milestones"],
            web_analysis=task_data["web_analysis"],
            relevant_data=task_data["relevant_data"],
        )

    def test_action_generation(self):
        """
        Test that actions are correctly generated from a goal and URL.
        """
        task_solution = self.web_agent.solve_task_sync(task=self.task)

        # Validate generated actions
        self.assertTrue(task_solution, "No task solution was generated.")
        self.assertTrue(task_solution.actions, "No actions were generated. The action list is empty.")

        # Debugging output (optional)
        print(f"Generated {len(task_solution.actions)} actions:")
        for idx, action in enumerate(task_solution.actions, start=1):
            print(f"{idx}: {repr(action)}")


if __name__ == "__main__":
    unittest.main()
