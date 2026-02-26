from enum import Enum
from typing import Any

from pydantic import BaseModel


class ComparisonOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


class CriterionValue(BaseModel):
    value: Any
    operator: ComparisonOperator = ComparisonOperator.EQUALS


_STRIP = str.maketrans("", "", ".,")


def _normalize(s: str) -> str:
    """lowercase + sin ',' ni '.' al inicio/fin ni en medio"""
    return s.translate(_STRIP).lower().strip()


def validate_criterion(actual_value: Any, criterion: Any | CriterionValue) -> bool:
    """
    Validate a single criterion against an actual value.
    Antes de comparar strings ⇒ se pasa a minúsculas y se quitan ',' y '.'
    """
    # ───── helper para strings ─────
    actual_norm = _normalize(actual_value) if isinstance(actual_value, str) else actual_value

    if not isinstance(criterion, CriterionValue):
        if isinstance(actual_value, bool) and isinstance(criterion, bool):
            return actual_value is criterion
        if isinstance(actual_value, str) and isinstance(criterion, str):
            return _normalize(criterion) in actual_norm
        return actual_value == criterion

    val = criterion.value
    val_norm = _normalize(val) if isinstance(val, str) else val

    op = criterion.operator

    if op == ComparisonOperator.EQUALS:
        if isinstance(actual_value, str) and isinstance(val, str):
            return actual_norm == val_norm
        return actual_value == val

    if op == ComparisonOperator.NOT_EQUALS:
        if isinstance(actual_value, str) and isinstance(val, str):
            return actual_norm != val_norm
        return actual_value != val

    if op == ComparisonOperator.CONTAINS:
        if isinstance(actual_value, list):
            return any((_normalize(item) if isinstance(item, str) else item) == val_norm or (isinstance(item, str) and val_norm in _normalize(item)) for item in actual_value)
        if isinstance(actual_value, str) and isinstance(val, str):
            return val_norm in actual_norm
        return False

    if op == ComparisonOperator.NOT_CONTAINS:
        if isinstance(actual_value, list):
            return all((_normalize(item) if isinstance(item, str) else item) != val_norm and not (isinstance(item, str) and val_norm in _normalize(item)) for item in actual_value)
        if isinstance(actual_value, str) and isinstance(val, str):
            return val_norm not in actual_norm
        return False

    if op == ComparisonOperator.GREATER_THAN:
        return actual_value is not None and actual_value > val

    if op == ComparisonOperator.LESS_THAN:
        return actual_value is not None and actual_value < val

    if op == ComparisonOperator.GREATER_EQUAL:
        return actual_value is not None and actual_value >= val

    if op == ComparisonOperator.LESS_EQUAL:
        return actual_value is not None and actual_value <= val

    if op == ComparisonOperator.IN_LIST:
        if actual_value is None or not isinstance(val, list):
            return False
        # Handle boolean values
        if isinstance(actual_value, bool):
            return actual_value in criterion.value
        if any(isinstance(v, bool) for v in criterion.value):
            return actual_value in criterion.value
        if isinstance(actual_value, str):
            return actual_norm in [_normalize(v) if isinstance(v, str) else v for v in val]
        return actual_value in val

    if op == ComparisonOperator.NOT_IN_LIST:
        if actual_value is None or not isinstance(val, list):
            return False
        # Handle boolean values
        if isinstance(actual_value, bool):
            return actual_value not in criterion.value
        if any(isinstance(v, bool) for v in criterion.value):
            return actual_value not in criterion.value
        if isinstance(actual_value, str):
            return actual_norm not in [_normalize(v) if isinstance(v, str) else v for v in val]
        return actual_value not in val

    return False
