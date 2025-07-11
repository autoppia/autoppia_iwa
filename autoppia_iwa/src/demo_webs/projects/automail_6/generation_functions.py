import random
from random import choice
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    EMAILS_DATA_MODIFIED,
    FIELD_OPERATORS_IMPORTANT_MAP,
    FIELD_OPERATORS_MAP_VIEW_EMAIL,
    FIELD_OPERATORS_READ_MAP,
    FIELD_OPERATORS_STARRED_MAP,
)

# def _generate_value_for_field(field_name, operator):
#     if field_name == 'subject':
#         if operator == ComparisonOperator.EQUALS:
#             return random.choice([email['subject'] for email in EMAILS_DATA if field_name == email['subject']])
#         elif operator == ComparisonOperator.NOT_EQUALS:
#             return random.choice([email['subject'] for email in EMAILS_DATA if field_name != email['subject']])
#         elif operator == ComparisonOperator.CONTAINS:
#             return random.choice([email['subject'] for email in EMAILS_DATA if field_name in email['subject']])
#         elif operator == ComparisonOperator.NOT_CONTAINS:
#             return random.choice([email['subject'] for email in EMAILS_DATA if field_name not in email['subject']])
#
#     if field_name == 'from_email':
#         email = None
#         if operator == ComparisonOperator.EQUALS:
#             email = random.choice([email for email in EMAILS_DATA if field_name == email['from']['email']])
#         elif operator == ComparisonOperator.NOT_EQUALS:
#             email = random.choice([email for email in EMAILS_DATA if field_name != email['from']['email']])
#         elif operator == ComparisonOperator.CONTAINS:
#             email = random.choice([email for email in EMAILS_DATA if field_name in email['from']['email']])
#         elif operator == ComparisonOperator.NOT_CONTAINS:
#             email = random.choice([email for email in EMAILS_DATA if field_name not in email['from']['email']])
#
#         if email:
#             return email['from']['email']
#
#     print(f"Warning: No specific mock value generator for field '{field_name}'. Using default string.")
#     return "mock_value"


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) != field_value]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        return random.choice(valid) if valid else None

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


def generate_view_email_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_MAP_VIEW_EMAIL.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    email = choice(EMAILS_DATA_MODIFIED)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_VIEW_EMAIL.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_is_starred_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_STARRED_MAP.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    email = choice(EMAILS_DATA_MODIFIED)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_STARRED_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_is_read_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_READ_MAP.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    email = choice(EMAILS_DATA_MODIFIED)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_STARRED_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_is_important_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_IMPORTANT_MAP.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    email = choice(EMAILS_DATA_MODIFIED)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_STARRED_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list
