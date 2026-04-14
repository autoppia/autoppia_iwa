from __future__ import annotations

from typing import Any

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest, DataExtractionTest
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
            criteria: dict[str, Any] = {}
            if not constraints:
                test_def = {
                    "type": "CheckEventTest",
                    "event_name": task.use_case.name,
                    "event_criteria": {},
                }

                check_event_test = CheckEventTest(**test_def)
                task.tests.append(check_event_test)
            else:
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

        # Optionally attach a DataExtractionTest for data-extraction style tasks
        if self._should_attach_data_extraction_test(task, test_types=test_types, data_extraction_use_cases=data_extraction_use_cases):
            try:
                # Always build criteria dict from constraints: { field_name: value } or { field_name: { operator, value } }.
                # This keeps the verify field name visible and uses answer_criteria (no expected_answer).
                criteria_dict: dict[str, Any] = {}
                for raw in constraints:
                    clean = enum_to_raw_recursive(raw)
                    field = clean.get("field")
                    operator = clean.get("operator", "equals")
                    value = clean.get("value")
                    if field is None:
                        continue
                    if operator == "equals":
                        criteria_dict[field] = value
                    else:
                        criteria_dict[field] = {"operator": operator, "value": value}
                # Set expected_answer from the single verify-field value so DataExtractionTest can compare agent's extracted_data
                expected_answer: Any = None
                if len(criteria_dict) == 1:
                    only_val = next(iter(criteria_dict.values()))
                    if not isinstance(only_val, dict):
                        expected_answer = only_val
                data_test = DataExtractionTest(
                    expected_answer=expected_answer,
                    answer_criteria=criteria_dict or None,
                )

                task.tests.append(data_test)
                logger.debug("Added DataExtractionTest to Task %s", task.id)
            except Exception as exc:
                logger.error("Failed to instantiate DataExtractionTest for Task %s: %s", task.id, exc)
