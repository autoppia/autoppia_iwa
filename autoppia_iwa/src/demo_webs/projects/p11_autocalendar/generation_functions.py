import asyncio
import random
from collections.abc import Callable
from datetime import date, datetime, time, timedelta
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url
from autoppia_iwa.src.demo_webs.shared_utils import (
    constraint_value_for_datetime_date,
    constraint_value_for_numeric,
    constraint_value_for_time,
    create_constraint_dict,
    parse_datetime,
    pick_different_value_from_dataset,
    random_str_not_contained_in,
)

from ...criterion_helper import ComparisonOperator
from .data import (
    ATTENDEE_EMAILS,
    CALENDAR_NAMES,
    DESCRIPTIONS,
    EVENT_TITLES,
    EXISTING_CALENDAR_NAMES,
    FIELD_OPERATORS_ADD_EVENT_MAP,
    FIELD_OPERATORS_CLICK_CELL_MAP,
    FIELD_OPERATORS_CREATE_CALENDAR_MAP,
    FIELD_OPERATORS_EVENT_ATTENDEE_MAP,
    FIELD_OPERATORS_EVENT_REMINDER_MAP,
    FIELD_OPERATORS_SEARCH_SUBMIT_MAP,
    FIELD_OPERATORS_UNSELECT_CALENDAR_MAP,
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
    _ = dataset  # Unused parameter kept for backward compatibility
    seed = get_seed_from_url(task_url)
    events = await fetch_data(seed_value=seed)
    if isinstance(events, list):
        return events
    return []


def _format_ui_time(hm: Any) -> str | None:
    if not isinstance(hm, list) or len(hm) < 2:
        return None
    try:
        hour = int(hm[0])
        minute = int(hm[1])
    except (TypeError, ValueError):
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}:{minute:02d} {suffix}"


def _format_ui_reminders(values: Any) -> list[str] | None:
    if not isinstance(values, list):
        return None
    out: list[str] = []
    for v in values:
        try:
            m = int(v)
        except (TypeError, ValueError):
            continue
        if m >= 60:
            out.append(f"{round(m / 60)}h before")
        else:
            out.append(f"{m}m before")
    return out if out else None


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    visible_fields: list[str],
    *,
    verify_field: str | None = None,
    question_fields_override: list[str] | None = None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure."""
    available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        return None

    question_fields: list[str]
    chosen_verify_field: str

    if question_fields_override:
        question_fields = [f for f in question_fields_override if f in available_fields and selected_item.get(f) is not None]
        if question_fields:
            remaining = [f for f in available_fields if f not in question_fields]
            if not remaining:
                return None
            chosen_verify_field = verify_field if verify_field is not None and verify_field in remaining else random.choice(remaining)
            remaining_for_extra = [f for f in available_fields if f != chosen_verify_field and f not in question_fields]
            if len(remaining_for_extra) >= 2:
                num_extra = random.randint(1, len(remaining_for_extra))
                question_fields = question_fields + random.sample(remaining_for_extra, num_extra)
        else:
            question_fields = []
            chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
    else:
        chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
        question_fields = []

    if chosen_verify_field not in available_fields:
        return None
    verify_value = selected_item.get(chosen_verify_field)
    if verify_value is None:
        return None

    if question_fields:
        question_candidates = question_fields
    else:
        question_candidates = [f for f in available_fields if f != chosen_verify_field]
        if not question_candidates:
            return None
        num_question_fields = 1 if len(question_candidates) == 1 else 2
        question_candidates = random.sample(question_candidates, num_question_fields)

    question_fields_and_values: dict[str, Any] = {}
    for qf in question_candidates:
        val = selected_item.get(qf)
        if val is not None:
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        return None

    constraints = [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


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
        return constraint_value_for_datetime_date(operator, field_value)

    if isinstance(field_value, time):
        return constraint_value_for_time(operator, field_value, field, dataset)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        return pick_different_value_from_dataset(dataset, field, field_value, None)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        longest = max(field_value.split(), key=len)
        random_picker_start = random.randint(0, len(longest) - 1)

        if random_picker_start == len(longest) - 1:
            return longest[random_picker_start]  # just return last char
        random_picker_end = random.randint(random_picker_start + 1, len(longest))
        return longest[random_picker_start:random_picker_end]

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return random_str_not_contained_in(field_value)

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        return constraint_value_for_numeric(operator, field_value)

    return None


def _generate_constraints_from_single_field(
    field_name: str,
    values: list[Any],
    operators_map: dict[str, list],
) -> list[dict[str, Any]]:
    """Generate constraints for a single field with a fixed value list. Reduces duplication across single-field generators."""
    field_map = {field_name: {"values": values}}
    return _generate_constraints_for_event(field_map, operators_map)


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


async def _generate_create_calendar_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for creating a calendar."""
    if test_types == "data_extraction_only":
        calendar_names = ["Personal", "Work", "Friends", "Wellness", "Family"]
        calendar_count = 5
        return {
            "constraints": random.sample(
                [create_constraint_dict("calendar_names", ComparisonOperator.EQUALS, calendar_names), create_constraint_dict("calendar_count", ComparisonOperator.EQUALS, calendar_count)],
                1,  # select only one item
            )
        }

    field_map = {
        "name": {"values": CALENDAR_NAMES},
        "description": {"values": DESCRIPTIONS},
    }
    return _generate_constraints_for_event(field_map, FIELD_OPERATORS_CREATE_CALENDAR_MAP)


async def _generate_unselect_calendar_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for selecting/deselecting a calendar."""
    if test_types == "data_extraction_only":
        calendar_names = ["Personal", "Work", "Friends", "Wellness", "Family"]
        calendar_count = 5
        return {
            "constraints": random.sample(
                [create_constraint_dict("calendar_names", ComparisonOperator.EQUALS, calendar_names), create_constraint_dict("calendar_count", ComparisonOperator.EQUALS, calendar_count)],
                1,  # select only one item
            )
        }

    return _generate_constraints_from_single_field("calendar_name", CALENDAR_NAMES, FIELD_OPERATORS_UNSELECT_CALENDAR_MAP)


def generate_create_calendar_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_create_calendar_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


def generate_unselect_calendar_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_unselect_calendar_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


async def generate_add_new_calendar_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Data extraction support for add-new-calendar modal use case."""
    if test_types == "data_extraction_only":
        calendar_names = ["Personal", "Work", "Friends", "Wellness", "Family"]
        calendar_count = 5
        return {
            "constraints": random.sample(
                [create_constraint_dict("calendar_names", ComparisonOperator.EQUALS, calendar_names), create_constraint_dict("calendar_count", ComparisonOperator.EQUALS, calendar_count)],
                1,  # select only one item
            )
        }
    return []


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


async def _generate_add_event_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for adding a calendar event."""
    if test_types == "data_extraction_only":
        return await _generate_search_submit_constraints_async(
            task_url=task_url,
            dataset=dataset,
            test_types=test_types,
        )

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


def generate_add_event_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_add_event_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


async def generate_event_wizard_open_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    event_data = await _ensure_event_dataset(task_url, dataset)
    if test_types == "data_extraction_only":
        if not event_data:
            return []
        selected = random.choice(event_data)
        if not isinstance(selected, dict):
            return []

        event_date = selected.get("date")
        start_time = _format_ui_time(selected.get("startTime"))
        end_time = _format_ui_time(selected.get("endTime"))
        time_duration = f"{start_time} - {end_time}" if start_time and end_time else None

        selected_item = {
            "title": selected.get("label"),
            "date": event_date,
            "time_duration": time_duration,
            "location": selected.get("location"),
        }
        visible_fields = ["date", "time_duration", "title", "location"]
        return _build_data_extraction_result(selected_item, visible_fields, question_fields_override=["title"]) or []

    constraints_list = []
    if not event_data:
        logger.error("No event data provided")
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


async def _generate_search_submit_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for submitting a search query."""
    if test_types == "data_extraction_only":
        event_data = await _ensure_event_dataset(task_url, dataset)
        if not event_data:
            return []
        selected = random.choice(event_data)
        if not isinstance(selected, dict):
            return []

        start_time_raw = selected.get("startTime")
        end_time_raw = selected.get("endTime")
        start_time = _format_ui_time(start_time_raw)
        end_time = _format_ui_time(end_time_raw)
        raw_date = selected.get("date")
        ui_date = raw_date.replace("-", "/") if isinstance(raw_date, str) else None
        recurrence_raw = selected.get("recurrence")
        recurrence = recurrence_raw.strip().capitalize() if isinstance(recurrence_raw, str) and recurrence_raw.strip() else None
        attendees = selected.get("attendees")

        selected_item = {
            "date": ui_date,
            "start_time": start_time,
            "end_time": end_time,
            "calendar": selected.get("calendar"),
            "title": selected.get("label"),
            "location": selected.get("location"),
            "description": selected.get("description"),
        }
        visible_fields = [
            "date",
            "start_time",
            "end_time",
            "calendar",
            "title",
            "location",
            "description",
        ]
        if attendees is not None and attendees != []:
            selected_item["attendees"] = attendees
            visible_fields.append("attendees")
        if recurrence is not None and recurrence != "None":
            selected_item["recurrence"] = recurrence
            visible_fields.append("recurrence")
        return _build_data_extraction_result(selected_item, visible_fields, question_fields_override=["title"]) or []

    return _generate_constraints_from_single_field("query", CALENDAR_NAMES, FIELD_OPERATORS_SEARCH_SUBMIT_MAP)


def generate_search_submit_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_search_submit_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


async def _generate_event_reminder_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for adding an event reminder."""
    if test_types == "data_extraction_only":
        event_data = await _ensure_event_dataset(task_url, dataset)
        if not event_data:
            return []
        selected = random.choice(event_data)
        if not isinstance(selected, dict):
            return []

        start_time = _format_ui_time(selected.get("startTime"))
        end_time = _format_ui_time(selected.get("endTime"))
        raw_date = selected.get("date")
        ui_date = raw_date.replace("-", "/") if isinstance(raw_date, str) else None
        recurrence_raw = selected.get("recurrence")
        recurrence = recurrence_raw.strip().capitalize() if isinstance(recurrence_raw, str) and recurrence_raw.strip() else None
        attendees = selected.get("attendees")
        raw_reminders = selected.get("reminders")
        reminders_ui = _format_ui_reminders(raw_reminders)
        if reminders_ui is None:
            return []

        selected_item = {
            "date": ui_date,
            "start_time": start_time,
            "end_time": end_time,
            "title": selected.get("label"),
            "location": selected.get("location"),
            "description": selected.get("description"),
            "reminders": reminders_ui,
        }
        visible_fields = [
            "date",
            "title",
            "start_time",
            "end_time",
            "location",
            "description",
            "reminders",
        ]
        if attendees is not None and attendees != []:
            selected_item["attendees"] = attendees
            visible_fields.append("attendees")
        if recurrence is not None and recurrence != "None":
            selected_item["recurrence"] = recurrence
            visible_fields.append("recurrence")

        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
                verify_field="reminders",
                question_fields_override=["title"],
            )
            or []
        )
    return _generate_constraints_from_single_field("minutes", REMINDER_MINUTES, FIELD_OPERATORS_EVENT_REMINDER_MAP)


async def _generate_event_attendee_constraints_async(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for adding an event attendee."""
    if test_types == "data_extraction_only":
        event_data = await _ensure_event_dataset(task_url, dataset)
        if not event_data:
            return []

        eligible_events = [event for event in event_data if isinstance(event, dict) and isinstance(event.get("attendees"), list) and len(event.get("attendees")) > 0]
        if not eligible_events:
            return []

        selected = random.choice(eligible_events)
        start_time = _format_ui_time(selected.get("startTime"))
        end_time = _format_ui_time(selected.get("endTime"))
        raw_date = selected.get("date")
        ui_date = raw_date.replace("-", "/") if isinstance(raw_date, str) else None
        recurrence_raw = selected.get("recurrence")
        recurrence = recurrence_raw.strip().capitalize() if isinstance(recurrence_raw, str) and recurrence_raw.strip() else None
        attendees = selected.get("attendees")

        selected_item = {
            "date": ui_date,
            "start_time": start_time,
            "end_time": end_time,
            "calendar": selected.get("calendar"),
            "title": selected.get("label"),
            "location": selected.get("location"),
            "description": selected.get("description"),
            "attendees": attendees,
        }
        visible_fields = [
            "date",
            "start_time",
            "end_time",
            "calendar",
            "title",
            "location",
            "description",
            "attendees",
        ]
        if recurrence is not None and recurrence != "None":
            selected_item["recurrence"] = recurrence
            visible_fields.append("recurrence")

        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
                verify_field="attendees",
                question_fields_override=["title"],
            )
            or []
        )
    return _generate_constraints_from_single_field("email", ATTENDEE_EMAILS, FIELD_OPERATORS_EVENT_ATTENDEE_MAP)


def generate_event_reminder_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_event_reminder_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro


def generate_event_attendee_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    coro = _generate_event_attendee_constraints_async(task_url=task_url, dataset=dataset, test_types=test_types)
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return coro
