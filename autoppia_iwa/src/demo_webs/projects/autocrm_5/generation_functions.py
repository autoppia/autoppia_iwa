import random
from typing import Any

from ..criterion_helper import ComparisonOperator
from ..shared_data import FIELD_OPERATORS_MAP_MATTER
from ..shared_utils import create_constraint_dict
from .data import MATTERS_DATA


def generate_view_matter_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "client", "status", "updated"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    matter = random.choice(MATTERS_DATA)

    for field in selected_fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_MATTER[field])
        operator = ComparisonOperator(op_str)
        value = matter.get(field)
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
