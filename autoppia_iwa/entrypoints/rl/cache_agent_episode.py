from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from collections.abc import Iterable
from datetime import datetime
from enum import Enum
from pathlib import Path

import requests
from loguru import logger

from autoppia_iwa.entrypoints.benchmark.task_generation import generate_tasks_for_project
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions import actions as _actions  # noqa: F401 -- ensure registry populated
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution

DEFAULT_CACHE_DIR = "data/cache/tasks"
DEFAULT_OUTPUT_DIR = Path("data/inputs/reward_model/raw_evaluations")


async def _generate_tasks(project_id: str, count: int, use_cached: bool, cache_dir: str) -> list[Task]:
    project = next((p for p in demo_web_projects if p.id == project_id), None)
    if project is None:
        raise ValueError(f"Project '{project_id}' not found in demo_web_projects")

    tasks = await generate_tasks_for_project(
        project,
        use_cached=use_cached,
        cache_dir=cache_dir,
        prompts_per_use_case=1,
        num_use_cases=max(1, count),
        use_cases=None,
        enable_dynamic_html=False,
    )
    if not tasks:
        raise RuntimeError("Task generation returned no tasks")
    return tasks[:count]


def _sanitize_payload(obj):
    if isinstance(obj, dict):
        return {key: _sanitize_payload(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_payload(item) for item in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    return obj


async def _evaluate_task(task: Task, solution: TaskSolution, project_id: str) -> tuple[dict, dict]:
    project = next((p for p in demo_web_projects if p.id == project_id), None)
    if project is None:
        raise ValueError(f"Project '{project_id}' not found")

    evaluator = ConcurrentEvaluator(web_project=project, config=EvaluatorConfig())
    result = await evaluator.evaluate_single_task_solution(task, solution)

    stats = result.stats.model_dump() if result.stats else {}

    return _serialize_evaluation(task, solution, result), stats


def _serialize_evaluation(task: Task, solution: TaskSolution, evaluation_result) -> dict:
    episode_id = f"{task.id}-{solution.web_agent_id or 'cache_agent'}"
    steps = []
    for idx, action_result in enumerate(evaluation_result.execution_history):
        snapshot = action_result.browser_snapshot
        action_dump = action_result.action.model_dump(mode="python")
        action_dump.setdefault("kind", action_dump.get("type"))
        step_payload = {
            "index": idx,
            "action_result": {
                "action": action_dump,
                "action_event": action_result.action_event,
                "successfully_executed": action_result.successfully_executed,
                "error": action_result.error,
                "execution_time": action_result.execution_time,
                "browser_snapshot": {
                    "iteration": snapshot.iteration,
                    "current_url": snapshot.current_url,
                    "prev_html": snapshot.prev_html,
                    "current_html": snapshot.current_html,
                    "backend_events": [event.model_dump() for event in snapshot.backend_events],
                    "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
                    "action": action_dump,
                },
            },
            "tests": [],
        }
        steps.append(step_payload)

    tests_definition = [test.model_dump() for test in task.tests]
    evaluation_tests = [test.model_dump() for test in evaluation_result.test_results]

    payload = {
        "episode_id": episode_id,
        "project_id": task.web_project_id,
        "task_id": task.id,
        "task_prompt": task.prompt,
        "web_agent_id": solution.web_agent_id,
        "final_score": evaluation_result.final_score,
        "raw_score": evaluation_result.raw_score,
        "tests_definition": tests_definition,
        "evaluation_tests": evaluation_tests,
        "steps": steps,
    }
    return payload


def _agent_alive(base_url: str) -> bool:
    try:
        response = requests.get(f"{base_url}/info", timeout=2.0)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _start_agent(port: int, agent_number: int) -> subprocess.Popen | None:
    base_url = f"http://127.0.0.1:{port}"
    if _agent_alive(base_url):
        logger.info("Agent already running on port %d, reusing existing instance", port)
        return None
    repo_root = Path(__file__).resolve().parents[3]
    dashboard_root = repo_root.parent
    simple_api = dashboard_root / "autoppia_web_agents" / "simple_api.py"
    if not simple_api.exists():
        raise FileNotFoundError(f"simple_api.py not found at {simple_api}")

    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    module_root = dashboard_root / "autoppia_web_agents" / "modules" / "autoppia_iwa_module"
    new_pythonpath_segments = [str(dashboard_root), str(module_root), str(module_root / "autoppia_iwa")]
    if pythonpath:
        new_pythonpath_segments.append(pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(new_pythonpath_segments)

    logger.info("Starting cache agent (agent_number=%s) on port %d", agent_number, port)
    proc = subprocess.Popen(
        [sys.executable, str(simple_api), "--port", str(port), "--agent_number", str(agent_number)],
        cwd=str(simple_api.parent),
        env=env,
    )
    return proc


def _wait_for_agent(base_url: str, timeout: float = 60.0) -> None:
    url = f"{base_url}/info"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=2.0)
            if response.status_code == 200:
                logger.info("Agent API is ready")
                return
        except requests.RequestException:
            pass
        time.sleep(1.0)
    raise TimeoutError(f"Agent API did not respond within {timeout} seconds")


def _solve_task_http(task: Task, base_url: str, web_agent_id: str) -> TaskSolution:
    payload = task.serialize()
    payload["assign_seed"] = False
    payload["web_agent_id"] = web_agent_id
    payload.pop("use_case", None)
    payload = _sanitize_payload(payload)
    response = requests.post(f"{base_url}/solve_task", json=payload, timeout=120)
    if response.status_code != 200:
        raise RuntimeError(f"Agent API error {response.status_code}: {response.text}")
    data = response.json()
    actions_payload = data.get("actions", [])
    actions = []
    for action_data in actions_payload:
        action = BaseAction.create_action(action_data)
        if action is None:
            raise ValueError(f"Unknown action payload: {action_data}")
        actions.append(action)

    solution = TaskSolution(
        task_id=data.get("task_id", task.id),
        actions=actions,
        web_agent_id=data.get("web_agent_id") or web_agent_id,
        recording=data.get("recording"),
    )
    return solution


def _terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    logger.info("Stopping agent API process")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate evaluation episodes with BaseAgentWithCache")
    parser.add_argument("--project-id", default="autozone", help="Demo web project id (e.g. autozone)")
    parser.add_argument("--count", type=int, default=1, help="Number of tasks to generate and evaluate")
    parser.add_argument("--agent-port", type=int, default=7000, help="Port for the simple API agent")
    parser.add_argument("--agent-number", type=int, default=5, help="Agent number for simple_api (5=BaseAgentWithCache)")
    parser.add_argument("--use-cached", action="store_true", help="Allow using cached tasks instead of regenerating")
    parser.add_argument("--cache-dir", default=DEFAULT_CACHE_DIR, help="Task cache directory")
    parser.add_argument("--output", default=None, help="Output JSONL path")
    parser.add_argument("--web-agent-id", default="cache_agent", help="Identifier to attach to TaskSolution")
    parser.add_argument(
        "--base-url",
        default=None,
        help="Explicit base URL for an already running /solve_task API (e.g. http://host:port)",
    )
    parser.add_argument(
        "--spawn-simple-api",
        action="store_true",
        help="Start the bundled simple_api process locally (ignored when --base-url is provided)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    output_path = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR / f"{args.project_id}_cache_agent.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.base_url:
        base_url = args.base_url.rstrip("/")
        proc = None
    else:
        base_url = f"http://127.0.0.1:{args.agent_port}"
        proc = _start_agent(args.agent_port, args.agent_number) if args.spawn_simple_api else None
        time.sleep(1.0)
    try:
        _wait_for_agent(base_url)
        tasks = asyncio.run(_generate_tasks(args.project_id, args.count, args.use_cached, args.cache_dir))
        logger.info("Generated %d task(s) for project %s", len(tasks), args.project_id)

        for task in tasks:
            solution = _solve_task_http(task, base_url, args.web_agent_id)
            episode_payload, stats = asyncio.run(_evaluate_task(task, solution, args.project_id))

            with output_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(_sanitize_payload(episode_payload), ensure_ascii=False) + "\n")

            logger.info(
                "Stored episode %s (score=%.2f raw=%.2f actions=%d)",
                episode_payload["episode_id"],
                episode_payload["final_score"],
                episode_payload["raw_score"],
                len(episode_payload["steps"]),
            )
    finally:
        if proc is not None:
            _terminate_process(proc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
