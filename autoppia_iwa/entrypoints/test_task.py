import asyncio
import base64
import datetime
import json
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution

# ==============
# CONFIGURATIONS
# ==============

PROJECT_ID = "autocalendar"
USE_CASE = "EVENT_REMOVE_REMINDER"
PROMPT_CONTENT = """
Please remove the reminder from the event where the time in minutes is greater than 1435. If it does not exist, add it first and then remove it.
"""
EVENT_CRITERIA = {"minutes": {"operator": "greater_than", "value": 1435}}


@dataclass
class PromptTestConfig:
    project_id: str
    use_case: str
    prompt_content: str
    event_criteria: dict | None = None
    agent_host: str = "127.0.0.1"
    agent_port: int = 5050
    agent_timeout: int = 180
    save_output: bool = True

    @property
    def output_dir(self) -> Path:
        return PROJECT_BASE_DIR / "prompt_test_output"


CONFIG = PromptTestConfig(
    project_id=PROJECT_ID,
    use_case=USE_CASE,
    prompt_content=textwrap.dedent(PROMPT_CONTENT),
    event_criteria=EVENT_CRITERIA,
)


def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _write_file_sync(path: Path, data: Any, is_binary: bool = False) -> None:
    """Synchronous helper to write file."""
    path.parent.mkdir(exist_ok=True, parents=True)
    with open(path, "wb" if is_binary else "w", encoding="utf-8" if not is_binary else None) as f:
        if is_binary:
            f.write(data)
        else:
            json.dump(data, f, indent=2)


async def save_file(path: Path, data: Any, is_binary: bool = False) -> None:
    """Save file asynchronously."""
    # Use async file I/O to avoid blocking event loop
    await asyncio.to_thread(_write_file_sync, path, data, is_binary)
    logger.info(f"Saved file: {path}")


async def save_gif(b64: str, path: Path) -> None:
    await save_file(path, base64.b64decode(b64), is_binary=True)


def generate_custom_task(project, use_case_name: str, prompt_content: str) -> Task | None:
    """Generate a task with custom prompt content."""
    use_case = next((uc for uc in project.use_cases if uc.name.lower() == use_case_name.lower()), None)
    if not use_case:
        logger.error(f"Use case '{use_case_name}' not found in project '{project.name}'")
        return None
    test_def = {
        "type": "CheckEventTest",
        "event_name": use_case_name,
        "event_criteria": CONFIG.event_criteria or {},
    }
    return Task(use_case=use_case, prompt=prompt_content, url=project.frontend_url, tests=[test_def])


async def run_prompt_test():
    """Run a test with the custom prompt content."""
    AppBootstrap()
    setup_logging("prompt_test.log")
    timing = TimingMetrics()
    timestamp = get_timestamp()
    output_dir = CONFIG.output_dir
    output_dir.mkdir(exist_ok=True)

    logger.info(f"Using prompt content:\n{'-' * 40}\n{CONFIG.prompt_content}\n{'-' * 40}")

    project = next((p for p in demo_web_projects if p.id.lower() == CONFIG.project_id.lower()), None)
    if not project:
        logger.error(f"Project '{CONFIG.project_id}' not found")
        return

    task = generate_custom_task(project, CONFIG.use_case, CONFIG.prompt_content)
    if not task:
        logger.error("Failed to generate task")
        return

    logger.info(f"Task generated with ID: {task.id}")
    logger.info(f"Testing prompt with project '{project.name}' and use case '{CONFIG.use_case}'")

    result_data = {
        "timestamp": timestamp,
        "task_id": task.id,
        "project_name": project.name,
        "use_case": CONFIG.use_case,
        "prompt": CONFIG.prompt_content,
        "tests": [t.model_dump() for t in task.tests],
    }

    agent = ApifiedOneShotWebAgent(id="1", name="TestAgent", host=CONFIG.agent_host, port=CONFIG.agent_port, timeout=CONFIG.agent_timeout)
    task.should_record = CONFIG.save_output
    backend = BackendDemoWebService(project)
    await backend.reset_database(web_agent_id=agent.id)

    try:
        logger.info(f"Starting task execution with agent {agent.name}...")
        timing.start()
        # Send task WITH placeholders - agent should return actions with placeholders
        solution = await agent.solve_task(task)
        timing.end()
        execution_time = timing.get_total_time()

        task_solution = TaskSolution(task_id=task.id, actions=solution.actions or [], web_agent_id=agent.id)
        # Replace credential placeholders in actions BEFORE evaluation
        task_solution.replace_credentials(agent.id)
        # Normalize any embedded agent IDs inside actions if needed
        task_solution.actions = task_solution.replace_web_agent_id()

        logger.info(f"Task completed in {execution_time:.2f} seconds")
        logger.info(f"Number of actions: {len(task_solution.actions)}")

        result_data.update(
            {
                "execution_time": execution_time,
                "num_actions": len(task_solution.actions),
                "actions": [a.model_dump() for a in task_solution.actions],
            }
        )

        logger.info("Evaluating solution...")
        evaluator = ConcurrentEvaluator(project, EvaluatorConfig())
        eval_result = await evaluator.evaluate_single_task_solution(task, task_solution)

        if eval_result:
            logger.info(f"Evaluation score: {eval_result.final_score}")
            logger.info(f"Success: {'Yes' if eval_result.final_score == 1.0 else 'No'}")  # NOSONAR - binary scores are always exact 0.0 or 1.0
            result_data.update(
                {
                    "score": eval_result.final_score,
                    "success": eval_result.final_score == 1.0,  # NOSONAR - binary scores are always exact 0.0 or 1.0
                }
            )
            if eval_result.gif_recording and CONFIG.save_output:
                gif_path = output_dir / f"{timestamp}_{task.id}.gif"
                await save_gif(eval_result.gif_recording, gif_path)
                result_data["gif_path"] = str(gif_path)

        if CONFIG.save_output:
            output_dir / f"{timestamp}_{task.id}.json"
            # await save_file(json_path, result_data)
    except Exception as e:
        logger.exception(f"Error executing task: {e}")
        result_data["error"] = str(e)
        error_path = output_dir / f"{timestamp}_{task.id}_error.json"
        await save_file(error_path, result_data)
    finally:
        await backend.close()


if __name__ == "__main__":
    asyncio.run(run_prompt_test())
