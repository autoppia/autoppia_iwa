from __future__ import annotations

from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.data_generation.tests.simple.utils import enum_to_raw_recursive


class GlobalTestGenerationPipeline:
    """
    Simplified pipeline that:

    • Iterates over tasks with a defined UseCase
    • Generates only CheckEventTest from the existing constraints
    • Attaches them to the task
    """

    # --------------------------------------------------------------------- #
    #  INIT
    # --------------------------------------------------------------------- #

    async def add_tests_to_tasks(self, tasks: list[Task]) -> list[Task]:
        for task in tasks:
            if not task.use_case:
                logger.debug("Task %s has no UseCase. Skipping.", task.id)
                continue

            try:
                self._generate_tests_for_task(task)
            except Exception as exc:
                logger.error("Failed to generate tests for Task=%s: %s", task.id, exc)
                logger.debug("Exception details: %s, %r", type(exc).__name__, exc)
                # Don't raise - continue with other tasks instead of breaking the entire validator
                continue

        return tasks

    # --------------------------------------------------------------------- #
    #  INTERNAL HELPERS
    # --------------------------------------------------------------------- #

    def _generate_tests_for_task(self, task: Task) -> None:
        """
        Build **one** `CheckEventTest` per Task with an `event_criteria`
        that already matches the ValidationCriteria structure expected by
        the Event classes.

        • Every constraint triplet (field / operator / value) is merged into
        a single dict:
            - If the operator is ``equals``  → just the raw value.
            - Otherwise                       → {"operator": op, "value": val}
        """
        constraints: list[dict[str, Any]] = task.use_case.constraints or []
        criteria: dict[str, Any] = {}
        if not constraints:
            test_def = {
                "type": "CheckEventTest",
                "event_name": task.use_case.name,
                "event_criteria": {},
            }

            check_event_test = CheckEventTest(**test_def)
            return task.tests.append(check_event_test)

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

        test_def = {
            "type": "CheckEventTest",
            "event_name": task.use_case.name,
            "event_criteria": criteria,
        }

        try:
            check_event_test = CheckEventTest(**test_def)  # Pydantic validation
            task.tests.append(check_event_test)
            logger.debug(
                "Added CheckEventTest to Task %s with %d criteria",
                task.id,
                len(criteria),
            )
        except Exception as exc:
            logger.error(
                "Failed to instantiate CheckEventTest for Task %s: %s",
                task.id,
                exc,
            )
