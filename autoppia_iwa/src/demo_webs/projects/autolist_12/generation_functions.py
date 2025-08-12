# autoppia_iwa/src/demo_webs/projects/autolist_12/generation_functions.py
import random
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    FIELD_OPERATORS_CANCEL_TASK_MAP,
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
    are_optional=False,
) -> list[dict[str, Any]]:
    """
    Generic function to generate a list of constraints from a field-operator map.
    """
    if dataset is None:
        dataset = TASKS_DATA

    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(field_operator_map.keys())
    if are_optional:
        num_constraints = random.randint(1, len(possible_fields))
        selected_fields = random.sample(possible_fields, num_constraints)
    else:
        selected_fields = possible_fields

    for field in selected_fields:
        allowed_ops = field_operator_map.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = sample_data.get(field)
        if field_value is None:
            continue
        if field == "selected_date" or "date" in field:
            # Special case for date fields, pick a random date from this month
            today = datetime.now().date()
            start_of_month = today.replace(day=1)
            next_month = today.replace(year=today.year + 1, month=1, day=1) if today.month == 12 else today.replace(month=today.month + 1, day=1)
            days_in_month = (next_month - start_of_month).days
            random_day = random.randint(0, days_in_month - 1)
            field_value = start_of_month + timedelta(days=random_day)
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list


def generate_select_date_for_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_SELECT_DATE_MAP, sample_task)


def generate_select_task_priority_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA).copy()
    priority = sample_task.get("priority")
    if priority:
        sample_task["label"] = f"Priority {priority}"
    return _generate_constraints_from_map(FIELD_OPERATORS_SELECT_PRIORITY_MAP, sample_task)


def generate_task_added_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_TASK_ADDED_MAP, sample_task)


def generate_cancel_task_creation_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA).copy()
    # Rename keys to match event validation criteria
    sample_task["current_name"] = sample_task.pop("name", "")
    sample_task["current_description"] = sample_task.pop("description", "")
    sample_task["selected_date"] = sample_task.pop("date", None)
    return _generate_constraints_from_map(FIELD_OPERATORS_CANCEL_TASK_MAP, sample_task)


def generate_edit_task_modal_opened_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_EDIT_MODAL_MAP, sample_task)


def generate_complete_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_TASK_ADDED_MAP, sample_task)


def generate_delete_task_constraints() -> list[dict[str, Any]]:
    sample_task = random.choice(TASKS_DATA)
    return _generate_constraints_from_map(FIELD_OPERATORS_TASK_ADDED_MAP, sample_task)
