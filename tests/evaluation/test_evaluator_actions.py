import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import TaskSolution


class TestActionExecution(unittest.IsolatedAsyncioTestCase):
    """
    Unit test for evaluating task execution and action processing.
    """

    async def asyncSetUp(self):
        """
        Class-level setup that initializes the application bootstrap and task/action data.
        """
        self.app_bootstrap = AppBootstrap()
        self.task = self.create_task()
        self.actions_data = self.get_action_data()
        self.web_project = (await initialize_demo_webs_projects(demo_web_projects))[0]

    def create_task(self):
        """Creates a Task instance with predefined test cases."""
        task_data = {
            "prompt": "Click on the 'Login' link in the header. Then fill the form with email: employee@employee.com and password: employee, and click on login.",
            "url": "http://localhost:8001/",
            "tests": [
                # {"type": "JudgeBaseOnHTML", "success_criteria": "The login must be completed."},
                # {"type": "FindInHtmlTest", "content": "login"},
                {"type": "JudgeBaseOnScreenshot", "success_criteria": "The login must be completed."},
            ],
        }
        return Task(
            prompt=task_data["prompt"],
            url=task_data["url"],
            tests=[BaseTaskTest.deserialize(test) for test in task_data["tests"]],
        )

    def get_action_data(self):
        """Stores different accuracy levels of actions for testing."""
        return {
            "accurate": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8001/"}, "type": "NavigateAction", "url": "http://localhost:8001/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "href", "value": "/login"}, "type": "ClickAction"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
                {"selector": {"type": "attributeValueSelector", "attribute": "class", "value": "btn-outline-white-primary"}, "type": "ClickAction"},
            ],
            "half_accurate": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8001/"}, "type": "NavigateAction", "url": "http://localhost:8001/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "href", "value": "/login"}, "type": "ClickAction"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
            ],
            "wrong": [
                {"selector": {"type": "attributeValueSelector", "attribute": "url", "value": "http://localhost:8001/"}, "type": "NavigateAction", "url": "http://localhost:8001/"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_email"}, "type": "TypeAction", "text": "employee@employee.com"},
                {"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "id_password"}, "type": "TypeAction", "text": "employee"},
                {"selector": {"type": "attributeValueSelector", "attribute": "class", "value": "btn-outline-white"}, "type": "ClickAction"},
            ],
        }

    async def asyncTearDown(self):
        """Clean up resources if needed."""
        del self.app_bootstrap
        del self.task
        del self.actions_data
        del self.web_project

    async def evaluate(self, action_type):
        """
        Evaluates the given action dataset type.
        """
        actions = [BaseAction.create_action(action) for action in self.actions_data[action_type]]
        evaluator_input = TaskSolution(task_id=self.task.id, actions=actions, web_agent_id=generate_random_web_agent_id())
        evaluator_config = EvaluatorConfig(save_results_in_db=False)
        evaluator = ConcurrentEvaluator(self.web_project, evaluator_config)

        evaluation_result = await evaluator.evaluate_single_task_solution(self.task, evaluator_input)

        # Display results
        print(f"\n--- Evaluation Results for {action_type.upper()} ---")
        print(f"Final score: {evaluation_result.final_score}")
        self.assertTrue(evaluation_result, f"Task evaluation failed for {action_type}.")

    async def test_accurate_task_evaluation(self):
        """Test evaluation with correct actions."""
        await self.evaluate("accurate")

    async def test_half_accurate_task_evaluation(self):
        """Test evaluation with partially correct actions."""
        await self.evaluate("half_accurate")

    async def test_wrong_task_evaluation(self):
        """Test evaluation with incorrect actions."""
        await self.evaluate("wrong")


if __name__ == "__main__":
    unittest.main()
