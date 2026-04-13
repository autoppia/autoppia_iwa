#!/usr/bin/env python3
"""
Run data-extraction trajectories and validate extracted output against expected answers.

Examples:
  .venv/bin/python scripts/debug_data_extraction_trajectories.py --project autocinema
  .venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -u FILM_DETAIL
  .venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -u FILM_DETAIL -u SEARCH_FILM
  .venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema -t <trajectory_id>
  .venv/bin/python scripts/debug_data_extraction_trajectories.py -p autocinema --frontend-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.data_extraction_trajectory_registry import (
    get_data_extraction_trajectories,
    supported_data_extraction_trajectory_project_ids,
)
from autoppia_iwa.src.demo_webs.trajectory_registry import remap_url_to_frontend
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.execution.actions.actions import ExtractAction, NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


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


def _build_task(project_id: str, prompt: str, entry_url: str) -> Task:
    return Task(
        url=entry_url,
        prompt=prompt,
        web_project_id=project_id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[],
    )


def _short(value: str, max_chars: int) -> str:
    cleaned = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}..."


def _normalize_use_case_name(value: str) -> str:
    return str(value or "").strip().upper()


def _resolve_project(project_id: str):
    for project in demo_web_projects:
        if project.id == project_id:
            return project
    return None


def _dataset_to_text(dataset: dict[str, list[dict]] | None) -> str:
    if not dataset:
        return ""
    try:
        return json.dumps(dataset, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(dataset)


def _select_trajectories(
    trajectories: list[DataExtractionTrajectory],
    trajectory_ids: list[str] | None,
    use_cases: list[str] | None,
) -> tuple[list[DataExtractionTrajectory] | None, str | None]:
    selected = list(trajectories)

    if trajectory_ids:
        wanted_ids = {trajectory_id.strip() for trajectory_id in trajectory_ids if trajectory_id.strip()}
        available_ids = {trajectory.id for trajectory in trajectories}
        missing_ids = sorted(wanted_ids - available_ids)
        if missing_ids:
            available = ", ".join(sorted(available_ids))
            return None, f"unknown trajectory id(s) {missing_ids!r}; available: {available}"
        selected = [trajectory for trajectory in selected if trajectory.id in wanted_ids]

    if use_cases:
        wanted_use_cases = {_normalize_use_case_name(use_case) for use_case in use_cases if str(use_case).strip()}
        available_use_cases = {_normalize_use_case_name(str(trajectory.use_case or "")) for trajectory in trajectories}
        available_use_cases.discard("")
        missing_use_cases = sorted(wanted_use_cases - available_use_cases)
        if missing_use_cases:
            available = ", ".join(sorted(available_use_cases))
            return None, f"unknown use case(s) {missing_use_cases!r}; available: {available}"
        selected = [trajectory for trajectory in selected if _normalize_use_case_name(str(trajectory.use_case or "")) in wanted_use_cases]

    if not selected:
        return None, "no data-extraction trajectories matched the provided filters"

    return selected, None


async def _run_one(
    *,
    project_id: str,
    trajectory: DataExtractionTrajectory,
    dataset_text_cache: dict[int, str],
    task_generator: SimpleTaskGenerator | None,
    frontend_url: str | None,
    headless: bool,
    show_extract_chars: int,
) -> tuple[bool, str]:
    if not trajectory.actions:
        if task_generator is None:
            return False, "dataset-only trajectory but project dataset loader is unavailable"
        dataset_text = dataset_text_cache.get(int(trajectory.seed), "")
        if not dataset_text:
            dataset = await task_generator._load_dataset(int(trajectory.seed))
            dataset_text = _dataset_to_text(dataset)
            dataset_text_cache[int(trajectory.seed)] = dataset_text
        return _run_dataset_only(trajectory=trajectory, dataset_text=dataset_text)

    raw_entry = _first_navigate_url(trajectory.actions)
    if not raw_entry:
        return False, "trajectory has no NavigateAction with url"

    entry = remap_url_to_frontend(raw_entry, frontend_url) if frontend_url else raw_entry
    actions = _prepare_actions(trajectory.actions, frontend_url)
    task = _build_task(project_id=project_id, prompt=trajectory.question, entry_url=entry)

    evaluator = AsyncStatefulEvaluator(
        task=task,
        web_agent_id="debug-de-trajectory",
        should_record_gif=False,
        capture_screenshot=False,
        headless=headless,
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
            f"id={trajectory.id} matched='{matched_candidate}' extracted='{_short(combined_output, show_extract_chars)}'",
        )

    expected_values = _normalize_expected(trajectory.expected_answer)
    return (
        False,
        f"id={trajectory.id} expected_one_of={expected_values} extracted='{_short(combined_output, show_extract_chars)}'",
    )


def _run_dataset_only(*, trajectory: DataExtractionTrajectory, dataset_text: str) -> tuple[bool, str]:
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


async def _run_selected(
    *,
    project_id: str,
    trajectory_ids: list[str] | None,
    use_cases: list[str] | None,
    frontend_url: str | None,
    headless: bool,
    show_extract_chars: int,
) -> tuple[bool, list[tuple[str, bool, str]]]:
    trajectories = get_data_extraction_trajectories(project_id)
    if trajectories is None:
        supported = ", ".join(sorted(supported_data_extraction_trajectory_project_ids()))
        return False, [("", False, f"unknown project {project_id!r}; supported: {supported}")]

    selected, selection_error = _select_trajectories(
        trajectories=trajectories,
        trajectory_ids=trajectory_ids,
        use_cases=use_cases,
    )
    if selection_error:
        return False, [("", False, selection_error)]
    assert selected is not None

    project = _resolve_project(project_id)
    task_generator = (
        SimpleTaskGenerator(
            web_project=project,
            llm_service=DIContainer.llm_service(),
        )
        if project is not None
        else None
    )
    dataset_text_cache: dict[int, str] = {}

    results: list[tuple[str, bool, str]] = []
    for trajectory in selected:
        ok, detail = await _run_one(
            project_id=project_id,
            trajectory=trajectory,
            dataset_text_cache=dataset_text_cache,
            task_generator=task_generator,
            frontend_url=frontend_url,
            headless=headless,
            show_extract_chars=show_extract_chars,
        )
        results.append((trajectory.id, ok, detail))
    all_ok = all(ok for _, ok, _ in results)
    return all_ok, results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run data-extraction trajectories and validate extracted output.")
    parser.add_argument("--project", "-p", required=True, help="Web project id (e.g. autocinema)")
    parser.add_argument(
        "--trajectory-id",
        "-t",
        action="append",
        default=None,
        help="Trajectory id to run (repeatable). Optional filter.",
    )
    parser.add_argument(
        "--use-case",
        "-u",
        action="append",
        default=None,
        help="Use case to run (repeatable, case-insensitive). If omitted, all use cases in the project are included.",
    )
    parser.add_argument(
        "--frontend-url",
        default=None,
        help="If set, remap trajectory localhost URLs to this origin (scheme+host+port).",
    )
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default is headless).")
    parser.add_argument(
        "--show-extract-chars",
        type=int,
        default=220,
        help="Max chars of extracted output to print in result lines.",
    )
    args = parser.parse_args()

    AppBootstrap()
    headless = not args.no_headless
    all_ok, results = asyncio.run(
        _run_selected(
            project_id=args.project,
            trajectory_ids=args.trajectory_id,
            use_cases=args.use_case,
            frontend_url=args.frontend_url,
            headless=headless,
            show_extract_chars=max(80, int(args.show_extract_chars)),
        )
    )

    if len(results) == 1:
        _, ok, detail = results[0]
        print(f"{'SUCCESS' if ok else 'FAIL'} ({detail})")
        return 0 if ok else 1

    for trajectory_id, ok, detail in results:
        print(f"{trajectory_id}: {'SUCCESS' if ok else 'FAIL'} ({detail})")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
