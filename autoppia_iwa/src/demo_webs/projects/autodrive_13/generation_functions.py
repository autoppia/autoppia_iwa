import random
from datetime import date, datetime, time, timedelta
from random import choice, randint, randrange
from typing import Any

from dateutil import parser

from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_MAP_ENTER_DESTINATION,
    FIELD_OPERATORS_MAP_ENTER_LOCATION,
    FIELD_OPERATORS_MAP_NEXT_PICKUP,
    FIELD_OPERATORS_MAP_SEARCH_RIDE,
    FIELD_OPERATORS_MAP_SEE_PRICES,
    FIELD_OPERATORS_MAP_SELECT_CAR,
    FIELD_OPERATORS_MAP_SELECT_DATE,
    FIELD_OPERATORS_MAP_SELECT_TIME,
)
from .data_utils import extract_drive_dataset, fetch_drive_data


async def _get_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 100,
) -> list[dict]:
    return await fetch_drive_data(
        entity_type=entity_type,
        method=method,
        filter_key=filter_key,
        seed_value=seed_value,
        count=count,
    )


async def _ensure_drive_dataset(
    task_url: str | None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> list[dict[str, Any]]:
    """Ensure dataset for the given entity type is available."""
    existing = extract_drive_dataset(dataset, entity_type)
    if existing is not None:
        return existing
    v2_seed = await resolve_v2_seed_from_url(task_url)
    return await _get_data(entity_type=entity_type, method=method, filter_key=filter_key, seed_value=v2_seed)


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

    if operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    if operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

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
            if new_field.get("is_datetime"):
                days = new_field.get("days", 1)
                new_field_name = new_field.get("field", "")
                current_datetime = datetime.now(timezone.utc) if new_field.get("utc") else datetime.now()
                constraint_value = random_datetime(days=days, start=current_datetime)
                field_value = constraint_value
                new_field = new_field_name

            elif new_field.get("is_date"):
                current_datetime = datetime.now(timezone.utc) if new_field.get("utc") else datetime.now()
                offset = random.randint(1, 7)
                new_date = current_datetime.date() + timedelta(days=offset)
                new_date = parser.parse(str(new_date))
                constraint_value = new_date
                field_value = new_field

            elif new_field.get("is_time"):
                current_datetime = datetime.now(timezone.utc) if new_field.get("utc") else datetime.now()
                offset_hours = random.randint(0, 23)
                offset_minutes = random.randint(0, 59)
                new_time = current_datetime + timedelta(hours=offset_hours, minutes=offset_minutes)
                new_time = time(new_time.hour, new_time.minute)
                constraint_value = new_time
                field_value = new_field

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


async def generate_enter_location_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    field_map = {"location": "label"}
    field_operators = FIELD_OPERATORS_MAP_ENTER_LOCATION
    dataset = await _ensure_drive_dataset(task_url, dataset, entity_type="places")
    constraints_list = _generate_constraints(dataset, field_operators, field_map=field_map)
    return constraints_list


async def generate_enter_destination_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    field_map = {"destination": "label"}
    field_operators = FIELD_OPERATORS_MAP_ENTER_DESTINATION
    dataset = await _ensure_drive_dataset(task_url, dataset, entity_type="places")
    constraints_list = _generate_constraints(dataset, field_operators, field_map=field_map)
    return constraints_list


async def generate_see_prices_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    dataset = await _ensure_drive_dataset(task_url, dataset, entity_type="places")
    field_mapping = {
        "location": {"field": "label", "dataset": dataset},
        "destination": {"field": "label", "dataset": dataset},
    }
    field_operators = FIELD_OPERATORS_MAP_SEE_PRICES
    constraints_list = _generate_constraints(dataset, field_operators, field_mapping, num_constraints=2)
    return constraints_list


def generate_select_date_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    for field, ops in FIELD_OPERATORS_MAP_SELECT_DATE.items():
        if field == "date":
            current_datetime = datetime.now()
            offset = random.randint(1, 7)
            new_date = current_datetime.date() + timedelta(days=offset)
            new_date = parser.parse(str(new_date))
            op = ComparisonOperator(choice(ops))
            if op == ComparisonOperator.LESS_THAN and new_date <= (current_datetime + timedelta(days=1)):
                new_date = new_date + timedelta(days=1)
            constraint = create_constraint_dict(field, op, new_date.date())
            all_constraints.append(constraint)
    return all_constraints


def generate_select_time_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    for field, ops in FIELD_OPERATORS_MAP_SELECT_TIME.items():
        if field == "time":
            current_datetime = datetime.now()
            offset_hours = random.randint(0, 23 - current_datetime.hour)
            minute_slot = random.randrange(0, 60 - current_datetime.minute, 10)

            future_dt = current_datetime + timedelta(hours=offset_hours)
            # Ensure the new time is not before the current time
            if future_dt.hour < current_datetime.hour or (future_dt.hour == current_datetime.hour and minute_slot < current_datetime.minute):
                future_dt = current_datetime
                minute_slot = ((current_datetime.minute + 9) // 10) * 10
                if minute_slot >= 60:
                    minute_slot = 0
                    future_dt += timedelta(hours=1)
            new_time = time(future_dt.hour, minute_slot)
            op = ComparisonOperator(choice(ops))
            constraint = create_constraint_dict(field, op, new_time)
            all_constraints.append(constraint)
    return all_constraints


def generate_next_pickup_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    current_datetime = datetime.now()
    selected_date = None

    # -------------------------
    # Handle DATE constraint
    # -------------------------
    if "date" in FIELD_OPERATORS_MAP_NEXT_PICKUP:
        ops = FIELD_OPERATORS_MAP_NEXT_PICKUP["date"]
        field = "date"

        offset = randint(0, 7)  # allow today as well (offset=0)
        new_date = current_datetime.date() + timedelta(days=offset)
        selected_date = new_date
        new_date = parser.parse(str(new_date))

        op = ComparisonOperator(choice(ops))
        # Avoid making invalid constraints for < operator
        if op == ComparisonOperator.LESS_THAN and new_date <= (current_datetime + timedelta(days=1)):
            new_date = new_date + timedelta(days=1)

        constraint = create_constraint_dict(field, op, new_date.date())
        all_constraints.append(constraint)

    # -------------------------
    # Handle TIME constraint
    # -------------------------
    if "time" in FIELD_OPERATORS_MAP_NEXT_PICKUP:
        ops = FIELD_OPERATORS_MAP_NEXT_PICKUP["time"]
        field = "time"

        if selected_date == current_datetime.date():
            # Case: date is today → pick time from now onward
            offset_hours = randint(0, 23 - current_datetime.hour)
            minute_slot = randrange(0, 60 - current_datetime.minute, 10)

            future_dt = current_datetime + timedelta(hours=offset_hours)
            # Ensure not earlier than current time
            if future_dt.hour < current_datetime.hour or (future_dt.hour == current_datetime.hour and minute_slot < current_datetime.minute):
                future_dt = current_datetime
                minute_slot = ((current_datetime.minute + 9) // 10) * 10
                if minute_slot >= 60:
                    minute_slot = 0
                    future_dt += timedelta(hours=1)

            new_time = time(future_dt.hour, minute_slot)

        else:
            # Case: future date → allow any random time
            hour = randint(0, 23)
            minute_slot = randrange(0, 60, 10)
            new_time = time(hour, minute_slot)

        op = ComparisonOperator(choice(ops))
        constraint = create_constraint_dict(field, op, new_time)
        all_constraints.append(constraint)

    return all_constraints


def _create_scheduled_constraint(field, ops):
    op = ComparisonOperator(choice(ops))
    current_datetime = datetime.now()
    offset_hours = random.randint(0, 23 - current_datetime.hour)
    minute_slot = random.randrange(0, 60 - current_datetime.minute, 10)
    future_dt = current_datetime + timedelta(hours=offset_hours)

    # Ensure the new time is not before the current time
    if future_dt.hour < current_datetime.hour or (future_dt.hour == current_datetime.hour and minute_slot < current_datetime.minute):
        future_dt = current_datetime
        minute_slot = ((current_datetime.minute + 9) // 10) * 10
        if minute_slot >= 60:
            minute_slot = 0
            future_dt += timedelta(hours=1)

    new_time = time(future_dt.hour, minute_slot)
    offset = random.randint(1, 7)
    new_date = current_datetime.date() + timedelta(days=offset)
    new_date = parser.parse(str(new_date))

    if op == ComparisonOperator.LESS_THAN and new_date <= (current_datetime + timedelta(days=1)):
        new_date = new_date + timedelta(days=1)

    date_time = datetime.combine(new_date, new_time)
    constraint = create_constraint_dict(field, op, date_time)
    return constraint


async def generate_search_ride_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_SEARCH_RIDE
    dataset = await _ensure_drive_dataset(task_url, dataset, entity_type="places")

    field_map = {
        "location": {"field": "label", "dataset": dataset},
        "destination": {"field": "label", "dataset": dataset},
    }
    constraints_list = _generate_constraints(dataset, field_ops, field_map=field_map, selected_fields=["location", "destination"])

    if "scheduled" in FIELD_OPERATORS_MAP_SEARCH_RIDE:
        ops = FIELD_OPERATORS_MAP_SEARCH_RIDE["scheduled"]
        constraint = _create_scheduled_constraint("scheduled", ops)
        constraints_list.append(constraint)

    return constraints_list


async def generate_select_car_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    fields_ops = FIELD_OPERATORS_MAP_SELECT_CAR.copy()
    scheduled_ops = fields_ops.pop("scheduled")
    places_data = None
    rides_data = None
    if isinstance(dataset, dict):
        places_data = dataset.get("places")
        rides_data = dataset.get("rides")
    places_data = await _ensure_drive_dataset(task_url, places_data, entity_type="places")
    rides_data = await _ensure_drive_dataset(task_url, rides_data, entity_type="rides")
    field_map = {
        "location": "label",
        "destination": "label",
        "ride_name": {"field": "name", "dataset": rides_data},
    }
    constraints_list = _generate_constraints(places_data, fields_ops, field_map=field_map, selected_fields=["location", "destination", "ride_name"], num_constraints=3)  # selected_fields=["ride_name"]
    constraints_list.append(_create_scheduled_constraint("scheduled", scheduled_ops))
    return constraints_list


async def generate_reserve_ride_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = await generate_select_car_constraints(task_url, dataset)

    return constraints_list
