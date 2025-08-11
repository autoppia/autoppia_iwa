import random
from datetime import datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from ..criterion_helper import ComparisonOperator
from .data import (
    CALENDAR_NAMES,
    DESCRIPTIONS,
    EVENT_TITLES,
    FIELD_OPERATORS_ADD_EVENT_MAP,
    FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP,
    FIELD_OPERATORS_CHOOSE_CALENDER_MAP,
    FIELD_OPERATORS_CLICK_CELL_MAP,
    FIELD_OPERATORS_CREATE_CALENDER_MAP,
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

    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        elif operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        elif operator in {
            ComparisonOperator.GREATER_EQUAL,
            ComparisonOperator.LESS_EQUAL,
            ComparisonOperator.EQUALS,
        }:
            return field_value
        elif operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(field_value, str):
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else None
        elif isinstance(field_value, list):
            # For lists, find a value in dataset that is not equal to the list
            valid = []
            for v in dataset:
                val = v.get(field)
                if val and val != field_value:
                    if isinstance(val, list):
                        valid.extend([item for item in val if item not in field_value])
                    else:
                        valid.append(val)
            return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

    elif operator == ComparisonOperator.IN_LIST:
        all_values = []
        for v in dataset:
            if field in v:
                val = v.get(field)
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
            if field in v:
                val = v.get(field)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        base = field_value
        if isinstance(base, int | float):
            # Generic numeric logic
            delta = random.uniform(0.5, 2.0) if isinstance(base, float) else random.randint(1, 5)
            if operator == ComparisonOperator.GREATER_THAN:
                return base - delta
            elif operator == ComparisonOperator.LESS_THAN:
                return base + delta
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                return base

    # Fallback: return None
    return None


def _generate_time_constraint(field: str, operator: ComparisonOperator, start_hour: int | None = None, start_minute: int | None = None) -> dict[str, Any]:
    """Helper function to generate time constraints in either 24h or AM/PM format."""
    use_24h = random.choice([True, False])

    # For 24-hour format: 1-24, for AM/PM: 1-12
    hour = random.randint(1, 24 if use_24h else 12) if field == "start_time" else None
    minute = random.choice([0, 30]) if field == "start_time" else None

    # Use the provided start values for end_time
    if field == "end_time":
        if use_24h:
            hour = start_hour + random.randint(0, 3)
            minute = random.choice([0, 30])

            # If same hour, ensure minutes are later
            if hour == start_hour and minute <= start_minute:
                minute = 30 if start_minute == 0 else 0
                if minute < start_minute:  # Rolled over to next hour
                    hour += 1

            time_value = f"{hour}:{minute:02d}"
        else:
            # For AM/PM format
            start_is_am = start_hour < 12
            end_is_am = start_is_am and random.choice([True, True, False])  # Bias toward same period

            if start_is_am and not end_is_am:
                # If start is AM and end is PM, end is always later
                hour = random.randint(1, 12)
                minute = random.choice([0, 30])
            elif not start_is_am and end_is_am:
                # Cannot have PM to AM on same day, so make it same period
                end_is_am = False
                hour = start_hour + random.randint(0, 3)
                if hour > 12:
                    hour = hour % 12 or 12
                minute = random.choice([0, 30])
            else:
                # Same period (AM-AM or PM-PM)
                hour = start_hour + random.randint(0, 3)
                if hour > 12:
                    hour = hour % 12 or 12
                minute = random.choice([0, 30])

                # If same hour, ensure minutes are later
                if hour == start_hour and minute <= start_minute:
                    minute = 30 if start_minute == 0 else 0
                    if minute < start_minute:  # Rolled over to next hour
                        hour += 1
                        if hour > 12:
                            hour = 1

            am_pm = "AM" if end_is_am else "PM"
            time_value = f"{hour}:{minute:02d} {am_pm}"
    else:  # start_time
        if use_24h:
            time_value = f"{hour}:{minute:02d}"
        else:
            am_pm = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            time_value = f"{display_hour}:{minute:02d} {am_pm}"

    return {"constraint": create_constraint_dict(field, operator, time_value), "hour": hour, "minute": minute, "use_24h": use_24h}


def _process_field_constraint(field: str, operators_map: dict[str, list], dataset: list[dict[str, Any]] | None = None, field_value: Any | None = None) -> dict[str, Any] | None:
    """Process a field constraint with appropriate operators and values."""
    operator = ComparisonOperator(random.choice(operators_map[field]))

    if field_value is None or dataset is None:
        return None

    value = _generate_constraint_value(operator, field_value, field, dataset)
    if value is not None:
        return create_constraint_dict(field, operator, value)
    return None


def generate_create_calendar_constraints() -> list[dict[str, Any]]:
    """Generate constraints for creating a calendar with specific details."""
    constraints_list = []
    field_map = {"name": {"values": CALENDAR_NAMES, "dataset_key": "name"}, "description": {"values": DESCRIPTIONS, "dataset_key": "description"}}

    for field, config in field_map.items():
        all_ops = FIELD_OPERATORS_CREATE_CALENDER_MAP[field]
        operator = ComparisonOperator(random.choice(all_ops))
        field_value = random.choice(config["values"])
        dataset = [{config["dataset_key"]: val} for val in config["values"]]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list


def generate_choose_calendar_constraints() -> list[dict[str, Any]]:
    """Generate constraints for selecting/deselecting a calendar."""
    constraints_list = []
    fields = ["calendar_name", "selected"]

    for field in fields:
        all_ops = FIELD_OPERATORS_CHOOSE_CALENDER_MAP[field]
        operator = ComparisonOperator(random.choice(all_ops))

        if field == "calendar_name":
            field_value = random.choice(CALENDAR_NAMES)
            dataset = [{field: name} for name in CALENDAR_NAMES]
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))
        elif field == "selected":
            constraints_list.append(create_constraint_dict(field, operator, False))

    return constraints_list


def generate_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding a calendar event."""
    constraints_list = []
    field_map = {
        "title": {"values": EVENT_TITLES, "dataset_key": "title"},
        "calendar": {"values": CALENDAR_NAMES, "dataset_key": "calendar"},
    }

    for field, config in field_map.items():
        all_ops = FIELD_OPERATORS_ADD_EVENT_MAP[field]
        operator = ComparisonOperator(random.choice(all_ops))
        field_value = random.choice(config["values"])
        dataset = [{config["dataset_key"]: val} for val in config["values"]]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    # Date constraint
    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP["date"]))
    today = datetime.now().date()
    date_range = [today + timedelta(days=i) for i in range(-30, 60)]
    field_value = random.choice(date_range)
    dataset = [{"date": date} for date in date_range]
    value = _generate_constraint_value(operator, field_value, "date", dataset)
    if value is not None:
        constraints_list.append(create_constraint_dict("date", operator, value))

    # Time constraints
    start_time_data = _generate_time_constraint("start_time", ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP["start_time"])))
    constraints_list.append(start_time_data["constraint"])

    end_time_data = _generate_time_constraint("end_time", ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP["end_time"])), start_time_data["hour"], start_time_data["minute"])
    constraints_list.append(end_time_data["constraint"])

    return constraints_list


def generate_cell_clicked_constraints() -> list[dict[str, Any]]:
    """Generate constraints for clicking a calendar cell."""
    constraints_list = []
    source_value = None

    fields = ["source", "date", "view"]
    field_map = {
        "source": {"values": ["month-view", "week-view", "day-view", "5 days-view"], "dataset_key": "source"},
        "view": {"values": ["Month", "Week", "Day", "5 days"], "dataset_key": "view"},
    }

    # Process fields with predefined values
    for field in fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP[field]))

        if field in field_map:
            field_value = random.choice(field_map[field]["values"])
            dataset = [{field_map[field]["dataset_key"]: val} for val in field_map[field]["values"]]
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraint = create_constraint_dict(field, operator, value)
                constraints_list.append(constraint)
                if field == "source":
                    source_value = value
        elif field == "date":
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date_range = [today + timedelta(days=i) for i in range(-30, 60)]
            date_value = random.choice(date_range)
            dataset = [{field: date} for date in date_range]
            value = _generate_constraint_value(operator, date_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

    # Add hour constraint only for week/day view
    if source_value and source_value != "month-view":
        hour_op = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP["hour"]))
        hour_value = random.randint(0, 23)
        constraints_list.append(create_constraint_dict("hour", hour_op, hour_value))

    return constraints_list


def generate_cancel_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for canceling event creation."""
    constraints_list = []
    field_map = {
        "source": {"values": ["month-view", "week-view", "day-view", "5 days-view"], "dataset_key": "source"},
        "title": {"values": EVENT_TITLES, "dataset_key": "title"},
    }

    # Process fields with predefined values
    for field in field_map:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP[field]))
        field_value = random.choice(field_map[field]["values"])
        dataset = [{field_map[field]["dataset_key"]: val} for val in field_map[field]["values"]]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    # Date constraint
    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP["date"]))
    today = datetime.now().date()
    date_range = [today + timedelta(days=i) for i in range(-30, 60)]
    date_value = random.choice(date_range)
    dataset = [{"date": date} for date in date_range]
    value = _generate_constraint_value(operator, date_value, "date", dataset)
    if value is not None:
        constraints_list.append(create_constraint_dict("date", operator, value))

    return constraints_list


def generate_delete_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for deleting a calendar event."""
    constraints_list = []
    field_map = {
        "source": {"values": ["event-modal", "month-view", "week-view", "day-view", "5 days-view"], "dataset_key": "source"},
        "event_title": {"values": EVENT_TITLES, "dataset_key": "event_title"},
        "calendar": {"values": CALENDAR_NAMES, "dataset_key": "calendar"},
    }

    # Process fields with predefined values
    for field, config in field_map.items():
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_DELETE_ADD_EVENT_MAP[field]))
        field_value = random.choice(config["values"])
        dataset = [{config["dataset_key"]: val} for val in config["values"]]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))

    # Date constraint
    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_DELETE_ADD_EVENT_MAP["date"]))
    today = datetime.now().date()
    date_range = [today + timedelta(days=i) for i in range(-30, 60)]
    date_value = random.choice(date_range)
    dataset = [{"date": date} for date in date_range]
    value = _generate_constraint_value(operator, date_value, "date", dataset)
    if value is not None:
        constraints_list.append(create_constraint_dict("date", operator, value))

    return constraints_list
