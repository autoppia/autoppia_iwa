import random
from datetime import datetime, timedelta
from random import choice
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import FIELD_OPERATORS_CONNECT_WITH_USER_MAP, FIELD_OPERATORS_POST_STATUS_MAP, FIELD_OPERATORS_VIEW_USER_PROFILE_MAP, mockUsers


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None
    if field == "amenities" and isinstance(field_value, list):
        field_value = choice(field_value) if field_value else ""

    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        elif operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        elif operator == ComparisonOperator.GREATER_EQUAL or operator == ComparisonOperator.LESS_EQUAL or operator == ComparisonOperator.EQUALS:
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
            valid = [v[f] for v in dataset for f in field_value if v.get(f) and v.get(f) != field_value]
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


def generate_view_user_profile_constraints() -> list[dict[str, Any]]:
    """
    Generates constraints for viewing a user profile based on the provided user profile data.
    """
    all_constraints = []

    dataset = mockUsers
    user_profile = choice(dataset)
    operators_allowed = FIELD_OPERATORS_VIEW_USER_PROFILE_MAP

    possible_fields = list(operators_allowed.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = operators_allowed.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(choice(allowed_ops))
        field_value = user_profile.get(field)
        if field_value is None:
            continue

        # Generate a constraint value based on the operator and field value
        constraint_value = _generate_constraint_value(op, field_value, field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


def generate_connect_with_user_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    dataset = mockUsers
    user_profile = choice(dataset)
    operators_allowed = FIELD_OPERATORS_CONNECT_WITH_USER_MAP

    selected_fields = random.sample(list(operators_allowed.keys()), 1)
    field_map = {
        "target_name": "name",
        "target_username": "username",
    }
    for field in selected_fields:
        allowed_ops = operators_allowed.get(field, [])
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        new_field = field_map.get(field, field)
        field_value = user_profile.get(new_field)

        if field_value is None:
            continue

        # Generate a constraint value based on the operator and field value
        constraint_value = _generate_constraint_value(op, field_value, new_field, dataset)

        if constraint_value is not None:
            constraint = create_constraint_dict(field, op, constraint_value)
            all_constraints.append(constraint)

    return all_constraints


sample_post_contents = [
    "Excited to join LinkedIn Lite!",
    "Just released a minimal LinkedIn clone with Next.js and Tailwind CSS! 🚀",
    "Attended a fantastic webinar on remote team collaboration today! Highly recommend it.",
    "Started learning TypeScript this week. Any tips for a React dev?",
    "Just finished a 10k run for charity. Feeling accomplished!",
    "Reading 'Inspired' by Marty Cagan. Game changer for product managers!",
    "Just launched our summer brand campaign. Feeling proud of the team! 🌞📣",
    "Migrated 20+ services to Kubernetes today. DevOps win! ⚙️🐳",
    "Hosting our first DEI panel at PeopleFirst. Let's build inclusive cultures. 🌈",
    "Experimenting with fine-tuning LLMs on small domain datasets. Results look promising.",
    "We just hit 10K users on RemoteWorks! 💪 Thank you for believing in us.",
    "Published a new research paper on GNNs and edge inference. DM for collab. 📄📊",
    "Launched our beta app today—can't wait for your feedback!",
    "Tried out the new GPT-4o model. Mind blown 🤯",
    "Remote work has changed how we build products. Flexibility = productivity.",
    "Had a great time mentoring at today's hackathon!",
    "Weekly reminder: take breaks, breathe, and trust your process.",
    "Redesigned our onboarding flow—conversion is up 18%!",
    "Learning Rust has been surprisingly fun and powerful.",
    "Attending React Summit next month—who else is going?",
]


def generate_post_status_constraints() -> list[dict[str, Any]]:
    all_constraints = []
    field = "content"
    operators_allowed = FIELD_OPERATORS_POST_STATUS_MAP
    op = ComparisonOperator(choice(operators_allowed[field]))
    field_value = choice(sample_post_contents)
    value = _generate_constraint_value(op, field_value, field, sample_post_contents)
    constraint = create_constraint_dict(field, op, value)
    all_constraints.append(constraint)

    return all_constraints
