import asyncio
import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from tests import test_container


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
        cls.web_agent: ApifiedWebAgent = test_container.web_agent()

        cls.task = cls._initialize_task()
        cls.web_agent_id = "miner_123"

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
            "tests": [
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "page_view", "page_view_url": "/login"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["email"]},
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "login"},
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

    def test_action_generation_and_evaluation(self):
        """
        Tests whether actions are correctly generated and evaluated.
        """
        task_solution = self.web_agent.solve_task_sync(task=self.task)

        # Validate generated actions
        self.assertTrue(task_solution, "No actions were generated.")
        self.assertIsInstance(task_solution.actions, list, "Generated actions should be in a list format.")
        self.assertTrue(all(isinstance(action, BaseAction) for action in task_solution.actions), "All generated actions should be instances of BaseAction.")

        # Debugging output
        print(f"Generated {len(task_solution.actions)} actions:")
        for idx, action in enumerate(task_solution.actions, start=1):
            print(f"{idx}: {action}")

        # Evaluate the generated actions
        evaluated_solution = TaskSolution(task=self.task, actions=task_solution.actions, web_agent_id=self.web_agent_id)
        evaluator = ConcurrentEvaluator(EvaluatorConfig())
        evaluated_task = asyncio.run(evaluator.evaluate_single_task(evaluated_solution))

        # Assert evaluation result
        self.assertTrue(evaluated_task, "Task evaluation failed.")

        # Debugging output for evaluation results
        print("\n--- Evaluation Results ---")
        print(f"Final score: {evaluated_task.feedback.final_score}")


if __name__ == "__main__":
    unittest.main()
