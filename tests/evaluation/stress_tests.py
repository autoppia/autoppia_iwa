import asyncio
import json
import logging
import time
import unittest
from pathlib import Path
from typing import List

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskDifficultyLevel
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.web_utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.classes import TaskSolution

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class BaseEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize test environment and configurations"""
        cls.app_bootstrap = AppBootstrap()
        cls.domain = "localhost:8000"
        cls.start_url = "http://localhost:8000/"
        cls.difficulty_level = TaskDifficultyLevel.EASY
        cls.output_dir = Path(__file__).resolve().parent
        cls.output_dir.mkdir(parents=True, exist_ok=True)
        cls.save_results_in_db = False
        cls.num_of_tasks_to_evaluate = 256

    @staticmethod
    def _save_tasks_to_file(tasks: dict, folder_name: str, output_dir: Path, file_name: str):
        """Save tasks to a JSON file in the specified folder."""
        file_path = output_dir / folder_name / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with file_path.open("w", encoding="utf-8") as file:
                json.dump(tasks, file, ensure_ascii=False, indent=4)
            logging.info(f"Tasks successfully saved to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save tasks to {file_path}: {e}")
            raise

    @staticmethod
    def _load_tasks_from_file(file_name: str, output_dir: Path) -> dict:
        """Load tasks from a JSON file in the specified folder."""
        file_path = output_dir / file_name
        if not file_path.exists():
            logging.warning(f"File not found: {file_path}. Tasks will be generated.")
            return {"tasks": []}
        try:
            with file_path.open("r", encoding="utf-8") as file:
                tasks = json.load(file)
            logging.info(f"Loaded {len(tasks.get('tasks', []))} tasks from {file_path}")
            return tasks
        except Exception as e:
            logging.error(f"Failed to load tasks from {file_path}: {e}")
            return {"tasks": []}

    def _create_base_task_solution(self) -> TaskSolution:
        """Create a base task solution for testing."""
        task_data = {
            "prompt": "Click on the \"Login\" link in the header. Then fill the form with email:admin@jobsapp.com and password:admin123 and click on login",
            "url": "http://localhost:8000/",
            "specifications": {
                "viewport_width": 1920,
                "viewport_height": 1080,
                "screen_width": 1920,
                "screen_height": 1080,
                "device_pixel_ratio": 1.0,
                "scroll_x": 0,
                "scroll_y": 0,
                "browser_x": 0,
                "browser_y": 0,
            },
            "tests": [
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "page_view"},
                {"description": "Find in the current HTML some of the words in the list", "test_type": "frontend", "keywords": ["login"]},
                {"description": "Check if the backend emitted the specified event", "test_type": "backend", "event_name": "login"},
            ],
            "actions": [
                {"type": "NavigateAction", "url": "http://localhost:8000/", "go_back": False, "go_forward": False}
                # ... remaining actions ...
            ],
        }

        return TaskSolution(
            task=Task(
                prompt=task_data["prompt"],
                url=task_data["url"],
                tests=BaseTaskTest.assign_tests(task_data["tests"]),
            ),
            actions=[BaseAction.create_action(action) for action in task_data["actions"]],
            web_agent_id=generate_random_web_agent_id(),
        )

    def _get_task_solutions(self, num_tasks: int, input_file: str = None) -> List[TaskSolution]:
        """Get task solutions either from file or generate them."""
        if input_file:
            tasks_data = self._load_tasks_from_file(input_file, self.output_dir)
            tasks = tasks_data.get("tasks", [])

            if len(tasks) > num_tasks:
                import random

                tasks = random.sample(tasks, num_tasks)

            return [
                TaskSolution(
                    task=Task(
                        prompt=task["prompt"],
                        url=task["url"],
                        tests=BaseTaskTest.assign_tests(task["tests"]),
                    ),
                    actions=[BaseAction.create_action(action) for action in task.get("actions", [])],
                    web_agent_id=task.get("web_agent_id", generate_random_web_agent_id()),
                )
                for task in tasks
            ]
        else:
            # Generate base tasks if no file is provided
            return [self._create_base_task_solution() for _ in range(num_tasks)]

    async def evaluate_tasks(self, num_tasks: int, enable_grouping_tasks: bool = True, input_file: str = None, output_file: str = None) -> float:
        """Evaluate tasks with optional file loading and saving."""
        start_time = time.time()

        evaluator_input = self._get_task_solutions(num_tasks, input_file)

        evaluator_config = EvaluatorConfig(save_results_in_db=self.save_results_in_db, enable_grouping_tasks=enable_grouping_tasks)

        evaluator = ConcurrentEvaluator(evaluator_config)
        evaluated_tasks = await evaluator.evaluate_all_tasks(evaluator_input)

        if output_file and self.save_results_in_db:
            tasks_data = {"tasks": [task.model_dump() for task in evaluated_tasks]}
            self._save_tasks_to_file(tasks_data, "evaluation_results", self.output_dir, output_file)

        elapsed_time = time.time() - start_time
        logging.info(f"Tasks evaluated: {len(evaluated_tasks)} / {num_tasks} in {elapsed_time:.2f} seconds ")

        return elapsed_time


class GroupedEvaluationTest(BaseEvaluationTest):
    def test_evaluation_with_grouping(self):
        """Test task evaluation with grouping enabled"""
        elapsed_time = asyncio.run(
            self.evaluate_tasks(
                num_tasks=self.num_of_tasks_to_evaluate,
                enable_grouping_tasks=True,
            )
        )
        logging.info(f"Grouped evaluation completed in {elapsed_time:.2f} seconds")


class NonGroupedEvaluationTest(BaseEvaluationTest):
    def test_evaluation_without_grouping(self):
        """Test task evaluation with grouping disabled"""
        elapsed_time = asyncio.run(
            self.evaluate_tasks(
                num_tasks=self.num_of_tasks_to_evaluate,
                enable_grouping_tasks=False,
            )
        )
        logging.info(f"Non-grouped evaluation completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    # Run all tests
    unittest.main()

    # Run only grouped tests
    # suite = unittest.TestLoader().loadTestsFromTestCase(GroupedEvaluationTest)
    # unittest.TextTestRunner().run(suite)

    # Run only non-grouped tests
    # suite = unittest.TestLoader().loadTestsFromTestCase(NonGroupedEvaluationTest)
    # unittest.TextTestRunner().run(suite)
