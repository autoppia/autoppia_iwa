#!/usr/bin/env python3
"""
Run concrete trajectories (scripted actions + CheckEventTests) for a web project.

CLI (from autoppia_iwa repo root):

  python scripts/debug_trajectories.py --project autodrive --use-case SELECT_DATE
  python scripts/debug_trajectories.py -p autodrive
      # all registered trajectories for the project (registry order)
  python scripts/debug_trajectories.py -p autohealth -u OPEN_APPOINTMENT_FORM \\
      --frontend-url http://127.0.0.1:8013

With a single ``-u``, prints one SUCCESS or FAIL line. With no ``-u`` or multiple ``-u`` flags,
prints one line per use case and exits 0 only if every run succeeded.

PyCharm:
  1. Working directory: autoppia_iwa repo root (parent of ``scripts/``).
  2. Python interpreter: this repo's ``.venv`` (or equivalent with ``autoppia_iwa`` installed).
  3. Script path: ``scripts/debug_trajectories.py`` (or the absolute path to this file).
  4. Script parameters: e.g. ``-p autodrive --no-headless`` or ``-p autodrive -u SELECT_DATE --no-headless``
     (optional ``--frontend-url``).
  5. Run → Debug (set breakpoints in this file or in ``stateful_evaluator`` / actions as needed).

If you start Debug with **no** script parameters, this script applies a small default argv
(``autodrive`` / ``--no-headless``, no ``-u``) so all autodrive trajectories run unless you override.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import sys
from pathlib import Path
from typing import Any

# Ensure local package imports work when running this script directly.
_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.demo_webs.trajectory_registry import (
    get_trajectory_map,
    remap_url_to_frontend,
    supported_trajectory_project_ids,
)
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction


def _first_navigate_url(actions: list[BaseAction] | None) -> str | None:
    for a in actions or []:
        if isinstance(a, NavigateAction) and getattr(a, "url", None):
            return str(a.url)
    return None


def _prepare_actions(actions: list[BaseAction] | None, frontend_url: str | None) -> list[BaseAction]:
    cloned = copy.deepcopy(actions or [])
    if not frontend_url:
        return cloned
    for a in cloned:
        if isinstance(a, NavigateAction) and a.url:
            a.url = remap_url_to_frontend(a.url, frontend_url)
    return cloned


def _build_task(*, project_id: str, prompt: str, entry_url: str, tests: list[Any] | None) -> Task:
    return Task(
        url=entry_url,
        prompt=prompt,
        web_project_id=project_id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=list(tests or []),
    )


async def _run_one(
    flows: dict[str, Trajectory],
    project_id: str,
    use_case: str,
    frontend_url: str | None,
    *,
    headless: bool,
) -> tuple[bool, str]:
    tr = flows.get(use_case)
    if tr is None:
        names = ", ".join(sorted(flows.keys()))
        return False, f"unknown use case {use_case!r}; available: {names}"

    if not tr.tests:
        return False, "trajectory has no tests (cannot score)"

    raw_entry = _first_navigate_url(tr.actions)
    if not raw_entry:
        return False, "trajectory has no NavigateAction with url"

    entry = remap_url_to_frontend(raw_entry, frontend_url) if frontend_url else raw_entry
    actions = _prepare_actions(tr.actions, frontend_url)
    task = _build_task(project_id=project_id, prompt=tr.prompt, entry_url=entry, tests=tr.tests)

    evaluator = AsyncStatefulEvaluator(
        task=task,
        web_agent_id="1",
        should_record_gif=False,
        capture_screenshot=False,
        headless=headless,
    )
    try:
        await evaluator.reset()
        for action in actions[1:]:
            await evaluator.step(action)
        details = await evaluator.get_score_details()
    except Exception as exc:
        return False, str(exc)
    finally:
        await evaluator.close()

    if details.total_tests <= 0:
        return False, "no tests ran (total_tests=0)"
    if details.success:
        return True, f"tests_passed={details.tests_passed}/{details.total_tests} score={details.raw_score:.2f}"
    return False, f"tests_passed={details.tests_passed}/{details.total_tests} score={details.raw_score:.2f}"


async def _run_selected(
    project_id: str,
    use_case_filter: list[str] | None,
    frontend_url: str | None,
    *,
    headless: bool,
) -> tuple[bool, list[tuple[str, bool, str]]]:
    flows = get_trajectory_map(project_id)
    if flows is None:
        supported = ", ".join(sorted(supported_trajectory_project_ids()))
        return False, [("", False, f"unknown project {project_id!r}; supported: {supported}")]

    if use_case_filter is None:
        names = list(flows.keys())
    else:
        unknown = [u for u in use_case_filter if u not in flows]
        if unknown:
            avail = ", ".join(sorted(flows.keys()))
            return False, [("", False, f"unknown use case(s) {unknown!r}; available: {avail}")]
        names = list(use_case_filter)

    if not names:
        return False, [("", False, "no trajectories registered for this project")]

    results: list[tuple[str, bool, str]] = []
    for uc in names:
        ok, detail = await _run_one(flows, project_id, uc, frontend_url, headless=headless)
        results.append((uc, ok, detail))
    all_ok = all(ok for _, ok, _ in results)
    return all_ok, results


def main() -> int:
    if len(sys.argv) == 1:
        sys.argv.extend(
            [
                "-p",
                "autodrive",
                "-u",
                "CANCEL_RESERVATION",
                "--no-headless",
            ]
        )

    parser = argparse.ArgumentParser(description="Run IWA concrete trajectory(ies) and report success or failure.")
    parser.add_argument("--project", "-p", required=True, help="Web project id (e.g. autodrive, autohealth, autolist)")
    parser.add_argument(
        "--use-case",
        "-u",
        action="append",
        default=None,
        help="Use case name (repeatable). If omitted, every registered trajectory for the project is run.",
    )
    parser.add_argument(
        "--frontend-url",
        default=None,
        help="If set, remap trajectory localhost URLs to this origin (scheme+host+port), e.g. http://127.0.0.1:8012",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show the browser window (default is headless)",
    )
    args = parser.parse_args()

    AppBootstrap()

    headless = not args.no_headless
    all_ok, results = asyncio.run(_run_selected(args.project, args.use_case, args.frontend_url, headless=headless))

    if len(results) == 1:
        _, ok, detail = results[0]
        print(f"{'SUCCESS' if ok else 'FAIL'} ({detail})")
        return 0 if ok else 1

    for uc, ok, detail in results:
        print(f"{uc}: {'SUCCESS' if ok else 'FAIL'} ({detail})")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
