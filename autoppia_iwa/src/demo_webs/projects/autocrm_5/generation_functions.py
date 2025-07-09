import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import (
    ALLOWED_EVENT_COLORS,
    CLIENT_DATA,
    DEMO_LOGS,
    DOCUMENT_DATA,
    FIELD_OPERATORS_MAP_CALENDAR,
    FIELD_OPERATORS_MAP_CHANGE_USER_NAME,
    FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER,
    FIELD_OPERATORS_MAP_DOCUMENT,
    FIELD_OPERATORS_MAP_LOG,
    FIELD_OPERATORS_MAP_MATTER,
    MATTERS_DATA,
)


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


def _generate_constraint_value(operator, field_value, field):
    value = None
    if operator == ComparisonOperator.EQUALS:
        value = field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in MATTERS_DATA if v[field] != field_value]
        if valid:
            value = random.choice(valid)

    elif operator == ComparisonOperator.CONTAINS:
        if isinstance(field_value, str) and len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            value = field_value[start:end]
        else:
            value = field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        invalid_substrings = [v[field] for v in MATTERS_DATA if isinstance(v[field], str) and field_value not in v[field]]
        if invalid_substrings:
            value = random.choice(invalid_substrings)

    elif operator == ComparisonOperator.IN_LIST:
        all_values = list({v[field] for v in MATTERS_DATA})
        random.shuffle(all_values)
        value = random.sample(all_values, min(2, len(all_values)))
        if not value or field_value not in value:
            value = [field_value]

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v[field] for v in MATTERS_DATA})
        if field_value in all_values:
            all_values.remove(field_value)
        if all_values:
            value = random.sample(all_values, min(2, len(all_values)))
    return value


def generate_view_matter_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "client", "status", "updated"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    matter_data = random.choice(MATTERS_DATA)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = matter_data.get(field)
        value = _generate_constraint_value(operator, field_value, field)

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
            "Active",
            "Archived",
            "On hold",
        ],
    }

    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(sample_values.keys())

    for field in possible_fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_MATTER[field])
        operator = ComparisonOperator(op_str)
        value = random.choice(sample_values[field])
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_view_client_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    possible_fields = ["name", "email", "status", "matters"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

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


def _generate_value_for_log_field(field: str, operator: ComparisonOperator, all_logs: list[dict[str, Any]] = DEMO_LOGS) -> Any:
    values = [log[field] for log in all_logs if field in log]
    values = list(set(values))
    if not values:
        return None

    if operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        chosen_value = str(random.choice(values))
        words = [w for w in chosen_value.split() if len(w) >= 3]
        return random.choice(words) if words else chosen_value[:3]

    if operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
        numeric_values = [v for v in values if isinstance(v, int | float)]
        if numeric_values:
            base = random.choice(numeric_values)
            offset = random.uniform(0.5, 1.5)
            return round(base + offset, 2) if "greater" in operator.value else round(base - offset, 2)

    return random.choice(values)


def generate_new_calendar_event_constraints() -> list[dict[str, Any]]:
    fields = ["label", "date", "time", "event_type"]
    ALLOWED_EVENT_LABELS = [
        "Client Meeting",
        "Sales Call",
        "Follow-up Call",
        "Lead Qualification",
        "Product Demo",
        "Contract Review",
        "Proposal Sent",
        "Negotiation Meeting",
        "Deal Closed",
        "Customer Onboarding",
        "Account Review",
        "Renewal Discussion",
        "Upsell Opportunity",
        "Cross-sell Discussion",
        "Support Call",
        "Customer Feedback Session",
        "Billing Discussion",
        "Churn Risk Review",
        "QBR Meeting",  # Quarterly Business Review
        "Welcome Call",
        "Lead Assignment",
        "Marketing Campaign Review",
        "Email Outreach Scheduled",
        "Pipeline Review",
        "CRM Data Cleanup",
        "Client Training Session",
        "Technical Walkthrough",
        "Internal Strategy Sync",
        "Team Performance Review",
        "Monthly Sales Review",
        "Weekly Client Check-in",
        "Cold Outreach Call",
        "Warm Lead Follow-up",
        "Trial Expiry Notification",
        "Subscription Renewal",
        "Invoice Review",
        "NDA Signing",
        "Kickoff Call",
        "Client Escalation",
        "Feature Discussion",
        "CSAT Follow-up",  # Customer Satisfaction follow-up
        "Implementation Review",
        "Introductory Meeting",
        "Decision Maker Call",
        "Referral Discussion",
    ]

    selected_fields = random.sample(fields, random.randint(1, len(fields)))
    constraints = []
    for field in selected_fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_CALENDAR[field])
        operator = ComparisonOperator(op_str)
        if field == "date":
            value = f"2025-05-{random.randint(1, 28):02d}"
        elif field == "time":
            hour = random.choice(range(8, 17))
            minute = random.choice([0, 30])
            value = f"{hour}:{minute:02d}{'am' if hour < 12 else 'pm'}"
        elif field == "event_type":
            value = random.choice(ALLOWED_EVENT_COLORS)
        elif field == "label":
            value = random.choice(ALLOWED_EVENT_LABELS)
        else:
            value = "N/A"

        constraint = create_constraint_dict(field, operator, value)
        constraints.append(constraint)
    return constraints


def generate_new_log_added_constraints() -> list[dict[str, Any]]:
    fields = ["matter", "client", "hours", "status"]
    selected_fields = random.sample(fields, random.randint(1, len(fields)))
    constraints = []
    for field in selected_fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_LOG[field])
        operator = ComparisonOperator(op_str)
        value = _generate_value_for_log_field(field, operator)
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints.append(constraint)
    return constraints


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
