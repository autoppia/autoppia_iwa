"""
Data-extraction trajectory verifier for the web verification pipeline.

Runs deterministic data-extraction trajectories (seed-filtered, project-level or use-case-filtered)
and validates extracted outputs against expected answers.
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory, WebProject
from autoppia_iwa.src.demo_webs.data_extraction_trajectory_registry import get_data_extraction_trajectories
from autoppia_iwa.src.demo_webs.trajectory_registry import remap_url_to_frontend
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.execution.actions.actions import ExtractAction, NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def _normalize_use_case_name(value: str | None) -> str:
    return str(value or "").strip().upper()


def _normalize_expected(expected_answer: str | list[str]) -> list[str]:
    if isinstance(expected_answer, str):
        return [expected_answer]
    return [str(value) for value in expected_answer if str(value).strip()]


def _matches_expected(extracted_text: str, expected_answer: str | list[str]) -> tuple[bool, str]:
    normalized_extracted = _normalize_text(extracted_text)
    candidates = _normalize_expected(expected_answer)
    if not candidates:
        return False, "empty expected_answer"

    for candidate in candidates:
        normalized_candidate = _normalize_text(candidate)
        if normalized_candidate and normalized_candidate in normalized_extracted:
            return True, candidate
    return False, candidates[0]


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


def _short(value: str, max_chars: int) -> str:
    cleaned = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}..."


class DataExtractionTrajectoryVerifier:
    """Executes and validates data-extraction trajectories for a project/use-case."""

    def __init__(
        self,
        web_project: WebProject,
        *,
        frontend_url: str | None = None,
        headless: bool = True,
        show_extract_chars: int = 220,
    ) -> None:
        self.web_project = web_project
        self.frontend_url = frontend_url or getattr(web_project, "frontend_url", None)
        self.headless = headless
        self.show_extract_chars = max(80, int(show_extract_chars))
        self.task_generator: SimpleTaskGenerator | None = None

    async def verify_for_project(self, *, seed: int = 1, use_cases: list[str] | None = None) -> dict[str, Any]:
        trajectories = get_data_extraction_trajectories(self.web_project.id)
        if trajectories is None:
            return {
                "skipped": True,
                "reason": f"No data-extraction trajectory registry for project '{self.web_project.id}'",
                "project_id": self.web_project.id,
                "seed": seed,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        normalized_use_cases = {_normalize_use_case_name(use_case) for use_case in use_cases or []}
        selected = [
            trajectory for trajectory in trajectories if int(trajectory.seed) == int(seed) and (not normalized_use_cases or _normalize_use_case_name(trajectory.use_case) in normalized_use_cases)
        ]
        if not selected:
            use_case_suffix = ""
            if normalized_use_cases:
                use_case_suffix = f" and use_cases={sorted(normalized_use_cases)}"
            return {
                "skipped": True,
                "reason": f"No data-extraction trajectories for project '{self.web_project.id}', seed={seed}{use_case_suffix}",
                "project_id": self.web_project.id,
                "seed": seed,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        return await self._verify_selected(trajectories=selected, seed=seed)

    async def verify_for_use_case(self, *, use_case_name: str, seed: int = 1) -> dict[str, Any]:
        trajectories = get_data_extraction_trajectories(self.web_project.id)
        if trajectories is None:
            return {
                "skipped": True,
                "reason": f"No data-extraction trajectory registry for project '{self.web_project.id}'",
                "use_case": use_case_name,
                "seed": seed,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        selected = [trajectory for trajectory in trajectories if _normalize_use_case_name(trajectory.use_case) == _normalize_use_case_name(use_case_name) and int(trajectory.seed) == int(seed)]
        if not selected:
            return {
                "skipped": True,
                "reason": f"No data-extraction trajectories for use case '{use_case_name}' and seed={seed}",
                "use_case": use_case_name,
                "seed": seed,
                "total_count": 0,
                "passed_count": 0,
                "all_passed": None,
                "results": [],
            }

        return await self._verify_selected(trajectories=selected, seed=seed, use_case_name=use_case_name)

    async def _verify_selected(
        self,
        *,
        trajectories: list[DataExtractionTrajectory],
        seed: int,
        use_case_name: str | None = None,
    ) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        dataset = await self._load_dataset(seed)
        dataset_text = self._dataset_to_text(dataset)
        for trajectory in trajectories:
            has_actions = bool(trajectory.actions)
            if has_actions:
                ok, detail = await self._run_one_replay(trajectory)
            else:
                ok, detail = self._run_one_dataset_only(trajectory, dataset_text)
            results.append(
                {
                    "trajectory_id": trajectory.id,
                    "use_case": trajectory.use_case,
                    "ok": ok,
                    "detail": detail,
                    "expected_answer": trajectory.expected_answer,
                    "mode": "replay" if has_actions else "dataset_only",
                }
            )

        passed_count = sum(1 for item in results if item.get("ok"))
        total_count = len(trajectories)
        all_passed = bool(total_count > 0 and passed_count == total_count)

        return {
            "skipped": False,
            "project_id": self.web_project.id,
            "use_case": use_case_name,
            "use_cases_tested": sorted({_normalize_use_case_name(trajectory.use_case) for trajectory in trajectories}),
            "seed": seed,
            "total_count": total_count,
            "passed_count": passed_count,
            "all_passed": all_passed,
            "results": results,
        }

    def _run_one_dataset_only(self, trajectory: DataExtractionTrajectory, dataset_text: str) -> tuple[bool, str]:
        if not dataset_text:
            return False, "dataset-only validation failed: could not load dataset for seed"

        expected_values = _normalize_expected(trajectory.expected_answer)
        if not expected_values:
            return False, "dataset-only validation failed: empty expected_answer"

        normalized_dataset = _normalize_text(dataset_text)
        for expected in expected_values:
            if _normalize_text(expected) in normalized_dataset:
                return True, f"id={trajectory.id} dataset_only matched='{expected}'"

        return False, f"id={trajectory.id} dataset_only expected_one_of={expected_values} (not found in seed dataset)"

    async def _run_one_replay(self, trajectory: DataExtractionTrajectory) -> tuple[bool, str]:
        raw_entry = _first_navigate_url(trajectory.actions)
        if not raw_entry:
            return False, "trajectory has no NavigateAction with url"

        entry = remap_url_to_frontend(raw_entry, self.frontend_url) if self.frontend_url else raw_entry
        actions = _prepare_actions(trajectory.actions, self.frontend_url)

        evaluator = AsyncStatefulEvaluator(
            task=trajectory_to_task(trajectory=trajectory, entry_url=entry),
            web_agent_id="web-verification-de-trajectory",
            should_record_gif=False,
            capture_screenshot=False,
            headless=self.headless,
        )

        extracted_outputs: list[str] = []
        try:
            await evaluator.reset()
            start_index = 1 if actions and isinstance(actions[0], NavigateAction) else 0
            for action in actions[start_index:]:
                step_result = await evaluator.step(action)
                if isinstance(action, ExtractAction):
                    action_output = step_result.action_result.action_output if step_result.action_result else None
                    extracted_outputs.append(str(action_output or ""))
        except Exception as exc:
            logger.exception(f"Data-extraction trajectory execution error: id={trajectory.id} error={exc}")
            return False, f"execution error: {exc}"
        finally:
            await evaluator.close()

        if not extracted_outputs:
            return False, "no ExtractAction output captured"

        combined_output = "\n".join(output for output in extracted_outputs if output)
        if not combined_output.strip():
            return False, "ExtractAction output is empty"

        matches, matched_candidate = _matches_expected(combined_output, trajectory.expected_answer)
        if matches:
            return (
                True,
                f"id={trajectory.id} matched='{matched_candidate}' extracted='{_short(combined_output, self.show_extract_chars)}'",
            )

        expected_values = _normalize_expected(trajectory.expected_answer)
        return (
            False,
            f"id={trajectory.id} expected_one_of={expected_values} extracted='{_short(combined_output, self.show_extract_chars)}'",
        )

    @staticmethod
    def _dataset_to_text(dataset: dict[str, list[dict]] | None) -> str:
        if not dataset:
            return ""
        try:
            return json.dumps(dataset, ensure_ascii=False, sort_keys=True)
        except Exception:
            return str(dataset)

    async def _load_dataset(self, seed: int) -> dict[str, list[dict]] | None:
        if self.task_generator is None:
            self.task_generator = SimpleTaskGenerator(
                web_project=self.web_project,
            )
        return await self.task_generator._load_dataset(seed)


def trajectory_to_task(*, trajectory: DataExtractionTrajectory, entry_url: str):
    from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task

    return Task(
        url=entry_url,
        prompt=trajectory.question,
        web_project_id=trajectory.web_project_id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[],
    )
