"""
Event-trajectory verifier for the web verification pipeline.

Runs deterministic event trajectories (project-level or use-case-filtered) and
validates them through the standard evaluator stack.
"""

from __future__ import annotations

import copy
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import Trajectory, WebProject
from autoppia_iwa.src.demo_webs.trajectory_registry import get_trajectory_map, remap_url_to_frontend
from autoppia_iwa.src.evaluation.concurrent_evaluator import ConcurrentEvaluator
from autoppia_iwa.src.evaluation.legacy.concurrent_config import EvaluatorConfig
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution


def _normalize_use_case_name(value: str | None) -> str:
    return str(value or "").strip().upper()


def _first_navigate_url(actions: list[BaseAction] | None) -> str | None:
    for action in actions or []:
        if isinstance(action, NavigateAction) and getattr(action, "url", None):
            return str(action.url)
    return None


def _prepare_actions(actions: list[BaseAction] | None, frontend_url: str | None) -> list[BaseAction]:
    cloned = copy.deepcopy(actions or [])
    if not frontend_url:
        return cloned
    for action in cloned:
        if isinstance(action, NavigateAction) and action.url:
            action.url = remap_url_to_frontend(action.url, frontend_url)
    return cloned


class EventTrajectoryVerifier:
    """Executes and validates event trajectories for a project/use-case."""

    def __init__(
        self,
        web_project: WebProject,
        *,
        frontend_url: str | None = None,
        headless: bool = True,
        web_agent_id_for_replay: str = "1",
    ) -> None:
        self.web_project = web_project
        self.frontend_url = frontend_url or getattr(web_project, "frontend_url", None)
        self.headless = headless
        self.web_agent_id_for_replay = str(web_agent_id_for_replay or "1")

    async def verify_for_project(self, *, use_cases: list[str] | None = None) -> dict[str, Any]:
        trajectory_map = get_trajectory_map(self.web_project.id)
        if trajectory_map is None:
            return {
                "skipped": True,
                "reason": f"No event trajectory registry for project '{self.web_project.id}'",
                "project_id": self.web_project.id,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        normalized_use_cases = {_normalize_use_case_name(use_case) for use_case in use_cases or []}
        selected = {use_case_name: trajectory for use_case_name, trajectory in trajectory_map.items() if not normalized_use_cases or _normalize_use_case_name(use_case_name) in normalized_use_cases}

        if not selected:
            use_case_suffix = ""
            if normalized_use_cases:
                use_case_suffix = f" and use_cases={sorted(normalized_use_cases)}"
            return {
                "skipped": True,
                "reason": f"No event trajectories for project '{self.web_project.id}'{use_case_suffix}",
                "project_id": self.web_project.id,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        results: list[dict[str, Any]] = []
        for use_case_name, trajectory in selected.items():
            ok, detail, meta = await self._run_one(use_case_name=use_case_name, trajectory=trajectory)
            results.append(
                {
                    "trajectory_id": use_case_name,
                    "use_case": use_case_name,
                    "ok": ok,
                    "detail": detail,
                    **meta,
                }
            )

        passed_count = sum(1 for item in results if item.get("ok"))
        total_count = len(selected)
        all_passed = bool(total_count > 0 and passed_count == total_count)
        return {
            "skipped": False,
            "project_id": self.web_project.id,
            "use_cases_tested": sorted({_normalize_use_case_name(use_case_name) for use_case_name in selected}),
            "total_count": total_count,
            "passed_count": passed_count,
            "all_passed": all_passed,
            "results": results,
        }

    async def _run_one(self, *, use_case_name: str, trajectory: Trajectory) -> tuple[bool, str, dict[str, Any]]:
        raw_entry = _first_navigate_url(trajectory.actions)
        if not raw_entry:
            return False, "trajectory has no NavigateAction with url", {"score": 0.0, "tests_passed": 0, "total_tests": 0}

        entry = remap_url_to_frontend(raw_entry, self.frontend_url) if self.frontend_url else raw_entry
        actions = _prepare_actions(trajectory.actions, self.frontend_url)
        if not actions:
            return False, "trajectory has no actions", {"score": 0.0, "tests_passed": 0, "total_tests": 0}

        use_case = self._resolve_use_case(use_case_name)
        task = Task(
            url=entry,
            prompt=trajectory.prompt or f"Replay trajectory for use case {use_case_name}",
            web_project_id=self.web_project.id,
            is_web_real=False,
            specifications=BrowserSpecification(),
            tests=copy.deepcopy(trajectory.tests or []),
            use_case=use_case,
        )

        task_solution = TaskSolution(
            task_id=task.id,
            actions=actions,
            web_agent_id=self.web_agent_id_for_replay,
        )
        task_solution.replace_credentials(self.web_agent_id_for_replay)
        task_solution.actions = task_solution.replace_web_agent_id()

        try:
            evaluator = ConcurrentEvaluator(
                self.web_project,
                EvaluatorConfig(
                    enable_grouping_tasks=False,
                    chunk_size=1,
                    should_record_gif=False,
                    verbose_logging=False,
                    headless=self.headless,
                ),
            )
            evaluation_result = await evaluator.evaluate_single_task_solution(task, task_solution)
        except Exception as exc:
            logger.exception(f"Event trajectory execution error: use_case={use_case_name} error={exc}")
            return False, f"execution error: {exc}", {"score": 0.0, "tests_passed": 0, "total_tests": 0}

        score = float(getattr(evaluation_result, "final_score", 0.0) or 0.0)
        stats = getattr(evaluation_result, "stats", None)
        tests_passed = int(getattr(stats, "tests_passed", 0) or 0)
        total_tests = int(getattr(stats, "total_tests", 0) or 0)
        ok = abs(score - 1.0) < 1e-9
        detail = f"score={score:.3f} tests={tests_passed}/{total_tests}"
        return ok, detail, {"score": score, "tests_passed": tests_passed, "total_tests": total_tests}

    def _resolve_use_case(self, use_case_name: str):
        target = _normalize_use_case_name(use_case_name)
        for use_case in self.web_project.use_cases or []:
            if _normalize_use_case_name(getattr(use_case, "name", None)) == target:
                return use_case
        return None
