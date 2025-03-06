from enum import Enum
from typing import Any, Union

from pydantic import BaseModel

# ================ Comparison Operators for Advanced Validation ================


class ComparisonOperator(str, Enum):
    """Operators for flexible criterion comparison"""

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
    """A validation criterion with its comparison operator"""

    value: Any
    operator: ComparisonOperator = ComparisonOperator.EQUALS


# ================ Helper Methods for Criterion Validation ================


def validate_criterion(actual_value: Any, criterion: Union[Any, CriterionValue]) -> bool:
    """
    Validate a single criterion against an actual value

    Args:
        actual_value: The value from the event to validate
        criterion: Either a simple value or a CriterionValue with operator

    Returns:
        True if the criterion is met, False otherwise
    """
    # If criterion is a simple value, use default comparison
    if not isinstance(criterion, CriterionValue):
        if isinstance(actual_value, str) and isinstance(criterion, str):
            return criterion.lower() in actual_value.lower()
        return actual_value == criterion

    # If criterion has an operator, apply according to type
    if criterion.operator == ComparisonOperator.EQUALS:
        if isinstance(actual_value, str) and isinstance(criterion.value, str):
            return actual_value.lower() == criterion.value.lower()
        return actual_value == criterion.value

    elif criterion.operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(actual_value, str) and isinstance(criterion.value, str):
            return actual_value.lower() != criterion.value.lower()
        return actual_value != criterion.value

    elif criterion.operator == ComparisonOperator.CONTAINS:
        if not isinstance(actual_value, str) or not isinstance(criterion.value, str):
            return False
        return criterion.value.lower() in actual_value.lower()

    elif criterion.operator == ComparisonOperator.NOT_CONTAINS:
        if not isinstance(actual_value, str) or not isinstance(criterion.value, str):
            return False
        return criterion.value.lower() not in actual_value.lower()

    elif criterion.operator == ComparisonOperator.GREATER_THAN:
        if actual_value is None:
            return False
        return actual_value > criterion.value

    elif criterion.operator == ComparisonOperator.LESS_THAN:
        if actual_value is None:
            return False
        return actual_value < criterion.value

    elif criterion.operator == ComparisonOperator.GREATER_EQUAL:
        if actual_value is None:
            return False
        return actual_value >= criterion.value

    elif criterion.operator == ComparisonOperator.LESS_EQUAL:
        if actual_value is None:
            return False
        return actual_value <= criterion.value

    elif criterion.operator == ComparisonOperator.IN_LIST:
        if actual_value is None or not isinstance(criterion.value, list):
            return False
        if isinstance(actual_value, str):
            return actual_value.lower() in [v.lower() if isinstance(v, str) else v for v in criterion.value]
        return actual_value in criterion.value

    elif criterion.operator == ComparisonOperator.NOT_IN_LIST:
        if actual_value is None or not isinstance(criterion.value, list):
            return False
        if isinstance(actual_value, str):
            return actual_value.lower() not in [v.lower() if isinstance(v, str) else v for v in criterion.value]
        return actual_value not in criterion.value

    return False
