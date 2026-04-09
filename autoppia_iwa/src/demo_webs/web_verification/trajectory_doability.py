"""
Build Step-3 doability payloads from an in-repo Trajectory (same shape as IWAP process_api_response_for_tasks).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autoppia_iwa.src.demo_webs.classes import Trajectory


def doability_result_from_trajectory(traj: Trajectory, *, fallback_start_url: str) -> dict[str, Any]:
    """
    Convert a Trajectory into the dict expected by Step 4 (verify_task_with_seeds).

    Mirrors IWAPClient.process_api_response_for_tasks output keys: matched, actions,
    api_prompt, api_tests, api_start_url.
    """
    from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction

    raw_actions = traj.actions or []
    if not raw_actions:
        return {"matched": False, "reason": "Trajectory has no actions", "actions": None}

    solution_actions: list[dict[str, Any]] = []
    for a in raw_actions:
        if isinstance(a, BaseAction):
            solution_actions.append(a.to_tool_call())

    if not solution_actions:
        return {"matched": False, "reason": "Could not serialize trajectory actions to tool calls", "actions": None}

    api_start_url = ""
    for a in raw_actions:
        if isinstance(a, NavigateAction) and getattr(a, "url", None):
            api_start_url = a.url
            break
    if not api_start_url:
        base = (fallback_start_url or "").rstrip("/")
        if base:
            api_start_url = f"{base}/?seed=1"

    api_tests: list[dict[str, Any]] = []
    for t in traj.tests or []:
        if hasattr(t, "model_dump"):
            api_tests.append(t.model_dump())
        elif isinstance(t, dict):
            api_tests.append(t)

    return {
        "matched": True,
        "match_type": "trajectory_reference",
        "reason": "Use case is doable — reference trajectory is registered for this project.",
        "actions": solution_actions,
        "api_prompt": traj.prompt or "",
        "api_tests": api_tests,
        "api_start_url": api_start_url,
        "api_task_id": None,
        "api_web_version": "",
        "total_solutions_found": 1,
    }
