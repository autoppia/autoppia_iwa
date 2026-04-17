import random
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from random import choice, randint, randrange
from typing import Any

from dateutil import parser

from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url

from ...criterion_helper import ComparisonOperator
from ...shared_utils import (
    constraint_value_for_datetime_date,
    constraint_value_for_numeric,
    constraint_value_for_time,
    create_constraint_dict,
    pick_different_value_from_dataset,
    random_str_not_contained_in,
)
from .data import (
    FIELD_OPERATORS_MAP_BOOK_TRIP,
    FIELD_OPERATORS_MAP_ENTER_DESTINATION,
    FIELD_OPERATORS_MAP_ENTER_LOCATION,
    FIELD_OPERATORS_MAP_FILTER_TRIPS,
    FIELD_OPERATORS_MAP_NEXT_PICKUP,
    FIELD_OPERATORS_MAP_SEARCH_RIDE,
    FIELD_OPERATORS_MAP_SEE_PRICES,
    FIELD_OPERATORS_MAP_SELECT_CAR,
    FIELD_OPERATORS_MAP_SELECT_DATE,
    FIELD_OPERATORS_MAP_SELECT_TIME,
    FIELD_OPERATORS_MAP_SUBMIT_TRIP_REVIEW,
    FIELD_OPERATORS_MAP_VIEW_AVAILABLE_TRIPS,
)
from .data_utils import fetch_data


def normalize_contain_value(value: str) -> str:
    """
    If value contains " - " with non-empty text after it, return the part after " - " (stripped).
    Otherwise return the part before " - " or the whole string.
    """
    if not value:
        return value
    if " - " in value:
        left, _, right = value.partition(" - ")
        right_stripped = right.strip()
        return right_stripped if right_stripped else left.strip()
    return value.strip()


async def _ensure_drive_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract entity data from the cache dataset, or fetch from server if not available.

    Dynamically fetches only the requested entity_type using the provided method.
    Returns a dictionary with entity_type as the key.
    """
    _ = dataset  # Unused parameter kept for backward compatibility

    # Otherwise, fetch the specific entity type dynamically using the provided parameters
    seed = get_seed_from_url(task_url)

    fetched_dataset = await fetch_data(
        entity_type=entity_type,
        method=method,
        seed_value=seed,
    )

    # Return as dictionary with entity_type as key
    return {entity_type: fetched_dataset}


async def _get_drive_entity_list(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None,
    entity_type: str,
    *,
    method: str | None = None,
) -> list[dict[str, Any]]:
    """Load entity list for the given type (e.g. 'places', 'rides') and return the list."""
    dataset_dict = await _ensure_drive_dataset(task_url, dataset, entity_type=entity_type, method=method)
    return dataset_dict.get(entity_type, [])


def _collect_field_values_from_dataset(dataset: list[dict[str, Any]], field: str) -> list[Any]:
    """Return unique non-None values for field across dataset rows."""
    return list({v.get(field) for v in dataset if field in v and v.get(field) is not None})


def _format_ui_currency(value: Any) -> str | None:
    """Format numeric backend prices to UI currency style like '$26.10'."""
    if value is None:
        return None
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return f"${amount:.2f}"


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
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            result = field_value[start:end]
        else:
            result = field_value
        return normalize_contain_value(result) if "-" in result else result

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return random_str_not_contained_in(field_value)

    if operator == ComparisonOperator.IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        return constraint_value_for_numeric(operator, field_value)

    return None


def random_datetime(days: int | None = None, end: datetime | None = None, start: datetime | None = None) -> datetime:
    """
    Generate a random datetime starting from today (or a given start datetime).

    Args:
        days (int, optional): Number of days from today to set as the end range.
        end (datetime, optional): Specific end datetime.
        start (datetime, optional): Custom start datetime (default: now).

    Returns:
        datetime: Random datetime within the range.
    """
    # Default start is now
    start = start or datetime.now()

    if end is None and days is None:
        raise ValueError("You must provide either 'end' datetime or 'days' range")

    if end is None:
        end = start + timedelta(days=days)

    if start >= end:
        raise ValueError("start must be earlier than end")

    # Pick random datetime
    delta = end - start
    random_second = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_second)


def _random_future_date(current_dt: datetime, min_days: int = 1, max_days: int = 7) -> tuple[date, Any]:
    """Return (date_obj, parsed_date) for a random date in [current + min_days, current + max_days]."""
    offset = randint(min_days, max_days)
    new_date = current_dt.date() + timedelta(days=offset)
    parsed = parser.parse(str(new_date))
    return new_date, parsed


def _apply_less_than_date_guard(parsed_date: Any, current_datetime: datetime) -> Any:
    """Ensure parsed_date is after current_datetime + 1 day when used with LESS_THAN operator."""
    if parsed_date <= (current_datetime + timedelta(days=1)):
        return parsed_date + timedelta(days=1)
    return parsed_date


def _build_date_constraint(field: str, ops: list, min_days: int = 1, max_days: int = 7) -> dict[str, Any]:
    """Build a single date constraint with random future date and optional LESS_THAN guard."""
    current_datetime = datetime.now()
    _, new_date = _random_future_date(current_datetime, min_days=min_days, max_days=max_days)
    op = ComparisonOperator(choice(ops))
    if op == ComparisonOperator.LESS_THAN:
        new_date = _apply_less_than_date_guard(new_date, current_datetime)
    return create_constraint_dict(field, op, new_date.date() if hasattr(new_date, "date") else new_date)


def _build_time_constraint(field: str, ops: list, current_datetime: datetime | None = None) -> dict[str, Any]:
    """Build a single time constraint with random future time from now."""
    current_datetime = current_datetime or datetime.now()
    new_time = _random_future_time_from_now(current_datetime)
    op = ComparisonOperator(choice(ops))
    return create_constraint_dict(field, op, new_time)


def _random_future_time_from_now(current_datetime: datetime) -> time:
    """Return a random time from now onward in 10-minute slots."""
    offset_hours = randint(0, max(0, 23 - current_datetime.hour))
    minute_slot = randrange(0, max(1, 60 - current_datetime.minute), 10)
    future_dt = current_datetime + timedelta(hours=offset_hours)
    if future_dt.hour < current_datetime.hour or (future_dt.hour == current_datetime.hour and minute_slot < current_datetime.minute):
        future_dt = current_datetime
        minute_slot = ((current_datetime.minute + 9) // 10) * 10
        if minute_slot >= 60:
            minute_slot = 0
            future_dt += timedelta(hours=1)
    return time(future_dt.hour, minute_slot)


def _first_available_10min_slot_for_today(current_datetime: datetime | None = None) -> time:
    """Match pickup-now UI default time: now rounded up to the next 10-minute slot."""
    now = current_datetime or datetime.now()
    rounded_minute = now.minute if now.minute % 10 == 0 else now.minute + (10 - (now.minute % 10))
    hour = now.hour

    if rounded_minute == 60:
        hour += 1
        rounded_minute = 0

    # If rounding goes past day boundary, clamp to final valid slot.
    if hour >= 24:
        return time(23, 50)

    return time(hour, rounded_minute)


def _now_optional_utc(use_utc: bool) -> datetime:
    """Return datetime.now(UTC) or datetime.now() to avoid repeating the ternary."""
    return datetime.now(UTC) if use_utc else datetime.now()


def _resolve_special_datetime_field(new_field: dict) -> tuple[Any, Any, str] | None:
    """
    For field configs with is_datetime, is_date, or is_time, return (constraint_value, field_value, new_field_name).
    Returns None if not a special datetime/date/time config.
    """
    use_utc = new_field.get("utc", False)
    current = _now_optional_utc(use_utc)
    new_field_name = new_field.get("field", "")

    if new_field.get("is_datetime"):
        constraint_value = random_datetime(days=new_field.get("days", 1), start=current)
        return (constraint_value, constraint_value, new_field_name)
    if new_field.get("is_date"):
        offset = random.randint(1, 7)
        new_date = current.date() + timedelta(days=offset)
        parsed = parser.parse(str(new_date))
        return (parsed, new_field, new_field_name)
    if new_field.get("is_time"):
        offset_hours = random.randint(0, 23)
        offset_minutes = random.randint(0, 59)
        new_time = current + timedelta(hours=offset_hours, minutes=offset_minutes)
        constraint_value = time(new_time.hour, new_time.minute)
        return (constraint_value, new_field, new_field_name)
    return None


def _generate_constraints(
    dataset: list[dict], field_operators: dict, field_map: dict | None = None, min_constraints: int | None = 1, num_constraints: int | None = None, selected_fields: list | None = None
) -> list[dict[str, Any]]:
    """
    Generates constraints based on the dataset and field operator mapping.
    """
    all_constraints = []
    sample_data = choice(dataset)
    possible_fields = [f for f in field_operators if not (selected_fields and f in selected_fields)]
    selected_fields = selected_fields or []

    if num_constraints is None:
        num_constraints = random.randint(min_constraints, len(possible_fields))

    chosen_fields = random.sample(possible_fields, min(num_constraints, len(possible_fields)))
    selected_fields.extend(chosen_fields)

    field_map = field_map or {}

    for field in selected_fields:
        allowed_ops = field_operators.get(field)
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)

        field_value = None
        constraint_value = None

        if isinstance(new_field, list):
            random.shuffle(new_field)
            for f in new_field:
                val = sample_data.get(f)
                if val is not None:
                    field_value = val
                    new_field = f
                    break
        elif isinstance(new_field, str):
            field_value = sample_data.get(new_field)
        elif isinstance(new_field, dict):
            special = _resolve_special_datetime_field(new_field)
            if special is not None:
                constraint_value, field_value, new_field = special
            else:
                custom_dataset = new_field.get("dataset", [])
                new_field_name = new_field.get("field", "")
                if custom_dataset and new_field_name:
                    field_value = choice(custom_dataset).get(new_field_name)
                    if field_value is not None:
                        constraint_value = _generate_constraint_value(op, field_value, new_field_name, dataset=custom_dataset)
                new_field = new_field_name

        if field_value is None:
            continue

        if constraint_value is None:
            constraint_value = _generate_constraint_value(op, field_value, new_field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


async def _generate_from_places(
    task_url: str | None,
    dataset: list[dict[str, Any]] | None,
    field_operators: dict,
    field_map: dict,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Fetch places and generate constraints; avoids repeating _get_drive_entity_list + _generate_constraints."""
    data = await _get_drive_entity_list(task_url, dataset, "places")
    return _generate_constraints(data, field_operators, field_map=field_map, **kwargs)


def _places_location_destination_field_map(places_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Shared field map for location/destination both using 'label' from places dataset."""
    return {
        "location": {"field": "label", "dataset": places_data},
        "destination": {"field": "label", "dataset": places_data},
    }


async def generate_enter_location_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return await _generate_from_places(task_url, dataset, FIELD_OPERATORS_MAP_ENTER_LOCATION, {"location": "label"})


async def generate_enter_destination_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return await _generate_from_places(task_url, dataset, FIELD_OPERATORS_MAP_ENTER_DESTINATION, {"destination": "label"})


async def generate_see_prices_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    places_data = await _get_drive_entity_list(task_url, dataset, "places")
    return _generate_constraints(
        places_data,
        FIELD_OPERATORS_MAP_SEE_PRICES,
        field_map=_places_location_destination_field_map(places_data),
        num_constraints=2,
    )


def generate_select_date_constraints(
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        # Match pickup-now UI date display format, e.g. "Apr 01, 2026"
        today_value = datetime.now().strftime("%b %d, %Y")
        return [create_constraint_dict("date", ComparisonOperator.EQUALS, today_value)]
    return [_build_date_constraint(field, ops) for field, ops in FIELD_OPERATORS_MAP_SELECT_DATE.items() if field == "date"]


def generate_select_time_constraints(
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        default_slot = _first_available_10min_slot_for_today()
        ui_time_value = datetime.combine(datetime.now().date(), default_slot).strftime("%I:%M %p")
        return [create_constraint_dict("time", ComparisonOperator.EQUALS, ui_time_value)]
    current_datetime = datetime.now()
    return [_build_time_constraint(field, ops, current_datetime) for field, ops in FIELD_OPERATORS_MAP_SELECT_TIME.items() if field == "time"]


def generate_next_pickup_constraints() -> list[dict[str, Any]]:
    current_datetime = datetime.now()
    all_constraints: list[dict[str, Any]] = []
    selected_date: date | None = None

    if "date" in FIELD_OPERATORS_MAP_NEXT_PICKUP:
        constraint = _build_date_constraint("date", FIELD_OPERATORS_MAP_NEXT_PICKUP["date"], min_days=0, max_days=7)
        selected_date = constraint.get("value")
        all_constraints.append(constraint)

    if "time" in FIELD_OPERATORS_MAP_NEXT_PICKUP:
        ops = FIELD_OPERATORS_MAP_NEXT_PICKUP["time"]
        if selected_date is not None and selected_date == current_datetime.date():
            all_constraints.append(_build_time_constraint("time", ops, current_datetime))
        else:
            hour = randint(0, 23)
            minute_slot = randrange(0, 60, 10)
            new_time = time(hour, minute_slot)
            op = ComparisonOperator(choice(ops))
            all_constraints.append(create_constraint_dict("time", op, new_time))

    return all_constraints


def _create_scheduled_constraint(field: str, ops: list) -> dict[str, Any]:
    op = ComparisonOperator(choice(ops))
    current_datetime = datetime.now()
    new_time = _random_future_time_from_now(current_datetime)
    _, new_date = _random_future_date(current_datetime, min_days=1, max_days=7)
    if op == ComparisonOperator.LESS_THAN:
        new_date = _apply_less_than_date_guard(new_date, current_datetime)
    date_time = datetime.combine(new_date.date(), new_time)
    return create_constraint_dict(field, op, date_time)


async def generate_search_ride_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        places_data = await _get_drive_entity_list(task_url, dataset, "places")
        rides_data = await _get_drive_entity_list(task_url, dataset, "rides")
        if len(places_data) < 2 or not rides_data:
            return []

        ride = random.choice(rides_data)
        if not isinstance(ride, dict):
            return []

        valid_place_labels = [p.get("main") for p in places_data if isinstance(p, dict) and p.get("main")]
        valid_place_labels = list({main for main in valid_place_labels if main})
        if len(valid_place_labels) < 2:
            return []

        from_location, to_location = random.sample(valid_place_labels, 2)
        selected_item: dict[str, Any] = {
            "from": from_location,
            "to": to_location,
        }

        ride_field_map = {
            "ride_name": "name",
            "eta": "eta",
            "price": "price",
            "old_price": "oldPrice",
            "description": "desc",
        }
        for out_field, source_field in ride_field_map.items():
            val = ride.get(source_field)
            if val is not None:
                if out_field in {"price", "old_price"}:
                    formatted_value = _format_ui_currency(val)
                    if formatted_value is not None:
                        selected_item[out_field] = formatted_value
                else:
                    selected_item[out_field] = val

        visible_fields = ["from", "to", "ride_name", "eta", "price", "old_price", "description"]
        verify_candidates = [f for f in ["ride_name", "eta", "price", "old_price", "description"] if selected_item.get(f) is not None]
        if not verify_candidates:
            return []

        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
                question_fields_override=["from", "to"],
            )
            or []
        )

    field_ops = FIELD_OPERATORS_MAP_SEARCH_RIDE
    places_data = await _get_drive_entity_list(task_url, dataset, "places")
    constraints_list = _generate_constraints(
        places_data,
        field_ops,
        field_map=_places_location_destination_field_map(places_data),
        selected_fields=["location", "destination"],
    )

    if "scheduled" in FIELD_OPERATORS_MAP_SEARCH_RIDE:
        ops = FIELD_OPERATORS_MAP_SEARCH_RIDE["scheduled"]
        constraint = _create_scheduled_constraint("scheduled", ops)
        constraints_list.append(constraint)

    return constraints_list


async def generate_select_car_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        return await generate_search_ride_constraints(
            task_url=task_url,
            dataset=dataset,
            test_types=test_types,
        )

    fields_ops = FIELD_OPERATORS_MAP_SELECT_CAR.copy()
    scheduled_ops = fields_ops.pop("scheduled")
    places_data = dataset.get("places") if isinstance(dataset, dict) else None
    rides_data = dataset.get("rides") if isinstance(dataset, dict) else None
    places_data = await _get_drive_entity_list(task_url, places_data, "places")
    rides_data = await _get_drive_entity_list(task_url, rides_data, "rides")
    field_map = {
        "location": "label",
        "destination": "label",
        "ride_name": {"field": "name", "dataset": rides_data},
    }
    constraints_list = _generate_constraints(places_data, fields_ops, field_map=field_map, selected_fields=["location", "destination", "ride_name"], num_constraints=3)  # selected_fields=["ride_name"]
    constraints_list.append(_create_scheduled_constraint("scheduled", scheduled_ops))
    return constraints_list


async def generate_reserve_ride_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        return await generate_select_car_constraints(task_url=task_url, dataset=dataset, test_types=test_types)
    constraints_list = await generate_select_car_constraints(task_url, dataset)

    return constraints_list


_SUBMIT_TRIP_REVIEW_RATINGS: list[int | float] = [1, 2, 3, 3, 4, 4, 5, 5]

_SUBMIT_TRIP_REVIEW_REVIEWER_NAMES: list[str] = [
    "Alex Morgan",
    "Jordan Lee",
    "Sam Rivera",
    "Taylor Chen",
    "Riley Brooks",
    "Morgan Patel",
    "Casey Nguyen",
    "Jamie Ortiz",
]

_SUBMIT_TRIP_REVIEW_COMMENTS: list[str] = [
    "Smooth ride; driver was on time.",
    "Clean car and friendly service.",
    "A bit pricey but worth it for the comfort.",
    "Great navigation through traffic.",
    "Pickup was quick and the route felt safe.",
    "Would book again for early airport runs.",
    "Driver was professional and the ETA was accurate.",
    "Comfortable seats; quiet cabin.",
    "Had to wait a few minutes past the window.",
    "Excellent experience overall.",
]


def _submit_trip_review_synthetic_dataset() -> list[dict[str, Any]]:
    """Rows aligned with SubmitTripReviewEvent fields used in constraints."""
    rows: list[dict[str, Any]] = []
    for i, comment in enumerate(_SUBMIT_TRIP_REVIEW_COMMENTS):
        name = _SUBMIT_TRIP_REVIEW_REVIEWER_NAMES[i % len(_SUBMIT_TRIP_REVIEW_REVIEWER_NAMES)]
        rating = _SUBMIT_TRIP_REVIEW_RATINGS[i % len(_SUBMIT_TRIP_REVIEW_RATINGS)]
        rows.append({"rating": rating, "reviewer_name": name, "comment": comment})
    return rows


async def generate_submit_trip_review_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """
    Constraints for trip SUBMIT_REVIEW: rating, reviewer name, message (``comment``),
    and trip details (``pickup``, ``dropoff``, ``price``, ``ride_type``), plus ``trip_id``.
    """
    _ = (task_url, dataset)
    synth = _submit_trip_review_synthetic_dataset()
    if test_types == "data_extraction_only":
        picked = random.choice(synth)
        visible = [f for f in ["rating", "reviewer_name", "comment"] if picked.get(f) is not None]
        if len(visible) < 2:
            return []
        verify_field = random.choice(visible)
        return _build_data_extraction_result(picked, visible, verify_field=verify_field) or []

    selected = ["rating", "reviewer_name", "comment"]
    sample_row = random.choice(synth)
    constraints: list[dict[str, Any]] = []
    for field in selected:
        allowed_ops = FIELD_OPERATORS_MAP_SUBMIT_TRIP_REVIEW.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        raw = sample_row[field]
        value = _generate_constraint_value(operator, raw, field, synth)
        if value is not None:
            constraints.append(create_constraint_dict(field, operator, value))
    return constraints


async def generate_view_available_trips_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    _ = (task_url, dataset)
    op = ComparisonOperator(choice(FIELD_OPERATORS_MAP_VIEW_AVAILABLE_TRIPS["total_trips"]))
    return [create_constraint_dict("total_trips", op, randint(1, 12))]


async def generate_book_trip_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    base = await generate_reserve_ride_constraints(task_url, dataset)
    op_t = ComparisonOperator(choice(FIELD_OPERATORS_MAP_BOOK_TRIP["trip_id"]))
    base.append(create_constraint_dict("trip_id", op_t, f"trip-{randint(1, 99)}"))
    op_s = ComparisonOperator(choice(FIELD_OPERATORS_MAP_BOOK_TRIP["source"]))
    base.append(create_constraint_dict("source", op_s, "available_trips"))
    return base


async def generate_filter_trips_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    _ = dataset
    places_data = await _get_drive_entity_list(task_url, None, "places")
    loc = choice(places_data).get("label", "San Francisco") if places_data else "San Francisco"
    ft_ops = FIELD_OPERATORS_MAP_FILTER_TRIPS["filter_type"]
    fv_ops = FIELD_OPERATORS_MAP_FILTER_TRIPS["filter_value"]
    return [
        create_constraint_dict("filter_type", ComparisonOperator(choice(ft_ops)), "location"),
        create_constraint_dict("filter_value", ComparisonOperator(choice(fv_ops)), loc),
    ]


async def generate_trip_details_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        trip_cards = [
            {"title": "1 Hotel San Francisco", "datetime": "7/17/2025 - 11:21:08 AM", "price": 26.6},
            {"title": "The Landing San Francisco Apartments", "datetime": "6/13/2024 - 6:17:48 PM", "price": 24.7},
            {"title": "Avis Car Rental", "datetime": "6/13/2024 - 10:45:32 AM", "price": 24.7},
            {"title": "The Landing San Francisco Apartments", "datetime": "6/12/2024 - 9:04:31 PM", "price": 19.0},
        ]
        selected_card = random.choice(trip_cards)
        if not isinstance(selected_card, dict):
            return []

        raw_price = selected_card.get("price")
        price_str = f"${int(raw_price) if raw_price.is_integer() else raw_price}"
        if price_str is None:
            return []

        dt = selected_card.get("datetime")
        date_part, time_part = dt.split("-")

        selected_item: dict[str, Any] = {"title": selected_card.get("title"), "price": price_str, "date": date_part, "time": time_part}
        visible_fields = ["title", "date", "price", "time"]
        return (
            _build_data_extraction_result(
                selected_item,
                visible_fields,
            )
            or []
        )

    constraints_list = await generate_select_car_constraints(task_url, dataset)
    return constraints_list
