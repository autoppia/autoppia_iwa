import asyncio
import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.web_utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import TaskSolution


class TestActionExecution(unittest.TestCase):
    """
    Unit test for evaluating task execution and action processing.
    """

    @classmethod
    def setUpClass(cls):
        """
        Class-level setup that initializes the application bootstrap and task/action data.
        """
        cls.app_bootstrap = AppBootstrap()
        task_data = {
            "prompt": "Click on the \"Login\" link in the header. Then fill the form with email:employee@employee.com and password:employee and click on login",
            "url": "http://localhost:8000/",
            "tests": [
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "page_view"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["login"]},
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "login"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["logout"]},
            ],
            "milestones": None,
            "web_analysis": None,
        }
        cls.task = Task(
            prompt=task_data["prompt"],
            url=task_data["url"],
            tests=BaseTaskTest.assign_tests(task_data["tests"]),
            milestones=task_data["milestones"],
            web_analysis=task_data["web_analysis"],
        )
        cls.accurate_actions_data = {
            "actions": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8000/"}, "type": "NavigateAction", "url": "http://localhost:8000/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "href", "value": "/login"}, "type": "ClickAction"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
                {"selector": {"type": "attributeValueSelector", "attribute": "class", "value": "btn-outline-white-primary"}, "type": "ClickAction"},
            ]
        }
        cls.half_accurate_actions_data = {
            "actions": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8000/"}, "type": "NavigateAction", "url": "http://localhost:8000/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "href", "value": "/login"}, "type": "ClickAction"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
            ]
        }
        cls.wrong_actions_data = {
            "actions": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8000/"}, "type": "NavigateAction", "url": "http://localhost:8000/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
                {"selector": {"type": "attributeValueSelector", "attribute": "class", "value": "btn-outline-white"}, "type": "ClickAction"},
            ]
        }

    def evaluate(self, actions):
        # Prepare evaluation input
        evaluator_input = TaskSolution(task=self.task, actions=actions, web_agent_id=generate_random_web_agent_id())
        evaluator_config = EvaluatorConfig(save_results_in_db=False)

        evaluator = ConcurrentEvaluator(evaluator_config)
        evaluation_result = asyncio.run(evaluator.evaluate_single_task(evaluator_input))

        # Display results
        print("\n--- Evaluation Results ---")
        # print(evaluation_result)
        self.assertTrue(evaluation_result, "Task evaluation failed.")
        print(f"Final score: {evaluation_result.final_score}")

    def test_accurate_task_evaluation(self):
        actions = [BaseAction.create_action(action) for action in self.accurate_actions_data["actions"]]
        self.evaluate(actions)

    def test_half_accurate_task_evaluation(self):
        actions = [BaseAction.create_action(action) for action in self.half_accurate_actions_data["actions"]]
        self.evaluate(actions)

    def test_wrong_task_evaluation(self):
        actions = [BaseAction.create_action(action) for action in self.wrong_actions_data["actions"]]
        self.evaluate(actions)


if __name__ == "__main__":
    unittest.main()
