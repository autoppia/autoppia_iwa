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
    """Generate constraints for clicking a calendar cell, ensuring date is valid for the view."""
    constraints_list = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    all_views = ["Month", "Week", "Day", "5 days"]

    view = random.choice(all_views)
    view_op = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP["view"]))
    constraints_list.append(create_constraint_dict("view", view_op, view))

    # 2. Determine a realistic viewDate, simulating weekly navigation
    navigation = random.choice(["current", "next", "previous"])
    offset = timedelta(0)
    if navigation != "current":
        # Navigation is always by week. Simulate 1 to 5 clicks.
        num_weeks = random.randint(1, 5)
        days_to_move = num_weeks * 7
        if navigation == "previous":
            days_to_move = -days_to_move
        offset = timedelta(days=days_to_move)

    view_date = today + offset

    # 3. Calculate the range of visible dates based on the view and view_date
    if view == "Month":
        # The month view shows the whole month for the given view_date
        start_date = view_date.replace(day=1)
        if start_date.month == 12:  # Handle December
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
    elif view == "Week":
        # The week view shows from Monday to Sunday for the given view_date
        start_date = view_date - timedelta(days=view_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif view == "5 days":
        # The 5 days view shows from Tuesday to Saturday for the week of the given view_date
        start_of_week = view_date - timedelta(days=view_date.weekday())
        start_date = start_of_week + timedelta(days=1)  # Tuesday
        end_date = start_of_week + timedelta(days=5)  # Saturday
    else:  # Day view
        # The day view shows only the given view_date
        start_date = end_date = view_date

    # 4. Select a date operator and value, ensuring the constraint is satisfiable
    days_in_range = (end_date - start_date).days
    possible_ops = FIELD_OPERATORS_CLICK_CELL_MAP["date"]

    # If view has only one day, some operators are impossible to satisfy

    if days_in_range == 0:
        allowed_ops = [ComparisonOperator.EQUALS.value, ComparisonOperator.GREATER_EQUAL.value, ComparisonOperator.LESS_EQUAL.value]
        possible_ops = [op for op in possible_ops if op in allowed_ops]
        if not possible_ops:
            possible_ops = [ComparisonOperator.EQUALS.value]  # Fallback

    date_op_str = random.choice(possible_ops)
    date_op = ComparisonOperator(date_op_str)

    # Select a date from the range
    random_day_offset = random.randint(0, max(0, days_in_range))
    constraint_date = start_date + timedelta(days=random_day_offset)

    # Adjust date for operators to ensure satisfiability
    if date_op == ComparisonOperator.LESS_THAN and constraint_date == start_date:
        # e.g., "date < start_date" is impossible. Move to next day.
        constraint_date += timedelta(days=1)
    elif date_op == ComparisonOperator.GREATER_THAN and constraint_date == end_date:
        # e.g., "date > end_date" is impossible. Move to previous day.
        constraint_date -= timedelta(days=1)

    constraints_list.append(create_constraint_dict("date", date_op, constraint_date))

    # 5. Generate hour constraint if not in month view
    if "month" not in view.lower():
        hour_op = ComparisonOperator(random.choice(FIELD_OPERATORS_CLICK_CELL_MAP["hour"]))
        hour_value = random.randint(0, 23)
        constraints_list.append(create_constraint_dict("hour", hour_op, hour_value))

    return constraints_list


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
    if "end_time" in selected_fields and "start_time" not in selected_fields:
        selected_fields.append("start_time")
    reduced_field_map = {field: field_map[field] for field in selected_fields}
    return _generate_constraints_for_event(reduced_field_map, FIELD_OPERATORS_ADD_EVENT_MAP, {"time": _handle_time_constraints})


def generate_event_wizard_open_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_ADD_EVENT_MAP.keys())
    selected_fields = random.sample(possible_fields, k=random.randint(3, len(possible_fields)))
    # Ensure start_time is present if end_time is selected
    if "end_time" in selected_fields and "start_time" not in selected_fields:
        selected_fields.append("start_time")
    sample_event = random.choice(EVENTS_DATASET)
    for field in selected_fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_ADD_EVENT_MAP[field]))
        if field == "title":
            field_value = sample_event.get("label", None)
            dataset = [{"title": v["label"]} for v in EVENTS_DATASET]
        elif field == "date":
            field_value = parse_datetime(sample_event.get("date", None))
            dataset = [{"date": parse_datetime(event["date"])} for event in EVENTS_DATASET if "date" in event]
        elif field in ["start_time", "end_time"]:
            val = sample_event.get(field, [])
            if len(val) == 2:
                time_str = f"{val[0]}:{str(val[1]).zfill(2)}"
                field_value = datetime.strptime(time_str, "%H:%M").time()
                dataset = [
                    {field: datetime.strptime(f"{event[field][0]}:{str(event[field][1]).zfill(2)}", "%H:%M").time()}
                    for event in EVENTS_DATASET
                    if field in event and isinstance(event[field], list) and len(event[field]) == 2
                ]
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
