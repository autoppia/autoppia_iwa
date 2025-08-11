import random
from collections.abc import Callable
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from ..criterion_helper import ComparisonOperator
from .data import (
    CALENDAR_NAMES,
    DESCRIPTIONS,
    EVENT_TITLES,
    FIELD_OPERATORS_ADD_EVENT_MAP,
    FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP,
    FIELD_OPERATORS_CHOOSE_CALENDAR_MAP,
    FIELD_OPERATORS_CLICK_CELL_MAP,
    FIELD_OPERATORS_CREATE_CALENDAR_MAP,
    FIELD_OPERATORS_DELETE_ADD_EVENT_MAP,
)


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    Handles various data types and operators robustly.
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
        valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
        return random.choice(valid) if valid else None

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        delta = random.uniform(0.5, 2.0) if isinstance(field_value, float) else random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - delta
        if operator == ComparisonOperator.LESS_THAN:
            return field_value + delta
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return field_value

    return None


def _generate_time_constraint(field: str, operator: ComparisonOperator, use_24h: bool, start_hour: int | None = None, start_minute: int | None = None) -> dict[str, Any]:
    """Helper function to generate time constraints in either 24h or AM/PM format."""
    if field == "start_time":
        hour = random.randint(0, 23)
        minute = random.choice([0, 30])
    else:  # end_time
        hour = start_hour + random.randint(0, 2)
        minute = random.choice([0, 30])
        if hour == start_hour and minute <= start_minute:
            minute = 30 if start_minute == 0 else 0
            if minute < start_minute:
                hour += 1
        hour %= 24

    if use_24h:
        time_value = f"{hour:02d}:{minute:02d}"
    else:
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        time_value = f"{display_hour}:{minute:02d} {am_pm}"

    return {"constraint": create_constraint_dict(field, operator, time_value), "hour": hour, "minute": minute}


def _generate_constraints_for_event(field_map: dict[str, dict[str, Any]], operators_map: dict[str, list], special_handlers: dict[str, Callable] | None = None) -> list[dict[str, Any]]:
    """Generic function to generate constraints based on a field map."""
    constraints_list = []
    context = {}
    if special_handlers is None:
        special_handlers = {}

    for field, config in field_map.items():
        if field in special_handlers:
            constraints_list.extend(special_handlers[field](context))
            continue

        operator = ComparisonOperator(random.choice(operators_map[field]))
        field_value_source = config.get("values")
        field_value = random.choice(field_value_source) if field_value_source else None

        if "dataset_generator" in config:
            dataset = config["dataset_generator"]()
            # For date fields, we need a field_value to compare against
            if field_value is None and dataset:
                field_value = random.choice(dataset)[field]
        else:
            dataset = [{config.get("dataset_key", field): val} for val in field_value_source]

        value = _generate_constraint_value(operator, field_value, field, dataset)

        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
            if config.get("provides_context"):
                context[field] = value

    return constraints_list


def _handle_time_constraints(context: dict) -> list[dict[str, Any]]:
    """Handler for start and end time constraints."""
    use_24h = random.choice([True, False])
    start_op = ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP["start_time"]))
    start_time_data = _generate_time_constraint("start_time", start_op, use_24h)

    end_op = ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP["end_time"]))
    end_time_data = _generate_time_constraint("end_time", end_op, use_24h, start_hour=start_time_data["hour"], start_minute=start_time_data["minute"])
    return [start_time_data["constraint"], end_time_data["constraint"]]


def _handle_cell_click_hour(context: dict) -> list[dict[str, Any]]:
    """Handler for hour constraint in cell click event."""
    source_value = context.get("source")
    if source_value and "month" not in source_value:
        hour_op = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP["hour"]))
        hour_value = random.randint(0, 23)
        return [create_constraint_dict("hour", hour_op, hour_value)]
    return []


def generate_create_calendar_constraints() -> list[dict[str, Any]]:
    """Generate constraints for creating a calendar."""
    field_map = {
        "name": {"values": CALENDAR_NAMES},
        "description": {"values": DESCRIPTIONS},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CREATE_CALENDAR_MAP)


def generate_choose_calendar_constraints() -> list[dict[str, Any]]:
    """Generate constraints for selecting/deselecting a calendar."""
    field_map = {
        "calendar_name": {"values": CALENDAR_NAMES},
        "selected": {"values": [False]},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CHOOSE_CALENDAR_MAP)


def generate_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding a calendar event."""
    field_map = {
        "title": {"values": EVENT_TITLES},
        "calendar": {"values": CALENDAR_NAMES},
        "date": {"dataset_generator": lambda: [{"date": date.today() + timedelta(days=i)} for i in range(-30, 60)]},
        "time": {},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_ADD_EVENT_MAP, {"time": _handle_time_constraints})


def generate_cell_clicked_constraints() -> list[dict[str, Any]]:
    """Generate constraints for clicking a calendar cell."""
    field_map = {
        "source": {"values": ["month-view", "week-view", "day-view", "5 days-view"], "provides_context": True},
        "date": {"dataset_generator": lambda: [{"date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=i)} for i in range(-30, 60)]},
        "view": {"values": ["Month", "Week", "Day", "5 days"]},
        "hour": {},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CLICK_CELL_MAP, {"hour": _handle_cell_click_hour})


def generate_cancel_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for canceling event creation."""
    field_map = {
        "source": {"values": ["event-modal", "month-view", "week-view", "day-view", "5 days-view"]},
        "date": {"dataset_generator": lambda: [{"date": date.today() + timedelta(days=i)} for i in range(-30, 60)]},
        "title": {"values": EVENT_TITLES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP)


def generate_delete_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for deleting a calendar event."""
    field_map = {
        "source": {"values": ["event-modal", "month-view", "week-view", "day-view", "5 days-view"]},
        "date": {"dataset_generator": lambda: [{"date": date.today() + timedelta(days=i)} for i in range(-30, 60)]},
        "event_title": {"values": EVENT_TITLES},
        "calendar": {"values": CALENDAR_NAMES},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_DELETE_ADD_EVENT_MAP)
