from typing import Any

from autoppia_iwa.src.execution.actions.base import BaseAction


def normalize_type(a: dict[str, Any]) -> dict[str, Any]:
    t = a.get("type") or a.get("action", {}).get("type")
    if not t:
        raise ValueError("Action missing 'type'.")
    if not str(t).endswith("Action"):
        a = dict(a)
        a["type"] = f"{str(t).capitalize()}Action"
    return a


def guard_safe(a: dict[str, Any], safe: list[str]) -> None:
    t = a.get("type") or a.get("action", {}).get("type")
    if not t.endswith("Action"):
        t = f"{str(t).capitalize()}Action"
    if t not in safe:
        raise ValueError(f"Action '{t}' not allowed. Safe list={sorted(safe)}")


def to_action(a: dict[str, Any]) -> BaseAction:
    obj = BaseAction.create_action(normalize_type(a))
    if obj is None:
        raise ValueError("Failed to build BaseAction.")
    return obj
