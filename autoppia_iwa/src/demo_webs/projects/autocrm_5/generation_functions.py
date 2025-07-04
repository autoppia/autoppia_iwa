import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_data import FIELD_OPERATORS_MAP_CHANGE_USER_NAME, FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER, FIELD_OPERATORS_MAP_DOCUMENT, FIELD_OPERATORS_MAP_MATTER
from ..shared_utils import create_constraint_dict
from .data import CLIENT_DATA, DOCUMENT_DATA, MATTERS_DATA


def _generate_value_for_matter_field(field: str, operator: ComparisonOperator, all_matters: list[dict[str, Any]] = MATTERS_DATA) -> Any:
    values = [m[field] for m in all_matters if field in m]
    values = list(set(values))

    if not values:
        return None

    if operator in [ComparisonOperator.IN_LIST, ComparisonOperator.NOT_IN_LIST]:
        k_val = min(random.randint(1, 3), len(values))
        return random.sample(values, k=k_val) if k_val > 0 else [random.choice(values)]
    elif operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        chosen_value: str = str(random.choice(values))
        if len(chosen_value) > 2:
            start = random.randint(0, max(0, len(chosen_value) - 2))
            end = random.randint(start + 1, len(chosen_value))
            return chosen_value[start:end]
        return chosen_value
    else:
        return random.choice(values)


def _generate_value_for_client_field(field: str, operator: ComparisonOperator, all_clients: list[dict[str, Any]] = CLIENT_DATA) -> Any:
    values = [c[field] for c in all_clients if field in c]
    values = list(set(values))  # Get unique values

    if not values:
        return None

    if operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        chosen_value: str = str(random.choice(values))
        if len(chosen_value) > 5:
            start = random.randint(0, max(0, len(chosen_value) - 2))
            end = random.randint(start + 1, len(chosen_value))
            return chosen_value[start:end]
        return chosen_value
    elif operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN]:
        if values and all(isinstance(v, int | float) for v in values):
            base_num = random.choice(values)
            delta = random.randint(1, 3)
            if operator == ComparisonOperator.GREATER_THAN:
                return base_num - delta
            else:  # LESS_THAN
                return base_num + delta
        return random.choice(values)  # Fallback
    else:  # EQUALS, NOT_EQUALS
        return random.choice(values)


def generate_view_matter_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "client", "status", "updated"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        value = _generate_value_for_matter_field(field, operator)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_add_matter_constraints() -> list[dict[str, Any]]:
    sample_values = {
        "name": [
            "New Matter",
            "Dummy Case",
            "Case Alpha",
            "Litigation 2025",
            "Corporate Merge",
            "Patent Filing",
            "HR Dispute",
            "Compliance Review",
            "Acquisition Deal",
            "Trademark Infringement",
            "Tax Investigation",
            "Employment Agreement",
            "Breach of Contract",
            "Insurance Claim",
        ],
        "client": [
            "Emma",
            "Anonymous",
            "John Doe",
            "XYZ Corp",
            "Techtron Ltd",
            "LegalEase Inc.",
            "Jane Smith",
            "Acme Co.",
            "Delta Partners",
            "Global Solutions",
            "Confidential Client",
            "Robert Miles",
        ],
        "status": [
            "active",
            "archived",
            "on hold",
            "pending",
            "closed",
            "under review",
            "in progress",
            "awaiting approval",
            "reopened",
            "draft",
            "cancelled",
        ],
    }

    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(sample_values.keys())

    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_MATTER[field])
        operator = ComparisonOperator(op_str)
        value = random.choice(sample_values[field])
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_archive_matter_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "client", "status", "updated"]

    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_MATTER.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        value = _generate_value_for_matter_field(field, operator)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_view_client_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    possible_fields = ["name", "email", "status", "matters"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample([possible_fields], num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        value = _generate_value_for_client_field(field, operator)
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


def generate_search_client_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    field = "name"
    allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
    op_str = random.choice(allowed_ops)
    operator = ComparisonOperator(op_str)

    value = _generate_value_for_client_field(field, operator)
    constraint = create_constraint_dict(field, operator, value)
    constraints_list.append(constraint)

    return constraints_list


def _generate_value_for_document_field(field: str, operator: ComparisonOperator, all_documents: list[dict[str, Any]]) -> Any:
    values = [d[field] for d in all_documents if field in d]
    values = list(set(values))  # Get unique values

    if not values:
        return None

    if operator in [ComparisonOperator.IN_LIST, ComparisonOperator.NOT_IN_LIST]:
        k_val = min(random.randint(1, 2), len(values))
        return random.sample(values, k=k_val) if k_val > 0 else [random.choice(values)]
    elif operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        chosen_value: str = str(random.choice(values))
        if len(chosen_value) > 2:
            start = random.randint(0, max(0, len(chosen_value) - 2))
            end = random.randint(start + 1, len(chosen_value))
            return chosen_value[start:end]
        return chosen_value
    elif operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN]:
        if field == "size":
            existing_sizes_kb = []
            for s in values:
                if isinstance(s, str) and "KB" in s:
                    existing_sizes_kb.append(float(s.replace(" KB", "")))
                elif isinstance(s, str) and "MB" in s:
                    existing_sizes_kb.append(float(s.replace(" MB", "")) * 1024)

            if existing_sizes_kb:
                base_size_kb = random.choice(existing_sizes_kb)
                delta_kb = random.randint(10, 200)
                generated_size_kb = base_size_kb + (delta_kb if operator == ComparisonOperator.GREATER_THAN else -delta_kb)
                return f"{max(1, int(generated_size_kb))} KB"
            return "100 KB"  # Fallback
        # For other numeric-like fields if they appear, handle them generally
        if values and all(isinstance(v, int | float) for v in values):
            base_num = random.choice(values)
            delta = random.randint(1, 3)
            return base_num + delta if operator == ComparisonOperator.GREATER_THAN else base_num - delta
        return random.choice(values)  # Fallback for non-numeric or complex types
    else:  # EQUALS, NOT_EQUALS
        return random.choice(values)


def generate_document_deleted_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "size", "version", "status", "updated"]
    if not possible_fields:
        return constraints_list

    num_constraints = random.randint(1, min(2, len(possible_fields)))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_DOCUMENT.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        value = _generate_value_for_document_field(field, operator, DOCUMENT_DATA)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


SAMPLE_USER_NAMES: list[str] = [
    "John Doe",
    "Jane Smith",
    "Alice Wonderland",
    "Bob Builder",
    "Chris Evans",
    "David Miller",
    "Emma Watson",
    "Frank White",
    "Grace Hopper",
    "Henry Ford",
    "Ivy Green",
    "Jack Black",
    "Jennifer Doe",
    "Muhammad Ali",
    "Aisha Khan",
    "Sana Ahmed",
    "Omar Farooq",
    "Fatima Zahra",
]


def generate_change_user_name_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    if not SAMPLE_USER_NAMES:
        return constraints_list

    field = "name"
    op_str = random.choice(FIELD_OPERATORS_MAP_CHANGE_USER_NAME[field])
    operator = ComparisonOperator(op_str)

    if operator in [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]:
        value = random.choice(SAMPLE_USER_NAMES)
    elif operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        base_name = random.choice(SAMPLE_USER_NAMES)
        value_parts = base_name.split()
        value = random.choice(value_parts) if value_parts else base_name[0]
    else:
        value = random.choice(SAMPLE_USER_NAMES)

    constraint = create_constraint_dict(field, operator, value)
    constraints_list.append(constraint)

    return constraints_list
