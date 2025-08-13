import random
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict, parse_datetime

from ..criterion_helper import ComparisonOperator
from .data import (
    ATTENDEE_EMAILS,
    CALENDAR_NAMES,
    DESCRIPTIONS,
    EVENT_TITLES,
    EVENTS_DATASET,
    FIELD_OPERATORS_ADD_EVENT_MAP,
    FIELD_OPERATORS_CHOOSE_CALENDAR_MAP,
    FIELD_OPERATORS_CLICK_CELL_MAP,
    FIELD_OPERATORS_CREATE_CALENDAR_MAP,
    FIELD_OPERATORS_EVENT_ATTENDEE_MAP,
    FIELD_OPERATORS_EVENT_REMINDER_MAP,
    FIELD_OPERATORS_SEARCH_SUBMIT_MAP,
    LOCATIONS,
    MEETING_LINKS,
    RECURRENCE_OPTIONS,
    REMINDER_MINUTES,
    VISIBILITY_OPTIONS,
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

    if isinstance(field_value, time):
        delta_minutes = random.choice([5, 10, 15, 30, 60])

        def add_minutes(t, mins):
            full_dt = datetime.combine(date.today(), t) + timedelta(minutes=mins)
            return full_dt.time()

        if operator == ComparisonOperator.GREATER_THAN:
            return add_minutes(field_value, -delta_minutes)
        if operator == ComparisonOperator.LESS_THAN:
            return add_minutes(field_value, delta_minutes)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS}:
            return field_value
        if operator == ComparisonOperator.NOT_EQUALS:
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else add_minutes(field_value, delta_minutes + 5)

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


def generate_cell_clicked_constraints() -> list[dict[str, Any]]:
    """Generate constraints for clicking a calendar cell."""
    field_map = {
        "source": {"values": ["month-view", "week-view", "day-view", "5 days-view"], "provides_context": True},
        "date": {"dataset_generator": lambda: [{"date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=i)} for i in range(-30, 60)]},
        "view": {"values": ["Month", "Week", "Day", "5 days"]},
        "hour": {},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CLICK_CELL_MAP, {"hour": _handle_cell_click_hour})


def generate_add_event_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding a calendar event."""
    field_map = {
        # "source": {"values": SOURCES},
        "title": {"values": EVENT_TITLES},
        "calendar": {"values": CALENDAR_NAMES},
        "date": {"dataset_generator": lambda: [{"date": (date.today() + timedelta(days=i)).strftime("%Y-%m-%d")} for i in range(-30, 60)]},
        "time": {},  # Special handler
        # "color": {"values": COLORS},
        # "is_editing": {"values": [True, False]},
        "all_day": {"values": [True, False]},
        "recurrence": {"values": RECURRENCE_OPTIONS},
        "attendees": {"values": ATTENDEE_EMAILS},
        "reminders": {"values": REMINDER_MINUTES},
        "busy": {"values": [True, False]},
        "visibility": {"values": VISIBILITY_OPTIONS},
        "location": {"values": LOCATIONS},
        "description": {"values": DESCRIPTIONS},
        "meeting_link": {"values": MEETING_LINKS},
    }
    possible_fields = list(field_map.keys())
    selected_fields = random.sample(possible_fields, k=random.randint(3, len(possible_fields)))
    reduced_field_map = {field: field_map[field] for field in selected_fields}
    return _generate_constraints_for_event(reduced_field_map, FIELD_OPERATORS_ADD_EVENT_MAP, {"time": _handle_time_constraints})


def generate_event_wizard_open_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_ADD_EVENT_MAP.keys())
    selected_fields = random.sample(possible_fields, k=random.randint(3, len(possible_fields)))
    sample_event = random.choice(EVENTS_DATASET)
    for field in selected_fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP[field]))
        if field == "title":
            field_value = sample_event.get("label", None)
            dataset = [{"title": v} for v in EVENTS_DATASET["label"]]
        elif field == "date":
            field_value = parse_datetime(sample_event.get("date", None))
            dataset = [{"date": parse_datetime(v)} for v in EVENTS_DATASET["date"]]
        elif field in ["start_time", "end_time"]:
            val = sample_event.get(field, [])
            if len(val) == 2:
                time_str = f"{val[0]}:{str(val[1]).zfill(2)}"
                field_value = datetime.strptime(time_str, "%H:%M").time()
                dataset = [{field: datetime.strptime(f"{v[0]}:{str(v[1]).zfill(2)}", "%H:%M").time()} for v in EVENTS_DATASET[field] if isinstance(v, list) and len(v) == 2]
            else:
                continue
        else:
            field_value = sample_event.get(field, None)
            dataset = [{field: event.get(field, None)} for event in EVENTS_DATASET if field in event]
        if not field_value:
            continue
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_search_submit_constraints() -> list[dict[str, Any]]:
    """Generate constraints for submitting a search query."""
    field_map = {"query": {"values": CALENDAR_NAMES}}
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_SEARCH_SUBMIT_MAP)


def generate_event_reminder_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding an event reminder."""
    field_map = {"minutes": {"values": REMINDER_MINUTES}}
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_EVENT_REMINDER_MAP)


def generate_event_attendee_constraints() -> list[dict[str, Any]]:
    """Generate constraints for adding an event attendee."""
    field_map = {"email": {"values": ATTENDEE_EMAILS}}
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_EVENT_ATTENDEE_MAP)
