import random
from random import choice
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict
from .data import (
    EXPERTS,
    EXPERTS_IN_WORK,
    EXPERTS_IN_WORK_MODIFIED,
    FIELD_OPERATORS_MAP_HIRE_BUTTON,
    FIELD_OPERATORS_MAP_HIRING_CONSULTANT,
    FIELD_OPERATORS_MAP_HIRING_TEAM,
    FIELD_OPERATORS_MAP_USER_BOOK_CONSULTANT,
)


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
        base = field_value

        if isinstance(base, int | float):
            if field == "rating":
                min_val, max_val = 0.0, 5.0
                if operator == ComparisonOperator.GREATER_THAN:
                    if base > min_val:
                        min_dataset = min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                        return round(random.uniform(min_dataset, max(base - 0.5, min_dataset)), 2)
                    else:
                        return min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                elif operator == ComparisonOperator.LESS_THAN:
                    if base < max_val:
                        max_dataset = max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                        return round(random.uniform(min(base + 0.1, max_dataset), max_dataset), 2)
                    else:
                        return max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return round(base, 2)
            else:
                # Generic numeric logic
                delta = random.uniform(0.5, 2.0) if isinstance(base, float) else random.randint(1, 5)
                if operator == ComparisonOperator.GREATER_THAN:
                    return base - delta
                elif operator == ComparisonOperator.LESS_THAN:
                    return base + delta
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return base
    return value


def generate_book_consultant_constraint() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field_mapping = {
        "country": "country",
        "expertName": "name",
        "jobs": "jobs",
        "rate": "rate",
        "rating": "rating",
        "role": "role",
    }
    # possible_fields = [field_mapping[field] for field in field_mapping.keys()]

    possible_fields = ["country", "expertName", "jobs", "rate", "rating", "role"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    sample_expert = random.choice(
        EXPERTS
    )  # go to web_demo project code then go to autoweb10 then go to library file and there we have event.ts file where each events define and their data, we can simply check where data comes by clicking event name

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_USER_BOOK_CONSULTANT.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        new_field = field_mapping.get(field, field)
        field_value = sample_expert.get(new_field)

        value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_hire_button_clicked_constraint() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field_mapping = {
        "country": "country",
        "expertName": "name",
        "expertSlug": "slug",
        "role": "role",
    }
    # possible_fields = [field_mapping[field] for field in field_mapping.keys()]
    possible_fields = ["country", "expertName", "expertSlug", "role"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    # team = ["a","b"]
    sample_expert = random.choice(EXPERTS_IN_WORK)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_HIRE_BUTTON.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        # if field == "team":
        #     field_value = choice(team)
        #     dataset = [{'team': t} for t in team]
        #     value = _generate_constraint_value(operator, field_value, field, dataset=dataset)
        # else:
        new_field = field_mapping.get(field, field)
        field_value = sample_expert.get(new_field)

        value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS_IN_WORK)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_select_hiring_team_constraint() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field_mapping = {
        "expertName": "name",
        "expertSlug": "slug",
        "team": "team",
    }
    # possible_fields = [field_mapping[field] for field in field_mapping.keys()]
    possible_fields = ["expertName", "expertSlug", "team"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    sample_expert = random.choice(EXPERTS_IN_WORK)

    team = ["Microsoft", "Apple", "Google"]

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_HIRING_TEAM.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "team":
            field_value = choice(team)
            dataset = [{"team": t} for t in team]
            value = _generate_constraint_value(operator, field_value, field, dataset=dataset)
        else:
            new_field = field_mapping.get(field, field)
            field_value = sample_expert.get(new_field)
            value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_hire_consultation_constraint() -> list[dict[str, Any]]:
    constraints_list = []
    field_mapping = {
        "country": "country",
        "expertName": "name",
        "expertSlug": "slug",
        "role": "role",
        "increaseHowMuch": "increaseHowMuch",
        "increaseWhen": "increaseWhen",
        "paymentType": "paymentType",
        "rate": "lastReviewRate",
    }
    # possible_fields = [field_mapping[field] for field in field_mapping.keys()]
    possible_fields = ["country", "expertName", "expertSlug", "increaseHowMuch", "increaseWhen", "paymentType", "role", "rate"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    payment_type = ["fixed", "hourly"]
    increase_how_much = ["5%", "10%", "15%"]
    increase_when = ["Never", "After 3 months", "After 6 months", "After 12 months"]
    random.choice(EXPERTS_IN_WORK_MODIFIED)
    sample_expert = random.choice(EXPERTS_IN_WORK_MODIFIED)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_HIRING_CONSULTANT.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        if field == "paymentType":
            field_value = random.choice(payment_type)
            payment_dataset = [{"paymentType": p} for p in payment_type]
            value = _generate_constraint_value(operator, field_value, field, dataset=payment_dataset)

        elif field == "increaseHowMuch":
            field_value = random.choice(increase_how_much)
            increase_when_dataset = [{"increaseWhen": p} for p in increase_how_much]
            value = _generate_constraint_value(operator, field_value, field, dataset=increase_when_dataset)

        elif field == "increaseWhen":
            field_value = random.choice(increase_when)
            increase_when_dataset = [{"increaseWhen": p} for p in increase_when]
            value = _generate_constraint_value(operator, field_value, field, dataset=increase_when_dataset)

        else:
            new_field = field_mapping.get(field, field)
            field_value = sample_expert.get(new_field)
            value = _generate_constraint_value(operator, field_value, new_field, dataset=EXPERTS_IN_WORK_MODIFIED)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


# def generate_cancel_hire_consultation_constraint() -> list[dict[str, Any]]:
#     constraints_list = []
