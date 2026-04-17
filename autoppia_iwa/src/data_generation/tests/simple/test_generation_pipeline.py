from __future__ import annotations

from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task

from .data_extraction_test_builder import build_data_extraction_test
from .event_test_builder import build_check_event_test


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

    def add_tests_to_tasks(
        self,
        tasks: list[Task],
        test_types: str = "event_only",
        data_extraction_use_cases: list[str] | None = None,
    ) -> list[Task]:
        for task in tasks:
            if not task.use_case:
                logger.debug("Task %s has no UseCase. Skipping.", task.id)
                continue

            try:
                self._generate_tests_for_task(
                    task,
                    test_types=test_types,
                    data_extraction_use_cases=data_extraction_use_cases,
                )
            except Exception as exc:
                logger.error("Failed to generate tests for Task=%s: %s", task.id, exc)
                logger.debug("Exception details: %s, %r", type(exc).__name__, exc)
                # Don't raise - continue with other tasks instead of breaking the entire validator
                continue

        return tasks

    # --------------------------------------------------------------------- #
    #  INTERNAL HELPERS
    # --------------------------------------------------------------------- #

    def _should_attach_data_extraction_test(self, task: Task, test_types: str, data_extraction_use_cases: list[str] | None) -> bool:
        if test_types != "data_extraction_only":
            return False
        use_case = task.use_case
        if not use_case:
            return False
        return not (data_extraction_use_cases is not None and use_case.name not in data_extraction_use_cases)

    def _generate_tests_for_task(
        self,
        task: Task,
        *,
        test_types: str = "event_only",
        data_extraction_use_cases: list[str] | None = None,
    ) -> None:
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

        # Optionally attach a CheckEventTest (event-based backend validation)
        if test_types == "event_only":
            try:
                check_event_test = build_check_event_test(task, constraints)
                task.tests.append(check_event_test)
                logger.debug(
                    "Added CheckEventTest to Task %s with %d criteria",
                    task.id,
                    len(check_event_test.event_criteria),
                )
            except Exception as exc:
                logger.error(
                    "Failed to instantiate CheckEventTest for Task %s: %s",
                    task.id,
                    exc,
                )

        # Optionally attach a DataExtractionTest for data-extraction style tasks
        if self._should_attach_data_extraction_test(task, test_types=test_types, data_extraction_use_cases=data_extraction_use_cases):
            try:
                data_test = build_data_extraction_test(constraints)
                task.tests.append(data_test)
                logger.debug("Added DataExtractionTest to Task %s", task.id)
            except Exception as exc:
                logger.error("Failed to instantiate DataExtractionTest for Task %s: %s", task.id, exc)
