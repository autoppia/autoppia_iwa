# autoppia_iwa/src/demo_webs/projects/autolist_12/generation_functions.py
import random
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    DATES_QUICK_OPTIONS,
    FIELD_OPERATORS_SELECT_DATE_MAP,
    FIELD_OPERATORS_SELECT_PRIORITY_MAP,
    FIELD_OPERATORS_TASK_MAP,
    FIELD_OPERATORS_TEAM_CREATED_MAP,
    FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP,
    FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP,
    PRIORITIES,
    ROLES,
    TASKS,
    TEAM_MEMBERS_OPTIONS,
    TEAMS,
)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, source_key: str, dataset: list[dict[str, Any]]) -> Any:
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
        valid = [v[source_key] for v in dataset if v.get(source_key) and v.get(source_key) != field_value]
        return random.choice(valid) if valid else None

    if operator == ComparisonOperator.CONTAINS:
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value
    elif operator == ComparisonOperator.NOT_CONTAINS:
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback
    elif operator == ComparisonOperator.IN_LIST:
        all_values = []
        for v in dataset:
            if source_key in v:
                val = v.get(source_key)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = []
        for v in dataset:
            if source_key in v:
                val = v.get(source_key)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    if isinstance(field_value, int | float):
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - delta
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + delta
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return field_value

    return None


def _generate_constraints_for_event(field_map: dict[str, dict[str, Any]], operators_map: dict[str, list]) -> list[dict[str, Any]]:
    """Generic function to generate constraints based on a field map."""
    constraints_list = []
    sample_data = random.choice(field_map.get("_dataset", [{}]))

    for field, config in field_map.items():
        if field == "_dataset":
            continue

        operator = ComparisonOperator(random.choice(operators_map[field]))
        source_key = config.get("source_key", field)
        dataset = config.get("dataset", [])
        if dataset and all(not isinstance(item, dict) for item in dataset):
            dataset = [{source_key: item} for item in dataset]
        field_value = sample_data.get(source_key) or random.choice(dataset)[source_key] if dataset else None

        if field_value is None and not config.get("is_date"):
            if "values" in config:
                field_value = random.choice(config["values"])
            else:
                continue

        if config.get("is_date"):
            today = datetime.today()
            start_of_month = today.replace(day=1)
            next_month = today.replace(year=today.year + 1, month=1, day=1) if today.month == 12 else today.replace(month=today.month + 1, day=1)
            days_in_month = (next_month - start_of_month).days
            random_day = random.randint(1, days_in_month)
            field_value = start_of_month + timedelta(days=random_day - 1)
            if operator == ComparisonOperator.GREATER_THAN:
                min_day = min(field_value.day + 1, days_in_month)
                field_value = field_value.replace(day=min_day)
            elif operator == ComparisonOperator.LESS_THAN:
                max_day = max(field_value.day - 1, 1)
                field_value = field_value.replace(day=max_day)
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
                pass  # already set
            elif operator == ComparisonOperator.NOT_EQUALS:
                alt_day = field_value.day + 1 if field_value.day < days_in_month else field_value.day - 1
                field_value = field_value.replace(day=alt_day)
            value = field_value.date()
        else:
            value = _generate_constraint_value(operator, field_value, source_key, dataset)

        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list


def generate_select_date_for_task_constraints() -> list[dict[str, Any]]:
    """Generate constraints for selecting a date for a task."""
    field_map = {"_dataset": TASKS, "date": {"is_date": True}} if random.choice([True, False]) else {"_dataset": TASKS, "quick_option": {"values": DATES_QUICK_OPTIONS}}
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_SELECT_DATE_MAP)


def generate_select_task_priority_constraints() -> list[dict[str, Any]]:
    """Generate constraints for selecting a task priority."""
    field_map = {
        "priority": {"dataset": PRIORITIES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_SELECT_PRIORITY_MAP)


def generate_task_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding or updating a task."""
    field_map = {
        "_dataset": TASKS,
        "name": {"dataset": TASKS},
        "description": {"dataset": TASKS},
        "date": {"is_date": True},
        "priority": {"dataset": PRIORITIES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TASK_MAP)


def generate_team_members_added_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding team members."""
    field_map = {
        "_dataset": TEAM_MEMBERS_OPTIONS,
        "members": {"source_key": "value", "dataset": TEAM_MEMBERS_OPTIONS},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP)


def generate_team_role_assigned_constraints() -> list[dict[str, Any]]:
    """Generate constraints for assigning a role to a team member."""
    field_map = {
        "_dataset": TEAMS,
        "member": {"source_key": "label", "dataset": TEAM_MEMBERS_OPTIONS},
        "role": {"source_key": "label", "dataset": ROLES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP)


def generate_team_created_constraints() -> list[dict[str, Any]]:
    """Generate constraints for creating a team."""
    field_map = {
        "_dataset": TEAMS,
        "team_name": {"source_key": "name", "dataset": TEAMS},
        "team_description": {"source_key": "description", "dataset": TEAMS},
        "member_name": {"source_key": "label", "dataset": TEAM_MEMBERS_OPTIONS},
        "member_email": {"source_key": "value", "dataset": TEAM_MEMBERS_OPTIONS},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_TEAM_CREATED_MAP)
