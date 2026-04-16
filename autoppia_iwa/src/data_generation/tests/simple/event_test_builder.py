from __future__ import annotations

from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest

from .utils import enum_to_raw_recursive


def build_check_event_test(task: Task, constraints: list[dict[str, Any]]) -> CheckEventTest:
    """Build a CheckEventTest from task constraints."""
    if not constraints:
        return CheckEventTest(
            type="CheckEventTest",
            event_name=task.use_case.name,
            event_criteria={},
        )

    criteria: dict[str, Any] = {}
    for raw in constraints:
        clean = enum_to_raw_recursive(raw)
        field = clean.get("field")
        operator = clean.get("operator", "equals")
        value = clean.get("value")

        if field is None:
            logger.warning("Constraint without 'field' skipped: %r", clean)
            continue

        if operator == "equals":
            criteria[field] = value
        else:
            criteria[field] = {"operator": operator, "value": value}

    return CheckEventTest(
        type="CheckEventTest",
        event_name=task.use_case.name,
        event_criteria=criteria,
    )
