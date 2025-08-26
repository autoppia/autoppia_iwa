import random
from datetime import UTC, date, datetime, time, timedelta
from random import choice
from typing import Any

from dateutil import parser

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    DISCOUNT_PERCENTAGE_DATA,
    FIELD_OPERATORS_MAP_CANCEL_RESERVATION,
    FIELD_OPERATORS_MAP_ENTER_DESTINATION,
    FIELD_OPERATORS_MAP_ENTER_LOCATION,
    FIELD_OPERATORS_MAP_NEXT_PICKUP,
    FIELD_OPERATORS_MAP_RESERVE_RIDE,
    FIELD_OPERATORS_MAP_SEARCH_RIDE,
    FIELD_OPERATORS_MAP_SEE_PRICES,
    FIELD_OPERATORS_MAP_SELECT_CAR,
    FIELD_OPERATORS_MAP_SELECT_DATE,
    FIELD_OPERATORS_MAP_SELECT_TIME,
    FIELD_OPERATORS_MAP_TRIP_DETAILS,
    PLACES,
    RIDES,
    TRIPS,
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
                constraint_value = random_datetime(days=days, start=datetime.now(UTC))
                field_value = constraint_value
                new_field = new_field_name

            elif new_field.get("is_date"):
                current_date = datetime.now(UTC)
                offset = random.randint(1, 7)
                new_date = current_date.date() + timedelta(days=offset)
                new_date = parser.parse(str(new_date))
                constraint_value = new_date
                field_value = new_field

            elif new_field.get("is_time"):
                current_time = datetime.now(UTC)
                offset_hours = random.randint(0, 23)
                offset_minutes = random.randint(0, 59)
                new_time = current_time + timedelta(hours=offset_hours, minutes=offset_minutes)
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


def generate_enter_location_constraints() -> list[dict[str, Any]]:
    field_map = {"location": "label"}
    field_operators = FIELD_OPERATORS_MAP_ENTER_LOCATION
    constraints_list = _generate_constraints(PLACES, field_operators, field_map=field_map)
    return constraints_list


def generate_enter_destination_constraints() -> list[dict[str, Any]]:
    field_map = {"destination": "label"}
    field_operators = FIELD_OPERATORS_MAP_ENTER_DESTINATION
    constraints_list = _generate_constraints(PLACES, field_operators, field_map=field_map)
    return constraints_list


def generate_see_prices_constraints() -> list[dict[str, Any]]:
    field_mapping = {
        "location": {"field": "label", "dataset": PLACES},
        "destination": {"field": "label", "dataset": PLACES},
    }
    field_operators = FIELD_OPERATORS_MAP_SEE_PRICES
    constraints_list = _generate_constraints(PLACES, field_operators, field_mapping)
    return constraints_list


def generate_select_date_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    for field, ops in FIELD_OPERATORS_MAP_SELECT_DATE.items():
        if field == "date":
            current_date = datetime.now()
            offset = random.randint(1, 7)
            new_date = current_date.date() + timedelta(days=offset)
            new_date = parser.parse(str(new_date))
            op = ComparisonOperator(choice(ops))
            if op == ComparisonOperator.LESS_THAN and new_date <= (current_date + timedelta(days=1)):
                new_date = new_date + timedelta(days=1)
            constraint = create_constraint_dict(field, op, new_date.date())
            all_constraints.append(constraint)
    return all_constraints


def generate_select_time_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    for field, ops in FIELD_OPERATORS_MAP_SELECT_TIME.items():
        if field == "time":
            current_time = datetime.now()
            offset_hours = random.randint(0, 23 - current_time.hour)
            minute_slot = random.randrange(0, 60 - current_time.minute, 10)

            future_dt = current_time + timedelta(hours=offset_hours)
            # Ensure the new time is not before the current time
            if future_dt.hour < current_time.hour or (future_dt.hour == current_time.hour and minute_slot < current_time.minute):
                future_dt = current_time
                minute_slot = ((current_time.minute + 9) // 10) * 10
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
    for field, ops in FIELD_OPERATORS_MAP_NEXT_PICKUP.items():
        if field == "date":
            current_date = datetime.now(UTC)
            offset = random.randint(1, 7)
            new_date = current_date.date() + timedelta(days=offset)
            new_date = parser.parse(str(new_date))
            op = ComparisonOperator(choice(ops))
            constraint = create_constraint_dict(field, op, new_date)
            all_constraints.append(constraint)

        if field == "time":
            current_time = datetime.now(UTC)
            offset_hours = random.randint(0, 23)
            offset_minutes = random.randint(0, 59)

            new_time = current_time + timedelta(hours=offset_hours, minutes=offset_minutes)
            new_time = time(new_time.hour, new_time.minute)
            op = ComparisonOperator(choice(ops))
            constraint = create_constraint_dict(field, op, new_time)
            all_constraints.append(constraint)

    return all_constraints


def generate_search_ride_constraints() -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_SEARCH_RIDE

    field_map = {
        "pickup": {"field": "label", "dataset": PLACES},
        "dropoff": {"field": "label", "dataset": PLACES},
        "scheduled": {"is_datetime": True, "days": 7, "field": "scheduled"},
    }
    constraints_list = _generate_constraints(PLACES, field_ops, field_map=field_map, selected_fields=["scheduled"])
    return constraints_list


def generate_select_car_constraints() -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_SELECT_CAR
    field_map = {
        # "discount_percentage": {"field": "discount_percentage", "dataset": [{"discount_percentage": d} for d in ["5%", "10%", "15%"]]},
        "discount_percentage": {"field": "discount_percentage", "dataset": DISCOUNT_PERCENTAGE_DATA},
        "old_price": {"field": "oldPrice", "dataset": RIDES},
        # "pick_up": {"field": "pickup", "dataset": TRIPS},
        "pick_up": "pickup",
        "ride_id": "id",
        "ride_name": {"field": "name", "dataset": RIDES},
        "scheduled": {"is_datetime": True, "days": 7, "field": "scheduled"},
        "seats": {"field": "seats", "dataset": RIDES},
    }
    constraints_list = _generate_constraints(TRIPS, field_ops, field_map=field_map, selected_fields=["dropoff", "old_price"])
    return constraints_list


def generate_reserve_ride_constraints() -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_RESERVE_RIDE
    field_map = {
        "discount_percentage": {"field": "discount_percentage", "dataset": DISCOUNT_PERCENTAGE_DATA},
        "old_price": {"field": "oldPrice", "dataset": RIDES},
        "pick_up": "pickup",
        "ride_id": "id",
        "ride_name": {"field": "name", "dataset": RIDES},
        "scheduled": {"is_datetime": True, "days": 7, "field": "scheduled"},
        "seats": {"field": "seats", "dataset": RIDES},
    }
    constraints_list = _generate_constraints(TRIPS, field_ops, field_map=field_map)
    return constraints_list


def generate_trip_details_constraints() -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_TRIP_DETAILS
    field_map = {
        "date": {"is_date": True, "field": "date"},
        "time": {"is_time": True, "field": "time"},
        "drop_off": "label",
        "drop_off_label": "main",
        "pick_up": "label",
        "pick_up_label": "main",
        "price": {"field": "price", "dataset": RIDES},
        "ride_name": {"field": "name", "dataset": RIDES},
    }
    constraints_list = _generate_constraints(PLACES, field_ops, field_map=field_map)
    return constraints_list


def generate_cancel_reservation_constraints() -> list[dict[str, Any]]:
    field_ops = FIELD_OPERATORS_MAP_CANCEL_RESERVATION
    field_map = {
        "date": {"is_date": True, "field": "date"},
        "time": {"is_time": True, "field": "time"},
        "drop_off": "label",
        "drop_off_label": "main",
        "pick_up": "label",
        "pick_up_label": "main",
        "price": {"field": "price", "dataset": RIDES},
        "ride_name": {"field": "name", "dataset": RIDES},
    }
    constraints_list = _generate_constraints(PLACES, field_ops, field_map=field_map)
    return constraints_list
