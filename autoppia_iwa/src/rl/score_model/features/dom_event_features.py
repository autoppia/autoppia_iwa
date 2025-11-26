from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ..features.snapshot_encoder import clean_dom

INPUT_PATTERN = re.compile(r"<input[\s>]", re.IGNORECASE)
BUTTON_PATTERN = re.compile(r"<button[\s>]", re.IGNORECASE)
LINK_PATTERN = re.compile(r"<a[\s>]", re.IGNORECASE)
TEXTAREA_PATTERN = re.compile(r"<textarea[\s>]", re.IGNORECASE)
FORM_PATTERN = re.compile(r"<form[\s>]", re.IGNORECASE)


def _count(pattern: re.Pattern[str], html: str) -> int:
    if not html:
        return 0
    return len(pattern.findall(html))


def extract_dom_features(html: str) -> dict[str, Any]:
    """Return simple structural/textual stats from raw HTML."""

    cleaned = clean_dom(html or "")
    features = {
        "html_length": len(html or ""),
        "dom_length": len(cleaned),
        "num_inputs": _count(INPUT_PATTERN, html),
        "num_buttons": _count(BUTTON_PATTERN, html),
        "num_links": _count(LINK_PATTERN, html),
        "num_textareas": _count(TEXTAREA_PATTERN, html),
        "num_forms": _count(FORM_PATTERN, html),
    }
    return features


def extract_js_event_features(events: Iterable[dict[str, Any]]) -> dict[str, Any]:
    counter = Counter()
    for event in events or []:
        event_type = (event or {}).get("event_type")
        if event_type:
            counter[event_type] += 1
    features = {f"js_{k}_count": v for k, v in counter.items()}
    features["js_event_total"] = sum(counter.values())
    return features


def extract_action_features(action: dict[str, Any]) -> dict[str, Any]:
    action = action or {}
    features: dict[str, Any] = {
        "action_type": action.get("type", "unknown"),
    }
    if "x" in action:
        features["action_x"] = action.get("x") or 0
    if "y" in action:
        features["action_y"] = action.get("y") or 0
    if "selector" in action:
        selector = action.get("selector") or {}
        features["has_selector"] = int(bool(selector))
    return features


def extract_backend_features(snapshot: dict[str, Any]) -> dict[str, Any]:
    after_events = snapshot.get("backend_events") or []
    before_events = snapshot.get("backend_events_before") or []
    return {
        "backend_event_count_before": len(before_events),
        "backend_event_count_after": len(after_events),
        "backend_event_delta": len(after_events) - len(before_events),
    }


def step_feature_row(
    trace_path: Path,
    raw_step: dict[str, Any],
    episode_uuid: str,
    step_index: int,
) -> dict[str, Any]:
    action = raw_step.get("action", {})
    snapshot = raw_step.get("browser_snapshot", {}) or {}
    html = snapshot.get("current_html", "")
    js_events = snapshot.get("js_events") or []

    row: dict[str, Any] = {
        "trace_file": str(trace_path),
        "episode_id": episode_uuid,
        "task_id": raw_step.get("task_id", raw_step.get("task", "")),
        "action_index": step_index,
        "success": bool(raw_step.get("success")),
        "execution_time": raw_step.get("execution_time", math.nan),
        "current_url": snapshot.get("current_url", ""),
    }
    row.update(extract_dom_features(html))
    row.update(extract_js_event_features(js_events))
    row.update(extract_action_features(action))
    row.update(extract_backend_features(snapshot))
    return row


def episode_feature_row(episode_id: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    if not steps:
        return {"episode_id": episode_id, "steps": 0, "success_rate": 0.0, "avg_execution_time": 0.0}
    total = len(steps)
    success = sum(1 for step in steps if step.get("success"))
    avg_time = sum(step.get("execution_time") or 0.0 for step in steps) / max(total, 1)
    backend_events = sum(step.get("backend_event_count", 0) for step in steps)
    return {
        "episode_id": episode_id,
        "steps": total,
        "success_rate": success / total if total else 0.0,
        "avg_execution_time": avg_time,
        "backend_event_total": backend_events,
    }
