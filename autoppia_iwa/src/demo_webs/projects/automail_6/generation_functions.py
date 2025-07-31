import random
from random import choice
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..operators import EQUALS, NOT_EQUALS
from ..shared_utils import create_constraint_dict
from .data import (
    ALL_EMAIL_WORDS,
    EMAILS_DATA_MODIFIED,
    FIELD_OPERATORS_ADD_LABEL_MAP,
    FIELD_OPERATORS_CREATE_LABEL_MAP,
    FIELD_OPERATORS_IMPORTANT_MAP,
    FIELD_OPERATORS_IS_READ_MAP,
    FIELD_OPERATORS_IS_SPAM_MAP,
    FIELD_OPERATORS_SEARCH_MAP,
    FIELD_OPERATORS_SEND_OR_DRAFT_EMAIL_MAP,
    FIELD_OPERATORS_STARRED_MAP,
    FIELD_OPERATORS_VIEW_EMAIL_MAP,
)


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
        if isinstance(field_value, str) and "\n" in field_value:
            parts = [part for part in field_value.split("\n") if part.strip()]
            if parts:
                field_value = max(parts, key=len)
                return field_value
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


def generate_view_email_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = list(FIELD_OPERATORS_VIEW_EMAIL_MAP.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    email = choice(EMAILS_DATA_MODIFIED)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_VIEW_EMAIL_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def _boolean_constraints_value(value, operator: ComparisonOperator) -> bool:
    if operator == ComparisonOperator.EQUALS:
        return bool(value)
    elif operator == ComparisonOperator.NOT_EQUALS:
        return not bool(value)


def generate_is_starred_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    email = choice(EMAILS_DATA_MODIFIED)
    fixed_field = "is_starred"
    op = ComparisonOperator(random.choice(FIELD_OPERATORS_STARRED_MAP[fixed_field]))
    field_value = not email.get(fixed_field, False)
    constraints_list.append(create_constraint_dict(fixed_field, op, field_value))

    possible_fields = [item for item in FIELD_OPERATORS_STARRED_MAP if item != fixed_field]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

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
    fixed_field = "is_read"
    field_value = False

    email = next((e for e in EMAILS_DATA_MODIFIED if e.get(fixed_field) is True), None)
    if not email:
        email = choice(EMAILS_DATA_MODIFIED)
    op = ComparisonOperator(choice(FIELD_OPERATORS_IS_READ_MAP[fixed_field]))
    constraints_list.append(create_constraint_dict(fixed_field, op, field_value))

    possible_fields = [item for item in FIELD_OPERATORS_IS_READ_MAP if item != fixed_field]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_IS_READ_MAP.get(field, [])
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
    fixed_field = "is_important"
    email = choice(EMAILS_DATA_MODIFIED)
    op = ComparisonOperator(random.choice(FIELD_OPERATORS_IMPORTANT_MAP[fixed_field]))
    field_value = not email[fixed_field]
    constraints_list.append(create_constraint_dict(fixed_field, op, field_value))

    possible_fields = [item for item in FIELD_OPERATORS_IMPORTANT_MAP if item != fixed_field]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_IMPORTANT_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_is_spam_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    fixed_field = "is_spam"
    field_value = True

    email = next((e for e in EMAILS_DATA_MODIFIED if e.get(fixed_field) is True), None)
    if not email:
        email = choice(EMAILS_DATA_MODIFIED)
    op = ComparisonOperator(choice(FIELD_OPERATORS_IS_SPAM_MAP[fixed_field]))
    constraints_list.append(create_constraint_dict(fixed_field, op, field_value))

    possible_fields = [item for item in FIELD_OPERATORS_IS_SPAM_MAP if item != fixed_field]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_IS_SPAM_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = email.get(field)
        value = _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def _generate_search_constraint_value(operator, value):
    if operator == ComparisonOperator.EQUALS:
        return value
    elif operator == ComparisonOperator.NOT_EQUALS:
        return choice([word for word in ALL_EMAIL_WORDS if value != word])
    elif operator == ComparisonOperator.CONTAINS:
        return choice([word for word in ALL_EMAIL_WORDS if value in word])
    elif operator == ComparisonOperator.NOT_CONTAINS:
        return choice([word for word in ALL_EMAIL_WORDS if value not in word])


def generate_search_email_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    for field, operators in FIELD_OPERATORS_SEARCH_MAP.items():
        operator = ComparisonOperator(random.choice(operators))
        field_value = choice(ALL_EMAIL_WORDS)

        value = _generate_search_constraint_value(operator, field_value)
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


LIST_OF_EMAILS = [
    "alice.smith@example.com",
    "john.doe@gmail.com",
    "maria.jones@yahoo.com",
    "kevin_lee@outlook.com",
    "nina.patel@company.org",
    "daniel_choi@webmail.net",
    "emma.watson@school.edu",
    "lucas.gray@workplace.io",
    "olivia.brown@startup.ai",
    "ethan.miller@techcorp.com",
    "sophia.morris@researchlab.org",
    "liam.johnson@business.co",
    "ava.wilson@healthcare.org",
    "noah.thomas@banksecure.com",
    "isabella.clark@freelancer.dev",
    "elijah.walker@codebase.io",
    "mia.hall@socialapp.me",
    "james.young@nonprofit.org",
    "amelia.king@greenenergy.com",
    "logan.scott@designhub.net",
    "harper.adams@newsdaily.com",
    "sebastian.moore@fintech.ai",
    "zoe.baker@civicgroup.org",
    "jackson.evans@customsoft.dev",
    "charlotte.cox@musicstream.fm",
]


def generate_save_as_draft_send_email_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    email = choice(EMAILS_DATA_MODIFIED)
    selected_fields = ["to"]  # Fixed 'to'
    possible_fields = ["subject", "body"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields.extend(random.sample(possible_fields, num_constraints))

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SEND_OR_DRAFT_EMAIL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = email.get(field)
        value = random.choice(LIST_OF_EMAILS) if field == "to" else _generate_constraint_value(operator, field_value, field, EMAILS_DATA_MODIFIED)
        constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def _get_labels_and_colors(email_data: list[dict[str, Any]]) -> tuple:
    labels = set()
    colors = set()
    for email in email_data:
        if email.get("labels"):
            labels.update([lbl["name"] for lbl in email["labels"] if lbl.get("name")])
            colors.update([lbl["color"] for lbl in email["labels"] if lbl.get("color")])
    return list(labels), list(colors)


def generate_create_label_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    labels, colors = _get_labels_and_colors(EMAILS_DATA_MODIFIED)
    labels_and_colors = [{"label_name": label, "label_color": color} for label, color in zip(labels, colors, strict=False)]
    possible_fields = ["label_name"]
    for field in possible_fields:
        allowed_ops = FIELD_OPERATORS_CREATE_LABEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = choice(labels_and_colors).get(field)
        value = _generate_constraint_value(operator, field_value, field, labels_and_colors)
        constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list


def generate_add_label_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    full_dataset = []
    for email in EMAILS_DATA_MODIFIED:
        subject = email.get("subject")
        labels = email.get("labels", [])
        body = email.get("body")
        if not labels:
            continue

        for label in labels:
            label_name = label.get("name")
            if label_name:
                full_dataset.append({"action": "added", "label_name": label_name, "body": body, "subject": subject})

    if not full_dataset:
        return []

    selected_item = choice(full_dataset)
    while not selected_item.get("body") and not selected_item.get("subject") and not selected_item.get("label_name"):
        selected_item = choice(full_dataset)

    # Step 5: Always include action + label_name
    base_fields = ["label_name"]

    # Conditionally include subject or body or both
    optional_fields = []
    if selected_item.get("subject"):
        optional_fields.append("subject")
    if selected_item.get("body"):
        optional_fields.append("body")

    if optional_fields:
        num_constraints = random.randint(1, len(optional_fields))
        optional_fields = random.sample(optional_fields, num_constraints)
    else:
        optional_fields = []

    final_fields = base_fields + optional_fields
    for field in final_fields:
        allowed_ops = FIELD_OPERATORS_ADD_LABEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(choice(allowed_ops))
        field_value = selected_item.get(field)

        value = _generate_constraint_value(operator, field_value, field, full_dataset)
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


def generate_theme_changed_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    themes = ["light", "dark", "system"]
    field = "theme"
    allowed_ops = [EQUALS, NOT_EQUALS]

    if not allowed_ops:
        return constraints_list

    operator = ComparisonOperator(random.choice(allowed_ops))

    field_value = choice(themes)
    value = field_value if operator == ComparisonOperator.EQUALS else random.choice([theme for theme in themes if theme != field_value])

    constraints_list.append(create_constraint_dict(field, operator, value))

    return constraints_list
