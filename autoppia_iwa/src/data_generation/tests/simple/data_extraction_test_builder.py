from __future__ import annotations

from typing import Any

from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest

from .utils import enum_to_raw_recursive


def build_data_extraction_test(constraints: list[dict[str, Any]]) -> DataExtractionTest:
    """Build a DataExtractionTest from use-case constraints."""
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

    expected_answer: Any = None
    if len(criteria_dict) == 1:
        only_val = next(iter(criteria_dict.values()))
        if not isinstance(only_val, dict):
            expected_answer = only_val

    return DataExtractionTest(
        expected_answer=expected_answer,
        answer_criteria=criteria_dict or None,
    )
