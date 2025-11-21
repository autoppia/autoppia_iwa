import calendar
import contextlib
import datetime
import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

from ..shared_utils import create_constraint_dict
from .data import (
    ALLOWED_EVENT_COLORS,
    FIELD_OPERATORS_MAP_CALENDAR,
    FIELD_OPERATORS_MAP_CHANGE_USER_NAME,
    FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER,
    FIELD_OPERATORS_MAP_DOCUMENT,
    FIELD_OPERATORS_MAP_LOG,
    FIELD_OPERATORS_MAP_MATTER,
    FIELD_OPERATORS_MAP_NEW_LOG,
)
from .data_utils import fetch_crm_data


def _extract_entity_dataset(dataset: Any, entity_type: str) -> list[dict[str, Any]] | None:
    if dataset is None:
        return None
    if isinstance(dataset, list):
        return dataset
    if isinstance(dataset, dict):
        value = dataset.get(entity_type)
        if isinstance(value, list):
            return value
    return None


async def _get_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 100,
) -> list[dict]:
    return await fetch_crm_data(entity_type, method=method, filter_key=filter_key, seed_value=seed_value, count=count)


async def _ensure_crm_dataset(
    task_url: str | None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> list[dict[str, Any]]:
    """Ensure dataset for CRM entity type is available."""
    existing = _extract_entity_dataset(dataset, entity_type)
    if existing is not None:
        return existing
    v2_seed = await resolve_v2_seed_from_url(task_url)
    return await _get_data(entity_type=entity_type, method=method, filter_key=filter_key, seed_value=v2_seed)


def _to_float_safe(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").strip())
        except Exception:
            return None
    return None


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) != field_value and v.get(field) is not None]
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
        all_values = [v.get(field) for v in dataset if field in v and v.get(field) is not None]
        all_values = list({v for v in all_values})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = [v.get(field) for v in dataset if field in v and v.get(field) is not None]
        all_values = list({v for v in all_values})
        if field_value in all_values:
            with contextlib.suppress(ValueError):
                all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        base = _to_float_safe(field_value)
        if base is None:
            return None
        delta = random.uniform(1, 3)
        if operator == ComparisonOperator.GREATER_THAN:
            return round(base - delta, 2)
        elif operator == ComparisonOperator.LESS_THAN:
            return round(base + delta, 2)
        elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return round(base, 2)

    return None


async def generate_view_matter_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    dataset = await _ensure_crm_dataset(task_url, dataset, entity_type="matters", method="distribute", filter_key="status")
    if not dataset:
        print("[ERROR] No dataset provided")
        return constraints_list
    possible_fields = ["name", "client", "status", "updated"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    matter_data = random.choice(dataset)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))

        field_value = matter_data.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=dataset)

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
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_MAP_MATTER[field]))
        value = random.choice(sample_values[field])
        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


async def generate_view_client_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    client_data = await _ensure_crm_dataset(task_url, dataset, entity_type="clients", method="distribute", filter_key="status")
    if not client_data:
        print("[ERROR] No dataset provided")
        return constraints_list
    possible_fields = ["name", "email", "status", "matters"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    sample_client = random.choice(client_data)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))

        field_value = sample_client.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=client_data)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


async def generate_search_client_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    client_data = await _ensure_crm_dataset(task_url, dataset, entity_type="clients", method="distribute", filter_key="status")
    if not client_data:
        print("[ERROR] No dataset provided")
        return constraints_list
    field_map = {"name": "query"}
    field = "name"
    allowed_ops = FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))

    sample_client = random.choice(client_data)
    field_value = sample_client.get(field)

    value = _generate_constraint_value(operator, field_value, field, dataset=client_data)
    if value is not None:
        constraint = create_constraint_dict(field_map[field], operator, value)
        constraints_list.append(constraint)

    return constraints_list


def _generate_value_for_document_field(field: str, field_value: str, operator: ComparisonOperator, all_documents: list[dict[str, Any]]) -> Any:
    values = [d[field] for d in all_documents if field in d and d.get(field) is not None]
    values = list(set(values))

    if not values:
        return None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [d[field] for d in all_documents if d.get(field) != field_value and d.get(field) is not None]
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
        base_kb: float | None = None
        unit = "KB"
        if isinstance(field_value, int | float):
            base_kb = float(field_value)
            unit = "KB"
        elif isinstance(field_value, str):
            fv = field_value.strip().upper()
            try:
                if fv.endswith("KB"):
                    base_kb = float(fv.replace("KB", "").strip())
                    unit = "KB"
                elif fv.endswith("MB"):
                    base_kb = float(fv.replace("MB", "").strip()) * 1024
                    unit = "MB"
                else:
                    base_kb = float(fv)
                    unit = "KB"
            except Exception:
                base_kb = None

        if base_kb is None:
            return None

        delta = random.randint(1, 20)

        if operator == ComparisonOperator.GREATER_THAN:
            new_kb = base_kb - delta
        elif operator == ComparisonOperator.GREATER_EQUAL:
            new_kb = base_kb - random.randint(0, delta)
        elif operator == ComparisonOperator.LESS_THAN:
            new_kb = base_kb + delta
        elif operator == ComparisonOperator.LESS_EQUAL:
            new_kb = base_kb + random.randint(0, delta)
        else:
            new_kb = base_kb

        # Format consistently with original unit
        if unit == "MB":
            return f"{round(new_kb / 1024, 2)} MB"
        else:
            # Keep KB as integer for readability
            return f"{round(new_kb)} KB"

    return random.choice(values)


async def generate_document_deleted_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["name", "size", "version", "status"]  # , "updated"]
    data = await _ensure_crm_dataset(task_url, dataset, entity_type="files", method="", filter_key="")
    if not data:
        print("[ERROR] No dataset provided")
        return constraints_list
    document_data = random.choice(data)
    # document_data = random.choice(DOCUMENT_DATA)

    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_DOCUMENT.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))

        field_value = document_data.get(field)

        value = _generate_value_for_document_field(field, field_value, operator, data) if field == "size" else _generate_constraint_value(operator, field_value, field, dataset=data)

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
        "QBR Meeting",
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
        "CSAT Follow-up",
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
            today = datetime.date.today()
            # choose previous (-1), current (0) or next (+1) month
            offset = random.choice([-1, 0, 1])
            total_month_index = today.year * 12 + (today.month - 1) + offset
            year = total_month_index // 12
            month = (total_month_index % 12) + 1
            max_day = calendar.monthrange(year, month)[1]
            day = random.randint(1, max_day)
            value = f"{year}-{month:02d}-{day:02d}"

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


async def generate_new_log_added_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    fields = ["matter", "hours", "description"]
    constraints: list[dict[str, Any]] = []
    data = await _ensure_crm_dataset(task_url, dataset, entity_type="logs")
    if not data:
        print("[ERROR] No dataset provided")
        return constraints
    log_data = random.choice(data)

    for field in fields:
        allowed_ops = FIELD_OPERATORS_MAP_NEW_LOG.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = log_data.get(field)

        value = _generate_constraint_value(operator, field_value, field, dataset=data)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints.append(constraint)

    return constraints


async def generate_delete_log_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    fields = ["matter", "hours", "client", "status"]
    constraints: list[dict[str, Any]] = []
    data = await _ensure_crm_dataset(task_url, dataset, entity_type="logs", method="", filter_key="")
    if not data:
        print("[ERROR] No dataset provided")
        return constraints
    log_data = random.choice(data)
    for field in fields:
        allowed_ops = FIELD_OPERATORS_MAP_LOG.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = log_data.get(field)

        value = _generate_constraint_value(operator, field_value, field, dataset=data)

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
