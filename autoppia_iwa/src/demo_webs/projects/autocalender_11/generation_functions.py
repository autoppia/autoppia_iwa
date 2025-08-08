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
            if field == "rating":
                min_val, max_val = 0.0, 5.0
                if operator == ComparisonOperator.GREATER_THAN:
                    if base > min_val:
                        min_dataset = min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                        return round(random.uniform(min_dataset, max(base - 0.5, min_dataset)), 2)
                    else:
                        return min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                elif operator == ComparisonOperator.LESS_THAN:
                    if base < max_val:
                        max_dataset = max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                        return round(random.uniform(min(base + 0.1, max_dataset), max_dataset), 2)
                    else:
                        return max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return round(base, 2)
            elif field == "reviews":
                min_val, max_val = 0, 1000  # Assume 1000 as a practical upper bound
                if operator == ComparisonOperator.GREATER_THAN:
                    if base > min_val:
                        min_dataset = min((v.get(field) for v in dataset if isinstance(v.get(field), int)), default=min_val)
                        return max(min_dataset, base - random.randint(1, min(base, 20)))
                    else:
                        return min((v.get(field) for v in dataset if isinstance(v.get(field), int)), default=min_val)
                elif operator == ComparisonOperator.LESS_THAN:
                    if base < max_val:
                        max_dataset = max((v.get(field) for v in dataset if isinstance(v.get(field), int)), default=max_val)
                        return min(max_dataset, base + random.randint(1, 20))
                    else:
                        return max((v.get(field) for v in dataset if isinstance(v.get(field), int)), default=max_val)
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return base
            else:
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


def generate_create_calendar_constraints() -> list[dict[str, Any]]:
    """Generate constraints for creating a calendar with specific details."""
    constraints_list = []
    fields = ["name", "description"]
    for field in fields:
        all_ops = FIELD_OPERATORS_CREATE_CALENDER_MAP[field]
        operator = ComparisonOperator(random.choice(all_ops))
        dataset = []
        field_value = None
        if field == "name":
            field_value = random.choice(CALENDAR_NAMES)
            dataset = [{"name": name} for name in CALENDAR_NAMES]
        elif field == "description":
            field_value = random.choice(DESCRIPTIONS)
            dataset = [{"description": desc} for desc in DESCRIPTIONS]
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
        dataset = []
        field_value = None
        if field == "calender_name":
            field_value = random.choice(CALENDAR_NAMES)
            dataset = [{field: name} for name in CALENDAR_NAMES]
        elif field == "selected":
            constraints_list.append(create_constraint_dict(field, operator, False))
            continue
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding a calendar event."""
    constraints_list = []
    all_fields = ["title", "calendar", "date", "start_time", "end_time"]

    for field in all_fields:
        all_ops = FIELD_OPERATORS_ADD_EVENT_MAP[field]
        operator = ComparisonOperator(random.choice(all_ops))

        if field == "title":
            field_value = random.choice(EVENT_TITLES)
            dataset = [{field: title} for title in EVENT_TITLES]
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "calendar":
            field_value = random.choice(CALENDAR_NAMES)
            dataset = [{field: name} for name in CALENDAR_NAMES]
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "date":
            today = datetime.now().date()
            date_range = [today + timedelta(days=i) for i in range(-30, 60)]
            field_value = random.choice(date_range)
            dataset = [{"date": date} for date in date_range]
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field in ["start_time", "end_time"]:
            start_hour = random.randint(8, 17)
            start_minute = random.choice([0, 30])
            end_hour = start_hour + random.randint(0, 3)
            end_minute = random.choice([0, 30])

            # Ensure end time is after start time
            if end_hour == start_hour and end_minute <= start_minute:
                end_minute = (start_minute + 30) % 60
                if end_minute < start_minute:  # Rolled over to next hour
                    end_hour += 1

            if field == "start_time":
                time_value = f"{start_hour}:{start_minute:02d}"
                constraints_list.append(create_constraint_dict(field, operator, time_value))
            else:  # end_time
                time_value = f"{end_hour}:{end_minute:02d}"
                constraints_list.append(create_constraint_dict(field, operator, time_value))

    return constraints_list


def generate_cell_clicked_constraints() -> list[dict[str, Any]]:
    """Generate constraints for clicking a calendar cell."""
    constraints_list = []
    fields = ["source", "date", "view"]
    for field in fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP[field]))
        if field == "source":
            sources = ["month-view", "week-view", "day-view", "5 days-view"]
            source_value = random.choice(sources)
            dataset = [{field: source} for source in sources]
            value = _generate_constraint_value(operator, source_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))
        elif field == "view":
            views = ["Month", "Week", "Day", "5 days"]
            view_value = random.choice(views)
            dataset = [{field: view} for view in views]
            value = _generate_constraint_value(operator, view_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))
        elif field == "date":
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            date_range = [today + timedelta(days=i) for i in range(-30, 60)]
            date_value = random.choice(date_range)
            dataset = [{field: date} for date in date_range]
            value = _generate_constraint_value(operator, date_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

    # Get the source value from the constraints to determine if we need an hour constraint
    source_constraints = [c for c in constraints_list if c["field"] == "source"]
    source_value = None
    if source_constraints and "value" in source_constraints[0]:
        source_value = source_constraints[0]["value"]

    # Add hour constraint only for week/day view
    if source_value and source_value != "month-view":
        hour_op = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP["hour"]))
        hour_value = random.randint(0, 23)
        constraints_list.append(create_constraint_dict("hour", hour_op, hour_value))

    return constraints_list


def generate_cancel_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for canceling event creation."""
    constraints_list = []
    fields = ["source", "date", "title"]

    for field in fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_CANCEL_MAP[field]))

        if field == "source":
            sources = ["month-view", "week-view", "day-view", "5 days-view"]
            source_value = random.choice(sources)
            dataset = [{field: source} for source in sources]
            value = _generate_constraint_value(operator, source_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "date":
            today = datetime.now().date()
            date_range = [today + timedelta(days=i) for i in range(-30, 60)]
            date_value = random.choice(date_range)
            dataset = [{field: date} for date in date_range]
            value = _generate_constraint_value(operator, date_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "title":
            title_value = random.choice(EVENT_TITLES)
            dataset = [{field: title} for title in EVENT_TITLES]
            value = _generate_constraint_value(operator, title_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list


def generate_delete_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for deleting a calendar event."""
    constraints_list = []
    fields = ["source", "eventTitle", "calendar", "date"]

    for field in fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_DELETE_ADD_EVENT_MAP))
        if field == "source":
            sources = ["event-modal", "month-view", "week-view", "day-view", "5 days-view"]
            source_value = random.choice(sources)
            dataset = [{field: source} for source in sources]
            value = _generate_constraint_value(operator, source_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "eventTitle":
            title_value = random.choice(EVENT_TITLES)
            dataset = [{field: title} for title in EVENT_TITLES]
            value = _generate_constraint_value(operator, title_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "calendar":
            calendar_value = random.choice(CALENDAR_NAMES)
            dataset = [{field: name} for name in CALENDAR_NAMES]
            value = _generate_constraint_value(operator, calendar_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

        elif field == "date":
            today = datetime.now().date()
            date_range = [today + timedelta(days=i) for i in range(-30, 60)]
            date_value = random.choice(date_range)
            dataset = [{field: date} for date in date_range]
            value = _generate_constraint_value(operator, date_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list
