import asyncio
import json
import logging
import random
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
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
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis

# Constants
ENABLE_CRAWL = False
IS_WEB_REAL = True

# Paths
DATA_DIR = Path(PROJECT_BASE_DIR.parent / "data")
TASK_OUTPUT_FILE = DATA_DIR / "GeneratedTests.jsonl"
ACTION_OUTPUT_FILE = DATA_DIR / "GeneratedTests_with_Actions.jsonl"
EVALUATION_OUTPUT_FILE = DATA_DIR / "GeneratedTests_with_Evaluation.jsonl"


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s]: %(message)s",
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def cleanup_webdriver_cache() -> None:
    """Clean up webdriver cache directories."""
    cache_paths = [
        Path.home() / ".wdm",
        Path.home() / ".cache" / "selenium",
        Path.home() / "Library" / "Caches" / "selenium",
    ]
    for path in cache_paths:
        if path.exists():
            logging.info(f"Removing cache directory: {path}")
            shutil.rmtree(path, ignore_errors=True)


async def generate_web_analysis_and_tests(url: str, task_description: str, enable_crawl: bool) -> Tuple[List[BaseTaskTest], DomainAnalysis]:
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
        return tests, web_analysis
    except Exception as e:
        logging.error(f"Failed to generate tests for URL '{url}': {e}")
        raise


async def add_actions_to_tasks(tasks_data: Dict, output_file: Path) -> None:
    """Add actions to tasks if not already present."""
    for task in tasks_data["tasks"]:
        try:
            if "actions" not in task:
                tests = BaseTaskTest.assign_tests(task["tests"])
                current_task = Task(prompt=task["prompt"], url=task["url"], tests=tests)
                task_solution = await AGENT.solve_task(task=current_task)
                task["actions"] = [action.model_dump() for action in task_solution.actions]
                logging.info(f"Added actions for task ID: {task['prompt']}")
                with output_file.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(task) + "\n")
        except Exception as e:
            logging.warning(f"Failed to generate actions for task {task['prompt']}: {e}")


async def evaluate_tasks(tasks_data: Dict, output_file: Path) -> List[EvaluationResult]:
    """Evaluate tasks and update the tasks data with the evaluation results."""
    evaluator_input = [
        TaskSolution(
            task=Task(
                prompt=task["prompt"],
                url=task["url"],
                tests=BaseTaskTest.assign_tests(task["tests"]),
                is_web_real=True,
            ),
            actions=[BaseAction.create_action(action) for action in task.get("actions", [])],
            web_agent_id=task.get("web_agent_id", generate_random_web_agent_id()),
        )
        for task in tasks_data["tasks"]
    ]
    logging.info("Starting task evaluation...")
    evaluator_config = EvaluatorConfig(save_results_in_db=True)
    evaluator = ConcurrentEvaluator(evaluator_config)
    evaluation_results = await evaluator.evaluate_all_tasks(evaluator_input)

    # Save evaluated tasks in JSONL format
    with output_file.open("w", encoding="utf-8") as f:
        for task, result in zip(tasks_data["tasks"], evaluation_results):
            task["evaluation_result"] = result.model_dump()
            f.write(json.dumps(task) + "\n")

    return evaluation_results


async def load_and_process_tasks() -> None:
    """Load tasks, process them, and save results."""
    try:
        if not TASK_OUTPUT_FILE.exists():
            logging.info("No existing task data found. Generating new tasks...")
            tasks = []
            with open(DATA_DIR / "WebVoyager_data.jsonl", "r") as f:
                for line in f:
                    try:
                        tasks.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping invalid JSON line: {e}")
            with open(DATA_DIR / "WebVoyagerImpossibleTasks.json", "r") as f:
                impossible_tasks = set(json.load(f))
            tasks = [TaskData(**task) for task in tasks if task["id"] not in impossible_tasks]
            random.shuffle(tasks)
            tasks_to_generate = tasks[:1]  # TODO: Limit for demo purposes
            tests_generated_tasks: List[Task] = []
            for task in tasks_to_generate:
                task_tests, task_web_analysis = await generate_web_analysis_and_tests(task.web, task.ques, ENABLE_CRAWL)
                task_obj = Task(url=task.web, prompt=task.ques, tests=task_tests, web_analysis=task_web_analysis, milestones=[])
                tests_generated_tasks.append(task_obj)
                with TASK_OUTPUT_FILE.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(task_obj.nested_model_dump()) + "\n")
                logging.info(f"Generated tests saved to: {TASK_OUTPUT_FILE}")
        else:
            with TASK_OUTPUT_FILE.open(encoding='utf-8') as f:
                tasks_data = {"tasks": [json.loads(line) for line in f]}
            await add_actions_to_tasks(tasks_data, ACTION_OUTPUT_FILE)
            await evaluate_tasks(tasks_data, EVALUATION_OUTPUT_FILE)
    except Exception as e:
        logging.error(f"Error processing tasks: {e}", exc_info=True)


async def main() -> None:
    """Main function."""

    cleanup_webdriver_cache()
    await load_and_process_tasks()
    logging.info("Shutting down...")


if __name__ == "__main__":
    setup_logging()
    app_bootstrap = AppBootstrap()
    AGENT = ApifiedWebAgent(name=AGENT_NAME, host=AGENT_HOST, port=AGENT_PORT)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
