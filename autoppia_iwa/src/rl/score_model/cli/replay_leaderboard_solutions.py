#!/usr/bin/env python3
"""Replay leaderboard solutions inside the instrumented evaluator to capture DOM/JS traces."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

try:  # pragma: no cover - require tqdm for progress tracking
    from tqdm import tqdm
except Exception as exc:  # pragma: no cover
    raise RuntimeError("tqdm is required for replay_leaderboard_solutions. Install it via pip.") from exc

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.rl.agent.evaluators.instrumented import InstrumentationConfig, JsInstrumentedEvaluator
from autoppia_iwa.src.web_agents.classes import TaskSolution

PROJECT_MAP: dict[str, WebProject] = {project.id: project for project in demo_web_projects}


@dataclass
class LeaderboardReplaySample:
    task_id: str
    website: str
    use_case: str | None
    intent: str | None
    start_url: str | None
    required_url: str | None
    actions: list[dict]
    miner_uid: int | None
    web_agent_id: str
    success: bool | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True, help="Leaderboard dataset JSONL path (from build_score_model_training_dataset).")
    parser.add_argument("--output-dir", type=Path, default=Path("data/score_model_pipeline/raw_traces"), help="Destination directory for trace JSONL files.")
    parser.add_argument("--website", action="append", help="Replay only these website IDs (repeatable).")
    parser.add_argument("--success", choices=["true", "false", "all"], default="all", help="Filter by success label.")
    parser.add_argument("--limit", type=int, default=None, help="Overall cap on number of samples to replay.")
    parser.add_argument("--per-website-limit", type=int, default=None, help="Maximum samples per website.")
    parser.add_argument("--max-actions", type=int, default=None, help="Skip solutions longer than this action count.")
    parser.add_argument("--capture-screenshots", action="store_true", help="Store base64 screenshots inside trace snapshots.")
    parser.add_argument("--dry-run", action="store_true", help="Parse/plan only, do not run Playwright.")
    parser.add_argument("--parallel", type=int, default=1, help="Number of websites to replay in parallel (separate Playwright contexts).")
    return parser.parse_args()


def load_samples(path: Path, allowed_websites: set[str] | None, success_filter: str) -> Iterable[LeaderboardReplaySample]:
    keep_success = {"true": True, "false": False}.get(success_filter.lower()) if success_filter.lower() != "all" else None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            website = row.get("website")
            if allowed_websites and website not in allowed_websites:
                continue
            passed = row.get("passed")
            if keep_success is not None and bool(passed) is not keep_success:
                continue
            actions = row.get("actions") or []
            if not actions:
                continue
            miner_uid = row.get("miner_uid")
            agent_id = row.get("agent_run_id") or f"leaderboard_{miner_uid or 'unknown'}"
            yield LeaderboardReplaySample(
                task_id=row.get("task_id"),
                website=website,
                use_case=row.get("use_case"),
                intent=row.get("intent"),
                start_url=row.get("start_url"),
                required_url=row.get("required_url"),
                actions=actions,
                miner_uid=miner_uid,
                web_agent_id=str(agent_id),
                success=bool(passed) if passed is not None else None,
            )


def _match_use_case(project: WebProject, name: str | None) -> UseCase | None:
    if not project.use_cases or not name:
        return None
    upper = name.upper()
    for use_case in project.use_cases:
        if use_case.name.upper() == upper:
            return use_case
    return None


def _normalize_action_payload(raw: dict[str, Any]) -> dict[str, Any]:
    attrs = raw.get("attributes") or {}
    payload = {k: v for k, v in attrs.items() if k != "selector"}
    if "selector" in attrs:
        payload["selector"] = attrs["selector"]

    action_type = (raw.get("type") or "").strip().lower()
    if action_type == "input":
        if "keys" in attrs:
            payload = {"type": "SendKeysIWAAction", "keys": attrs["keys"]}
        else:
            payload.setdefault("type", "TypeAction")
    elif action_type == "navigate":
        payload.setdefault("type", "NavigateAction")
    elif action_type == "click":
        payload.setdefault("type", "ClickAction")
    elif action_type == "scroll":
        payload.setdefault("type", "ScrollAction")
    elif action_type == "wait":
        payload.setdefault("type", "WaitAction")
    elif action_type == "selectdropdownoption":
        payload.setdefault("type", "SelectDropDownOptionAction")
    elif action_type == "select":
        payload.setdefault("type", "SelectAction")
    else:
        payload.setdefault("type", action_type.capitalize() + "Action")
    return payload


def _build_actions(raw_actions: list[dict[str, Any]]) -> list[BaseAction]:
    actions: list[BaseAction] = []
    for idx, raw in enumerate(raw_actions):
        payload = _normalize_action_payload(raw)
        action = BaseAction.create_action(payload)
        if action is None:
            raise ValueError(f"Unsupported action payload at index {idx}: {raw}")
        actions.append(action)
    return actions


def _build_task(project: WebProject, sample: LeaderboardReplaySample, agent_id: str) -> Task:
    use_case = _match_use_case(project, sample.use_case)
    task = Task(
        id=sample.task_id,
        prompt=sample.intent or f"Execute {sample.use_case or 'task'} on {project.name}",
        url=(sample.start_url or project.frontend_url),
        web_project_id=project.id,
        use_case=use_case,
        is_web_real=project.is_web_real,
        relevant_data=project.relevant_data or {},
    )
    object.__setattr__(task, "assign_seed", False)
    return task.prepare_for_agent(agent_id)


async def replay_for_project(
    project: WebProject,
    samples: list[LeaderboardReplaySample],
    instrumentation: InstrumentationConfig,
    max_actions: int | None,
) -> tuple[int, int]:
    evaluator = JsInstrumentedEvaluator(
        project,
        EvaluatorConfig(enable_grouping_tasks=False, chunk_size=5, should_record_gif=False),
        instrumentation=instrumentation,
    )
    total = 0
    successes = 0
    iterator = tqdm(samples, desc=f"{project.id} replays", unit="task")
    for sample in iterator:
        if max_actions is not None and len(sample.actions) > max_actions:
            logger.debug("Skipping %s (%s) due to action limit (%s > %s).", sample.task_id, project.id, len(sample.actions), max_actions)
            continue
        try:
            actions = _build_actions(sample.actions)
        except Exception as exc:
            logger.warning("Failed to convert actions for %s (%s): %s", sample.task_id, project.id, exc)
            continue
        if not actions:
            continue
        task = _build_task(project, sample, sample.web_agent_id)
        solution = TaskSolution(task_id=task.id, actions=actions, web_agent_id=sample.web_agent_id)
        solution.replace_web_agent_id()
        logger.info("Replaying %s (%s) with %d actions.", task.id, project.id, len(actions))
        results = await evaluator.evaluate_task_solutions(task, [solution])
        total += 1
        if results:
            successes += sum(1 for res in results if getattr(res, "tests_passed", 0))
    return total, successes


async def run(args: argparse.Namespace) -> None:
    allowed_websites = set(args.website) if args.website else None
    instrumentation = InstrumentationConfig(
        enabled=not args.dry_run,
        output_dir=args.output_dir,
        capture_screenshots=args.capture_screenshots,
    )
    samples = list(load_samples(args.dataset, allowed_websites, args.success))
    if args.limit:
        samples = samples[: args.limit]
    grouped = defaultdict(list)
    for sample in samples:
        grouped[sample.website].append(sample)

    overall = 0
    passed = 0
    websites = list(grouped.items())
    semaphore = asyncio.Semaphore(max(1, args.parallel))

    async def process_site(website: str, website_samples: list[LeaderboardReplaySample]) -> tuple[str, int, int]:
        async with semaphore:
            project = PROJECT_MAP.get(website)
            if not project:
                logger.warning("No demo project registered for website '%s'; skipping %d samples.", website, len(website_samples))
                return website, 0, 0
            limit = args.per_website_limit or len(website_samples)
            subset = website_samples[:limit]
            logger.info("Replaying %d samples for %s.", len(subset), website)
            completed, successes = await replay_for_project(project, subset, instrumentation, args.max_actions)
            return website, completed, successes

    for coro in tqdm(asyncio.as_completed([process_site(w, samples) for w, samples in websites]), total=len(websites), desc="Websites", unit="site"):
        website, completed, successes = await coro
        overall += completed
        passed += successes

    logger.info("Replay completed: %d tasks evaluated (%d reported successes). Traces stored under %s", overall, passed, args.output_dir)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
