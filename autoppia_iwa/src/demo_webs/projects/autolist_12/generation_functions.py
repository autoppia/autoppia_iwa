# autoppia_iwa/src/demo_webs/projects/autolist_12/generation_functions.py
import random
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    FIELD_OPERATORS_ADD_TASK_CLICKED_MAP,
    FIELD_OPERATORS_CANCEL_TASK_MAP,
    FIELD_OPERATORS_COMPLETE_TASK_MAP,
    FIELD_OPERATORS_DELETE_TASK_MAP,
    FIELD_OPERATORS_EDIT_MODAL_MAP,
    FIELD_OPERATORS_SELECT_DATE_MAP,
    FIELD_OPERATORS_SELECT_PRIORITY_MAP,
    FIELD_OPERATORS_TASK_ADDED_MAP,
    TASKS_DATA,
)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    """
    if isinstance(field_value, datetime | date):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        valid_values = [d.get(field) for d in dataset if d.get(field) is not None and d.get(field) != field_value]
        return random.choice(valid_values) if valid_values else "a different value"

    if isinstance(field_value, str):
        if operator == ComparisonOperator.CONTAINS:
            if len(field_value) > 2:
                start = random.randint(0, len(field_value) - 2)
                end = random.randint(start + 1, len(field_value))
                return field_value[start:end]
            return field_value
        if operator == ComparisonOperator.NOT_CONTAINS:
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            for _ in range(100):
                test_str = "".join(random.choice(alphabet) for _ in range(3))
                if test_str.lower() not in field_value.lower():
                    return test_str
            return "xyz"  # fallback

    if isinstance(field_value, int | float):
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - delta
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + delta
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return field_value

    return None


def _generate_constraints_from_map(
    field_operator_map: dict[str, list[str]],
    sample_data: dict[str, Any],
    dataset: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Generic function to generate a list of constraints from a field-operator map.
    """
    if dataset is None:
        dataset = TASKS_DATA

    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(field_operator_map.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = field_operator_map.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = sample_data.get(field)
        if field_value is None:
            continue

        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            # Map python field names to event field names if they differ
            # e.g., is_editing -> isEditing
            event_field_name = "".join(word.capitalize() for word in field.split("_"))
            event_field_name = event_field_name[0].lower() + event_field_name[1:]
            constraints_list.append(create_constraint_dict(event_field_name, operator, value))

    return constraints_list


def generate_add_task_clicked_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_ADD_TASK_CLICKED_MAP, sample_task)


def generate_select_date_for_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_SELECT_DATE_MAP, sample_task)


def generate_select_task_priority_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_SELECT_PRIORITY_MAP, sample_task)


def generate_task_added_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_TASK_ADDED_MAP, sample_task)


def generate_cancel_task_creation_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    # Rename keys to match event definition
    sample_task["currentName"] = sample_task.pop("name", "")
    sample_task["currentDescription"] = sample_task.pop("description", "")
    sample_task["isEditing"] = sample_task.pop("is_editing", False)
    return _generate_constraints_from_map(FIELD_OPERATORS_CANCEL_TASK_MAP, sample_task)


def generate_edit_task_modal_opened_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_EDIT_MODAL_MAP, sample_task)


def generate_complete_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_COMPLETE_TASK_MAP, sample_task)


def generate_delete_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_DELETE_TASK_MAP, sample_task)
