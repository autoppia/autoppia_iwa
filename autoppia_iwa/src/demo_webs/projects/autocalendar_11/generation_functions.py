import random
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict, parse_datetime

from ..criterion_helper import ComparisonOperator
from .data import (
    ATTENDEE_EMAILS,
    CALENDAR_NAMES,
    DESCRIPTIONS,
    EVENT_TITLES,
    EXISTING_CALENDAR_NAMES,
    FIELD_OPERATORS_ADD_EVENT_MAP,
    FIELD_OPERATORS_CHOOSE_CALENDAR_MAP,
    FIELD_OPERATORS_CLICK_CELL_MAP,
    FIELD_OPERATORS_CREATE_CALENDAR_MAP,
    FIELD_OPERATORS_EVENT_ATTENDEE_MAP,
    FIELD_OPERATORS_EVENT_REMINDER_MAP,
    FIELD_OPERATORS_SEARCH_SUBMIT_MAP,
    FIELD_OPERATORS_WIZARD_OPEN,
    LOCATIONS,
    MEETING_LINKS,
    RECURRENCE_OPTIONS,
    REMINDER_MINUTES,
    VISIBILITY_OPTIONS,
)
from .data_utils import fetch_data


async def _ensure_event_dataset(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Extract events data from the cache, or fetch from server if not available."""
    seed = get_seed_from_url(task_url)
    events = await fetch_data(seed_value=seed)
    dataset = {"events": events}

    if dataset and "events" in dataset:
        return dataset["events"]
    return []


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
        longest = max(field_value.split(), key=len)
        random_picker_start = random.randint(0, len(longest) - 1)

        if random_picker_start == len(longest) - 1:
            return longest[random_picker_start]  # just return last char
        else:
            random_picker_end = random.randint(random_picker_start + 1, len(longest))
            return longest[random_picker_start:random_picker_end]

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
                field_str = random.choice(dataset)[field]
                field_value = datetime.strptime(field_str, "%Y-%m-%d").date()
        else:
            dataset = [{config.get("dataset_key", field): val} for val in field_value_source]

        value = _generate_constraint_value(operator, field_value, field, dataset)

        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
            if config.get("provides_context"):
                context[field] = value

    return constraints_list


def _handle_time_constraints(context: dict) -> list[dict[str, Any]]:
    """Handler for start and end time constraints ensuring logical consistency."""
    start_hour = random.randint(0, 22)
    start_minute = random.choice([0, 30])

    end_hour = start_hour
    end_minute = start_minute

    if start_minute == 0:
        end_minute = 30
    else:
        end_minute = 0
        end_hour += 1

    start_op_choices = FIELD_OPERATORS_ADD_EVENT_MAP["start_time"]
    end_op_choices = FIELD_OPERATORS_ADD_EVENT_MAP["end_time"]

    # Select operators
    start_op = ComparisonOperator(random.choice(start_op_choices))
    end_op = ComparisonOperator(random.choice(end_op_choices))

    start_time_value = time(hour=start_hour, minute=start_minute)
    end_time_value = time(hour=end_hour, minute=end_minute)

    # If start_time > X, then end_time must be > X + 30min
    # Ensure end time is not less than or equal to start time
    if start_op in [ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL] and end_op in [ComparisonOperator.LESS_THAN, ComparisonOperator.LESS_EQUAL, ComparisonOperator.EQUALS]:
        end_op = ComparisonOperator.GREATER_THAN

    # If end_time < X, then start_time must be < X - 30min
    # Ensure start time is not greater than or equal to end time
    elif end_op in [ComparisonOperator.LESS_THAN, ComparisonOperator.LESS_EQUAL] and start_op in [ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.EQUALS]:
        start_op = ComparisonOperator.LESS_THAN

    start_constraint = create_constraint_dict("start_time", start_op, start_time_value)
    end_constraint = create_constraint_dict("end_time", end_op, end_time_value)

    return [start_constraint, end_constraint]


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
        "title": {"values": EVENT_TITLES},
        "calendar": {"values": EXISTING_CALENDAR_NAMES},
        "date": {"dataset_generator": lambda: [{"date": (date.today() + timedelta(days=i)).strftime("%Y-%m-%d")} for i in range(-30, 30)]},
        "time": {},  # Special handler
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
    selected_fields = random.sample(possible_fields, k=random.randint(3, min(8, len(possible_fields))))
    if "title" not in selected_fields:
        selected_fields.append("title")
    if "date" not in selected_fields:
        selected_fields.append("date")
    if "all_day" in selected_fields and "time" in selected_fields:
        selected_fields.remove("time")
    reduced_field_map = {field: field_map[field] for field in selected_fields}
    return _generate_constraints_for_event(reduced_field_map, FIELD_OPERATORS_ADD_EVENT_MAP, {"time": _handle_time_constraints})


async def generate_event_wizard_open_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    event_data = await _ensure_event_dataset(task_url, dataset)
    constraints_list = []
    if not event_data:
        print("[ERROR] No event data provided")
        return constraints_list
    possible_fields = list(FIELD_OPERATORS_WIZARD_OPEN.keys())
    selected_fields = random.sample(possible_fields, k=random.randint(1, len(possible_fields)))
    sample_event = random.choice(event_data)
    for field in selected_fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_WIZARD_OPEN[field]))
        if field == "title":
            field_value = sample_event.get("label", None)
            dataset = [{"title": v["label"]} for v in event_data]
        elif field == "date":
            dt = parse_datetime(sample_event.get("date", None))
            if not dt:
                continue
            # Convert datetime to string format for validation
            field_value = dt.strftime("%Y-%m-%d")
            dataset = [{"date": parse_datetime(event["date"]).strftime("%Y-%m-%d")} for event in event_data if "date" in event]
        else:
            field_value = sample_event.get(field, None)
            dataset = [{field: event.get(field, None)} for event in event_data if field in event]
        if not field_value:
            continue
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            if field == "date" and isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d")
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
