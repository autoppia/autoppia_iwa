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
    FIELD_OPERATORS_MAP_NEW_LOG,
    MATTERS_DATA,
    NEW_LOGS_DATA,
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
        value = _generate_constraint_value(operator, field_value, field, dataset=MATTERS_DATA)

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

    sample_client = random.choice(CLIENT_DATA)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = sample_client.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=CLIENT_DATA)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_search_client_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    field_map = {"name": "query"}
    field = "name"
    allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
    op_str = random.choice(allowed_ops)
    operator = ComparisonOperator(op_str)

    sample_client = random.choice(CLIENT_DATA)
    field_value = sample_client.get(field)

    value = _generate_constraint_value(operator, field_value, field, dataset=CLIENT_DATA)
    if value is not None:
        constraint = create_constraint_dict(field_map[field], operator, value)
        constraints_list.append(constraint)

    return constraints_list


def _generate_value_for_document_field(field: str, field_value: str, operator: ComparisonOperator, all_documents: list[dict[str, Any]]) -> Any:
    values = [d[field] for d in all_documents if field in d]
    values = list(set(values))

    if not values:
        return None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [d[field] for d in all_documents if d.get(field) != field_value]
        return random.choice(valid) if valid else random.choice(values)

    elif (
        operator
        in [
            ComparisonOperator.GREATER_THAN,
            ComparisonOperator.LESS_THAN,
            ComparisonOperator.GREATER_EQUAL,
            ComparisonOperator.LESS_EQUAL,
        ]
        and field == "size"
    ):
        # Extract all sizes in KB and track units
        size_entries = []
        for s in values:
            try:
                if "KB" in s:
                    size_entries.append((float(s.replace("KB", "").strip()), "KB"))
                elif "MB" in s:
                    mb = float(s.replace("MB", "").strip())
                    size_entries.append((mb * 1024, "MB"))
            except Exception:
                continue

        if not size_entries:
            return None

        # Pick base
        base_kb, unit = random.choice(size_entries)
        delta = random.randint(1, 20)

        if operator == ComparisonOperator.GREATER_THAN:
            new_kb = base_kb + delta
        elif operator == ComparisonOperator.GREATER_EQUAL:
            new_kb = base_kb + random.randint(0, delta)
        elif operator == ComparisonOperator.LESS_THAN:
            new_kb = max(min(kb for kb, _ in size_entries), base_kb - delta)
        elif operator == ComparisonOperator.LESS_EQUAL:
            new_kb = max(min(kb for kb, _ in size_entries), base_kb - random.randint(0, delta))
        else:
            new_kb = base_kb

        # Format consistently with original unit
        if unit == "MB":
            return f"{round(new_kb / 1024, 2)} MB"
        else:
            return f"{int(new_kb)} KB"

    return random.choice(values)


def generate_document_deleted_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "size", "version", "status"]  # , "updated"]
    document_data = random.choice(DOCUMENT_DATA)

    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_DOCUMENT.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        field_value = document_data.get(field)

        value = _generate_value_for_document_field(field, field_value, operator, DOCUMENT_DATA) if field == "size" else _generate_constraint_value(operator, field_value, field, dataset=DOCUMENT_DATA)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_new_calendar_event_constraints() -> list[dict[str, Any]]:
    fields = ["label", "time", "date", "event_type"]
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

    constraints = []
    for field in fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_CALENDAR[field])
        operator = ComparisonOperator(op_str)

        if field == "date":
            # Ensure generated date is within a feasible range
            base_day = random.randint(1, 28)
            if operator == ComparisonOperator.LESS_THAN:
                value = f"2025-05-{base_day:02d}"
                # Prevent dates too far in the past or before system start
                if base_day < 2:
                    value = "2025-05-02"
            elif operator == ComparisonOperator.GREATER_THAN:
                value = f"2025-05-{base_day:02d}"
                if base_day > 27:
                    value = "2025-05-27"
            else:
                value = f"2025-05-{base_day:02d}"

        elif field == "time":
            hour = random.randint(8, 16)
            minute = random.choice([0, 30])
            suffix = "am" if hour < 12 else "pm"
            display_hour = hour if hour <= 12 else hour - 12
            value = f"{display_hour}:{minute:02d}{suffix}"
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
    fields = ["matter", "hours", "description"]
    constraints: list[dict[str, Any]] = []

    log_data = random.choice(NEW_LOGS_DATA)

    for field in fields:
        allowed_ops = FIELD_OPERATORS_MAP_NEW_LOG.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        field_value = log_data.get(field)

        value = _generate_constraint_value(operator, field_value, field, dataset=NEW_LOGS_DATA)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints.append(constraint)

    return constraints


def generate_delete_log_constraints() -> list[dict[str, Any]]:
    fields = ["matter", "hours", "client", "status"]
    constraints: list[dict[str, Any]] = []

    log_data = random.choice(DEMO_LOGS)

    for field in fields:
        allowed_ops = FIELD_OPERATORS_MAP_LOG.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)
        field_value = log_data.get(field)

        value = _generate_constraint_value(operator, field_value, field, dataset=DEMO_LOGS)

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
