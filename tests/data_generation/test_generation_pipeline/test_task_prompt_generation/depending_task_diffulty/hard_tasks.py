import asyncio
import json
import logging
import unittest
from pathlib import Path
from typing import List

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskDifficultyLevel, TaskGenerationConfig
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED
from tests import test_container


class TaskGenerationByHardDifficultyTest(unittest.TestCase):
    logger = logging.getLogger("TaskGenerationByEasyDifficultyTest")
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.INFO)

    @classmethod
    def setUpClass(cls):
        """
        Initialize dependencies and prepare output directory.
        """
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.web_agent: ApifiedWebAgent = test_container.web_agent()
        cls.domain = "localhost:8000"
        cls.start_url = f"http://{cls.domain}/"
        cls.difficulty_level = TaskDifficultyLevel.HARD
        cls.file_name = "hard_tasks.json"
        cls.output_dir = Path(__file__).resolve().parents[4] / "sample_tasks_data_files"
        cls.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, folder_name: str) -> Path:
        return self.output_dir / folder_name / self.file_name

    def _save_tasks(self, tasks: dict, folder_name: str):
        """
        Save tasks to a JSON file in the specified folder.

        Args:
            tasks (dict): The task results to save.
            folder_name (str): Name of the folder where the file will be saved.
        """
        file_path = self._get_file_path(folder_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(tasks, file, ensure_ascii=False, indent=4)
            self.logger.info(f"Tasks successfully saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save tasks to {file_path}: {e}")
            raise

    def _load_tasks(self, folder_name: str) -> dict:
        """
        Load tasks from a JSON file in the specified folder.
        """
        file_path = self._get_file_path(folder_name)
        if not file_path.exists():
            self.logger.info(f"File not found: {file_path}. Tasks will be generated.")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                tasks = json.load(file)
            self.logger.info(f"Loaded {len(tasks)} tasks for difficulty '{self.difficulty_level}' from {file_path}")
            return tasks
        except Exception as e:
            self.logger.error(f"Failed to load tasks from {file_path}: {e}")
            return {}

    def _generate_tasks(self, include_actions: bool = False, include_evaluation: bool = False) -> dict:
        """
        Generate tasks and optionally include actions and evaluations.

        Args:
            include_actions (bool): Whether to generate actions for tasks.
            include_evaluation (bool): Whether to evaluate tasks with generated actions.

        Returns:
            dict: The generated tasks and additional data if requested.
        """
        tasks_data = self._load_tasks("with_actions") or self._load_tasks("tasks_only")
        save_results = False

        if not tasks_data:
            web_project = WebProject(
                backend_url=self.start_url,
                frontend_url=self.start_url,
                name="jobs",
                events=EVENTS_ALLOWED,
            )
            task_input = TaskGenerationConfig()
            task_generator = TaskGenerationPipeline(config=task_input, web_project=web_project, llm_service=self.llm_service)
            tasks_data = asyncio.run(task_generator.generate()).to_dict()
            save_results = True

        if include_actions:
            self._add_actions_to_tasks(tasks_data)
            save_results = True

        if include_evaluation:
            tasks_data = self._evaluate_tasks(tasks_data)
            save_results = True

        if save_results:
            folder_name = self._determine_output_folder(include_actions, include_evaluation)
            self._save_tasks(tasks_data, folder_name)

        return tasks_data

    def _add_actions_to_tasks(self, tasks_data: dict):
        """
        Add actions to tasks if not already present.

        Args:
            tasks_data (dict): Tasks data dictionary.
        """
        for task in tasks_data["tasks"]:
            try:
                if "actions" not in task:
                    tests = BaseTaskTest.assign_tests(task["tests"])
                    current_task = Task(prompt=task["prompt"], url=task["url"], tests=tests)
                    task_solution = self.web_agent.solve_task_sync(task=current_task)
                    task["actions"] = [action.model_dump() for action in task_solution.actions]
            except Exception as e:
                self.logger.warning(f"Failed to generate actions for task {task['id']}: {e}")

    def _evaluate_tasks(self, tasks_data: dict) -> List[EvaluationResult]:
        """
        Evaluate tasks and update the tasks data with the evaluation results.

        Args:
            tasks_data (dict): Tasks data dictionary.
        """

        evaluator_input = []

        for task in tasks_data["tasks"]:
            actions = []
            if task.get("actions", ""):
                for action in task["actions"]:
                    try:
                        created_action = BaseAction.create_action(action)
                        if created_action:
                            actions.append(created_action)
                        else:
                            self.logger.warning(f"Action could not be created: {action}")
                    except Exception as e:
                        self.logger.error(f"Error creating action: {action}. Exception: {e}")

            task_solution = TaskSolution(
                actions=actions,
                web_agent_id=task.get("web_agent_id", generate_random_web_agent_id()),
            )
            evaluator_input.append(task_solution)

        evaluator_config = EvaluatorConfig(save_results_in_db=True)
        evaluator = ConcurrentEvaluator(evaluator_config)
        evaluation_result = asyncio.run(evaluator.evaluate_task_solutions(evaluator_input))
        return [result.model_dump() for result in evaluation_result]

    @staticmethod
    def _determine_output_folder(include_actions: bool, include_evaluation: bool) -> str:
        if include_actions and include_evaluation:
            return "with_actions_and_evaluation"
        if include_actions:
            return "with_actions"
        return "tasks_only"

    def _test_task_generation(self, include_actions: bool, include_evaluation: bool):
        """
        Generic test function for task generation with different options.

        Args:
            include_actions (bool): Whether to include actions in the test.
            include_evaluation (bool): Whether to include evaluations in the test.
        """
        result = self._generate_tasks(include_actions, include_evaluation)
        if not include_evaluation:
            self.assertIn("tasks", result, "Generated result does not contain tasks.")
            self.assertGreater(len(result["tasks"]), 0, "No tasks were generated.")

            if include_actions:
                self.assertIn("actions", result["tasks"][0], "Actions were not generated for tasks.")

    # Hard Level Tests
    def test_hard_tasks_generation_only(self):
        self._test_task_generation(include_actions=False, include_evaluation=False)

    def test_hard_tasks_generation_with_actions(self):
        self._test_task_generation(include_actions=True, include_evaluation=False)

    def test_hard_tasks_generation_with_actions_and_evaluation(self):
        self._test_task_generation(include_actions=True, include_evaluation=True)


if __name__ == "__main__":
    unittest.main()
