import asyncio
import json
import logging
import random
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

from pydantic import BaseModel

from autoppia_iwa.config.config import AGENT_HOST, AGENT_NAME, AGENT_PORT, PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.task_tests_generator import TaskTestGenerator
from autoppia_iwa.src.data_generation.domain.classes import Task, WebProject
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest
from autoppia_iwa.src.evaluation.classes import EvaluationResult
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator, EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.INFO, handlers=[logging.StreamHandler()])


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def load_jsonl_file(file_path: Path) -> List[Dict]:
    """Load tasks from a JSONL file."""
    if not file_path.exists():
        logging.warning(f"File {file_path} not found.")
        return []

    tasks = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError as e:
                logging.warning(f"Skipping invalid JSON line in {file_path}: {e}")
    return tasks


async def generate_tests(url: str, task_description: str, enable_crawl: bool) -> List[BaseTaskTest]:
    """Generate task-based tests for a web project."""
    logging.info(f"Starting web analysis for URL: {url}")
    try:
        web_analysis_pipeline = WebAnalysisPipeline(start_url=url)
        web_analysis = await web_analysis_pipeline.analyze(enable_crawl=enable_crawl, save_results_in_db=True)
        web_project = WebProject(
            backend_url=url,
            frontend_url=url,
            name=urlparse(url).netloc,
            events_to_check=[],
            is_real_web=IS_WEB_REAL,
        )
        task_test_generator = TaskTestGenerator(web_project=web_project, web_analysis=web_analysis)
        tests = await task_test_generator.generate_task_tests(task_description, url)
        logging.info(f"Generated {len(tests)} tests for URL: {url}")
        return tests
    except Exception as e:
        logging.error(f"Failed to generate tests for URL '{url}': {e}")
        raise


async def add_actions_to_tasks(tasks: List[Dict], output_file: Path) -> List[Dict]:
    """Add actions to tasks if not already present."""
    updated_tasks = []
    for task in tasks:
        try:
            if "actions" not in task:
                tests = BaseTaskTest.assign_tests(task["tests"])
                current_task = Task(prompt=task["prompt"], url=task["url"], tests=tests, is_web_real=IS_WEB_REAL)
                task_solution = await AGENT.solve_task(task=current_task)
                task["actions"] = [action.model_dump() for action in task_solution.actions]
                logging.info(f"Added actions for task ID: {task['prompt']}")
                updated_tasks.append(task)
                with output_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(task) + "\n")

        except Exception as e:
            logging.warning(f"Failed to generate actions for task {task['prompt']}: {e}")
    return updated_tasks


async def evaluate_tasks(tasks_data: List[Dict], output_file: Path) -> List[EvaluationResult]:
    """Evaluate tasks and update the tasks data with the evaluation results."""
    evaluator_input = [
        TaskSolution(
            task=Task(
                prompt=task["prompt"],
                url=task["url"],
                tests=BaseTaskTest.assign_tests(task["tests"]),
                is_web_real=IS_WEB_REAL,
            ),
            actions=[BaseAction.create_action(action) for action in task.get("actions", [])],
            web_agent_id=task.get("web_agent_id", generate_random_web_agent_id()),
        )
        for task in tasks_data
    ]
    logging.info("Starting task evaluation...")
    evaluator_config = EvaluatorConfig(save_results_in_db=True)
    evaluator = ConcurrentEvaluator(evaluator_config)
    evaluation_results = await evaluator.evaluate_all_tasks(evaluator_input)

    # Save evaluated tasks in JSONL format
    with output_file.open("w", encoding="utf-8") as f:
        for result in evaluation_results:
            f.write(json.dumps(result.model_dump()) + "\n")

    return evaluation_results


async def load_and_process_tasks() -> None:
    """Load tasks, process them, and save results."""
    try:
        if not TASK_OUTPUT_FILE.exists():
            logging.info("No existing task data found. Generating new tasks...")
            original_tasks = load_jsonl_file(DATA_DIR / "WebVoyager_data.jsonl")
            impossible_tasks_ids = load_jsonl_file(DATA_DIR / "WebVoyagerImpossibleTasks.json")
            tasks = [TaskData(**task) for task in original_tasks if task["id"] not in impossible_tasks_ids]

            tasks_to_generate = tasks[:3]  # TODO: Limit for demo purposes
            # tasks_to_generate=random.sample(tasks, NUM_OF_RANDOM_TASKS_TO_SAMPLE)
            logging.info(f"Loaded {len(tasks)} tasks and generating tests for {len(tasks_to_generate)} tasks")

            for task in tasks_to_generate:
                task_tests = await generate_tests(task.web, task.ques, ENABLE_CRAWL)
                task_obj = Task(url=task.web, prompt=task.ques, tests=task_tests, milestones=[], is_web_real=IS_WEB_REAL)
                with TASK_OUTPUT_FILE.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(task_obj.nested_model_dump()) + "\n")
                logging.info(f"Generated tests saved to: {TASK_OUTPUT_FILE}")
                logging.info("Re-run the script to start the actions generation and evaluation.")
        else:
            existing_tasks = load_jsonl_file(TASK_OUTPUT_FILE)
            if not existing_tasks:
                logging.error("No tasks loaded. Exiting...")
                return

            if len(existing_tasks) > 3:
                logging.warning("More than three tasks loaded. Randomly selecting 3 tasks.")
                existing_tasks = random.sample(existing_tasks, NUM_OF_RANDOM_TASKS_TO_SAMPLE)

            actioned_tasks = load_jsonl_file(ACTION_OUTPUT_FILE)
            actioned_prompts = {t["prompt"] for t in actioned_tasks if t.get("actions")}
            tasks_to_process = [t for t in existing_tasks if t["prompt"] not in actioned_prompts]
            logging.info(f"Found {len(tasks_to_process)} tasks that need actions.")

            evaluation_ready_tasks = await add_actions_to_tasks(tasks_to_process, ACTION_OUTPUT_FILE) if tasks_to_process else actioned_tasks

            await evaluate_tasks(evaluation_ready_tasks, EVALUATION_OUTPUT_FILE)

    except Exception as e:
        logging.error(f"Error processing tasks: {e}", exc_info=True)


if __name__ == "__main__":
    setup_logging()
    app_bootstrap = AppBootstrap()

    # Constants
    ENABLE_CRAWL = False
    IS_WEB_REAL = True
    NUM_OF_RANDOM_TASKS_TO_SAMPLE = 3

    # Paths
    DATA_DIR = Path(PROJECT_BASE_DIR.parent / "data")
    TASK_OUTPUT_FILE = DATA_DIR / "GeneratedTests.jsonl"
    ACTION_OUTPUT_FILE = DATA_DIR / "GeneratedTests_with_Actions.jsonl"
    EVALUATION_OUTPUT_FILE = DATA_DIR / "GeneratedTests_with_Evaluation.jsonl"

    # Agent
    AGENT = ApifiedWebAgent(name=AGENT_NAME, host=AGENT_HOST, port=AGENT_PORT, timeout=120)

    try:
        asyncio.run(load_and_process_tasks())
        logging.info("Shutting down...")
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
