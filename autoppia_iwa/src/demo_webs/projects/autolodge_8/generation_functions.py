import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import DASHBOARD_HOTELS, FIELD_OPERATORS_SEARCH_HOTEL_MAP, REGION_HOTELS


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(field_value, str):
            valid = [v[field] for v in dataset if v.get(field) != field_value]
            return random.choice(valid) if valid else None
        elif isinstance(field_value, list):
            valid = [v[field] for v in dataset for f in field_value if v.get(f) != field_value]
            return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        while True:
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str

    elif operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float)]
        if numeric_values:
            base = random.choice(numeric_values)
            delta = random.uniform(1, 3)
            if operator == ComparisonOperator.GREATER_THAN:
                return round(base - delta, 2)
            elif operator == ComparisonOperator.LESS_THAN:
                return round(base + delta, 2)
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                return round(base, 2)

    return value


def generate_search_hotel_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = [
        "search_term",
        "date_from",
        "date_to",
        "adults",
        "children",
        "infants",
        "pets",
    ]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    sample_hotel = random.choice(REGION_HOTELS + DASHBOARD_HOTELS)

    # Dummy guests and date ranges to simulate constraint values
    sample_guests = {
        "adults": random.randint(1, 4),
        "children": random.randint(0, 2),
        "infants": random.randint(0, 1),
        "pets": random.randint(0, 1),
    }

    sample_dates = {"date_from": "2025-07-25", "date_to": "2025-07-28"}

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SEARCH_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        if field == "search_term":
            value = sample_hotel.get("location", {}).get("name") or sample_hotel.get("title")
        elif field in ["date_from", "date_to"]:
            value = sample_dates.get(field)
        else:
            value = sample_guests.get(field, 0)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list
