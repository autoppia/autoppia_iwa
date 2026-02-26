from enum import Enum
from typing import Any

from pydantic import BaseModel

# ============================================================================
# ENUMS AND MODELS
# ============================================================================


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


# ============================================================================
# STRING NORMALIZATION HELPERS
# ============================================================================

_STRIP = str.maketrans("", "", ".,")


def _normalize(s: str) -> str:
    """lowercase + sin ',' ni '.' al inicio/fin ni en medio"""
    return s.translate(_STRIP).lower().strip()


# ============================================================================
# VALIDATION HELPERS - SIMPLE CRITERIA
# ============================================================================


def _validate_simple_criterion(actual_value: Any, criterion: Any) -> bool:
    """Validate simple criterion (not CriterionValue)."""
    if isinstance(actual_value, bool) and isinstance(criterion, bool):
        return actual_value is criterion
    if isinstance(actual_value, str) and isinstance(criterion, str):
        return _normalize(criterion) in _normalize(actual_value)
    return actual_value == criterion


# ============================================================================
# VALIDATION HELPERS - EQUALS/NOT_EQUALS
# ============================================================================


def _validate_equals(actual_value: Any, actual_norm: Any, val: Any, val_norm: Any) -> bool:
    """Validate EQUALS operator."""
    if isinstance(actual_value, str) and isinstance(val, str):
        return actual_norm == val_norm
    return actual_value == val


def _validate_not_equals(actual_value: Any, actual_norm: Any, val: Any, val_norm: Any) -> bool:
    """Validate NOT_EQUALS operator."""
    if isinstance(actual_value, str) and isinstance(val, str):
        return actual_norm != val_norm
    return actual_value != val


# ============================================================================
# VALIDATION HELPERS - CONTAINS/NOT_CONTAINS
# ============================================================================


def _check_list_contains(actual_value: list, val_norm: Any) -> bool:
    """Check if list contains value."""
    return any((_normalize(item) if isinstance(item, str) else item) == val_norm or (isinstance(item, str) and val_norm in _normalize(item)) for item in actual_value)


def _check_list_not_contains(actual_value: list, val_norm: Any) -> bool:
    """Check if list does not contain value."""
    return all((_normalize(item) if isinstance(item, str) else item) != val_norm and not (isinstance(item, str) and val_norm in _normalize(item)) for item in actual_value)


def _validate_contains(actual_value: Any, actual_norm: Any, val: Any, val_norm: Any) -> bool:
    """Validate CONTAINS operator."""
    if isinstance(actual_value, list):
        return _check_list_contains(actual_value, val_norm)
    if isinstance(actual_value, str) and isinstance(val, str):
        return val_norm in actual_norm
    return False


def _validate_not_contains(actual_value: Any, actual_norm: Any, val: Any, val_norm: Any) -> bool:
    """Validate NOT_CONTAINS operator."""
    if isinstance(actual_value, list):
        return _check_list_not_contains(actual_value, val_norm)
    if isinstance(actual_value, str) and isinstance(val, str):
        return val_norm not in actual_norm
    return False


# ============================================================================
# VALIDATION HELPERS - NUMERIC COMPARISONS
# ============================================================================


def _validate_greater_than(actual_value: Any, val: Any) -> bool:
    """Validate GREATER_THAN operator."""
    return actual_value is not None and actual_value > val


def _validate_less_than(actual_value: Any, val: Any) -> bool:
    """Validate LESS_THAN operator."""
    return actual_value is not None and actual_value < val


def _validate_greater_equal(actual_value: Any, val: Any) -> bool:
    """Validate GREATER_EQUAL operator."""
    return actual_value is not None and actual_value >= val


def _validate_less_equal(actual_value: Any, val: Any) -> bool:
    """Validate LESS_EQUAL operator."""
    return actual_value is not None and actual_value <= val


# ============================================================================
# VALIDATION HELPERS - IN_LIST/NOT_IN_LIST
# ============================================================================


def _normalize_list_for_comparison(val: list) -> list:
    """Normalize list values for comparison."""
    return [_normalize(v) if isinstance(v, str) else v for v in val]


def _validate_in_list(actual_value: Any, actual_norm: Any, val: list, criterion: CriterionValue) -> bool:
    """Validate IN_LIST operator."""
    if actual_value is None or not isinstance(val, list):
        return False

    if isinstance(actual_value, bool):
        return actual_value in criterion.value
    if any(isinstance(v, bool) for v in criterion.value):
        return actual_value in criterion.value
    if isinstance(actual_value, str):
        return actual_norm in _normalize_list_for_comparison(val)
    return actual_value in val


def _validate_not_in_list(actual_value: Any, actual_norm: Any, val: list, criterion: CriterionValue) -> bool:
    """Validate NOT_IN_LIST operator."""
    if actual_value is None or not isinstance(val, list):
        return False

    if isinstance(actual_value, bool):
        return actual_value not in criterion.value
    if any(isinstance(v, bool) for v in criterion.value):
        return actual_value not in criterion.value
    if isinstance(actual_value, str):
        return actual_norm not in _normalize_list_for_comparison(val)
    return actual_value not in val


# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================


def validate_criterion(actual_value: Any, criterion: Any | CriterionValue) -> bool:
    """
    Validate a single criterion against an actual value.
    Antes de comparar strings ⇒ se pasa a minúsculas y se quitan ',' y '.'
    """
    if not isinstance(criterion, CriterionValue):
        return _validate_simple_criterion(actual_value, criterion)

    actual_norm = _normalize(actual_value) if isinstance(actual_value, str) else actual_value
    val = criterion.value
    val_norm = _normalize(val) if isinstance(val, str) else val
    op = criterion.operator

    if op == ComparisonOperator.EQUALS:
        return _validate_equals(actual_value, actual_norm, val, val_norm)
    if op == ComparisonOperator.NOT_EQUALS:
        return _validate_not_equals(actual_value, actual_norm, val, val_norm)
    if op == ComparisonOperator.CONTAINS:
        return _validate_contains(actual_value, actual_norm, val, val_norm)
    if op == ComparisonOperator.NOT_CONTAINS:
        return _validate_not_contains(actual_value, actual_norm, val, val_norm)
    if op == ComparisonOperator.GREATER_THAN:
        return _validate_greater_than(actual_value, val)
    if op == ComparisonOperator.LESS_THAN:
        return _validate_less_than(actual_value, val)
    if op == ComparisonOperator.GREATER_EQUAL:
        return _validate_greater_equal(actual_value, val)
    if op == ComparisonOperator.LESS_EQUAL:
        return _validate_less_equal(actual_value, val)
    if op == ComparisonOperator.IN_LIST:
        return _validate_in_list(actual_value, actual_norm, val, criterion)
    if op == ComparisonOperator.NOT_IN_LIST:
        return _validate_not_in_list(actual_value, actual_norm, val, criterion)

    return False
