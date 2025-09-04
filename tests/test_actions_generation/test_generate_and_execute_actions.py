import asyncio
import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from tests.test_di_container import TestDIContainer


class TestActionGenerationAndEvaluation(unittest.TestCase):
    """
    Unit tests for action generation and evaluation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources for the test class.
        """
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.web_agent: ApifiedWebAgent = TestDIContainer().web_agent()

        cls.task = cls._initialize_task()
        cls.web_agent_id = "miner_123"
        cls.loop = asyncio.get_event_loop()

    @staticmethod
    def _initialize_task():
        """
        Initializes and returns a Task instance with sample data.

        Returns:
            Task: A configured Task instance.
        """
        task_data = {
            "prompt": "Click on the 'Login' link in the header. Then fill the form and click on login.",
            "url": "http://localhost:8000/",
            "tests": [{"type": "FindInHtmlTest", "content": "email"}],
        }

        # Create tests from test data
        tests = [BaseTaskTest.deserialize(test) for test in task_data["tests"]]

        # Create and return a Task instance
        return Task(prompt=task_data["prompt"], url=task_data["url"], tests=tests)

    def test_action_generation_and_evaluation(self):
        """
        Tests whether actions are correctly generated and evaluated.
        """
        task_solution = self.web_agent.solve_task_sync(task=self.task)

        # Validate generated actions
        self.assertTrue(task_solution, "No actions were generated.")
        self.assertIsInstance(task_solution.actions, list, "Generated actions should be in a list format.")
        self.assertTrue(all(isinstance(action, BaseAction) for action in task_solution.actions), "All generated actions should be instances of BaseAction.")

        # Optional debugging output
        print(f"Generated {len(task_solution.actions)} actions:")
        for idx, action in enumerate(task_solution.actions, start=1):
            print(f"{idx}: {action}")

        # Evaluate the actions
        web_project = self.loop.run_until_complete(demo_web_projects)
        web_project[0].relevant_data = ({"authorization": {"email": "employee@employee.com", "password": "employee"}},)

        task_solution = TaskSolution(actions=task_solution.actions, web_agent_id=self.web_agent_id)
        evaluator = ConcurrentEvaluator(web_project[0], EvaluatorConfig())
        evaluated_task = self.loop.run_until_complete(evaluator.evaluate_single_task_solution(self.task, task_solution))

        # Assert the evaluation result
        self.assertTrue(evaluated_task, "Task evaluation failed.")

        # Optional debugging output for evaluation
        print("\n--- Evaluation Results ---")
        print(f"Final score: {evaluated_task.feedback.final_score}")

    def tearDown(self):
        self.loop.close()
        self.web_agent = None
        self.app_bootstrap = None


if __name__ == "__main__":
    unittest.main()
