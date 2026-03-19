import calendar
import contextlib
import random
from datetime import date, datetime, timedelta
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict

# Constants
ERROR_NO_DATASET_MSG = "[ERROR] No dataset provided"


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    visible_fields: list[str],
    *,
    verify_field: str | None = None,
    question_fields_override: list[str] | None = None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure.

    When verify_field is provided, it is used as the verify field (fixed). Otherwise, verify field is chosen randomly
    from the available visible fields.

    When question_fields_override is provided and non-empty, those fields (that exist and have values) are used
    as the fixed question fields. The verify field is verify_field if it is provided and lies among the remaining
    visible fields; otherwise it is chosen randomly from the remaining available fields.
    If, apart from the verify field and the fixed question fields, there are 2 or more visible fields left,
    a random subset of those is added to the question fields.
    """
    available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        return None

    question_fields: list[str]
    chosen_verify_field: str

    if question_fields_override:
        question_fields = [f for f in question_fields_override if f in available_fields and selected_item.get(f) is not None]
        if question_fields:
            remaining = [f for f in available_fields if f not in question_fields]
            if not remaining:
                return None
            chosen_verify_field = verify_field if verify_field is not None and verify_field in remaining else random.choice(remaining)
            remaining_for_extra = [f for f in available_fields if f != chosen_verify_field and f not in question_fields]
            if len(remaining_for_extra) >= 2:
                num_extra = random.randint(1, len(remaining_for_extra))
                question_fields = question_fields + random.sample(remaining_for_extra, num_extra)
        else:
            question_fields = []
            chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
    else:
        chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
        question_fields = []

    if chosen_verify_field not in available_fields:
        return None
    verify_value = selected_item.get(chosen_verify_field)
    if verify_value is None:
        return None

    if question_fields:
        question_candidates = question_fields
    else:
        question_candidates = [f for f in available_fields if f != chosen_verify_field]
        if not question_candidates:
            return None
        num_question_fields = 1 if len(question_candidates) == 1 else 2
        question_candidates = random.sample(question_candidates, num_question_fields)

    question_fields_and_values: dict[str, Any] = {}
    for qf in question_candidates:
        val = selected_item.get(qf)
        if val is not None:
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        return None

    constraints = [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


from .data import (
    ALLOWED_EVENT_COLORS,
    FIELD_OPERATORS_MAP_BILLING_SEARCH,
    FIELD_OPERATORS_MAP_CALENDAR,
    FIELD_OPERATORS_MAP_CHANGE_USER_NAME,
    FIELD_OPERATORS_MAP_CLIENT,
    FIELD_OPERATORS_MAP_CLIENT_FILTERS,
    FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER,
    FIELD_OPERATORS_MAP_DOCUMENT,
    FIELD_OPERATORS_MAP_DOCUMENT_RENAME,
    FIELD_OPERATORS_MAP_LOG,
    FIELD_OPERATORS_MAP_MATTER,
    FIELD_OPERATORS_MAP_NEW_LOG,
    VISIBLE_FIELDS_CLIENT_DETAIL,
    VISIBLE_FIELDS_DOCUMENT,
    VISIBLE_FIELDS_LOG,
    VISIBLE_FIELDS_MATTER_DETAIL,
    VISIBLE_FIELDS_SEARCH_CLIENT,
    VISIBLE_FIELDS_SEARCH_MATTER,
)


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


async def _ensure_crm_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Extract entity data from the pre-loaded dataset, or fetch from server if not available.

    Dynamically fetches only the requested entity_type using the provided method and filter_key.
    Returns a dictionary with entity_type as the key.
    """
    _ = dataset  # Unused parameter kept for backward compatibility
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    from .data_utils import fetch_data

    seed = get_seed_from_url(task_url)
    fetched_dataset = await fetch_data(
        entity_type=entity_type,
        method=method,
        filter_key=filter_key,
        seed_value=seed,
    )

    # Return as dictionary with entity_type as key
    return {entity_type: fetched_dataset}


async def _get_crm_entity_list(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    entity_type: str,
    *,
    method: str | None = None,
    filter_key: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch CRM dataset for entity_type and return the list. Reduces repeated ensure+get pattern."""
    data_dict = await _ensure_crm_dataset(task_url, dataset, entity_type=entity_type, method=method, filter_key=filter_key)
    return data_dict.get(entity_type, [])


def _collect_field_values_from_dataset(dataset: list[dict[str, Any]], field: str) -> list[Any]:
    """Collect all unique non-None values for field from dataset. Used by IN_LIST and NOT_IN_LIST."""
    values = [v.get(field) for v in dataset if field in v and v.get(field) is not None]
    return list(set(values))


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
        all_values = _collect_field_values_from_dataset(dataset, field)
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = _collect_field_values_from_dataset(dataset, field)
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


def _generate_constraints_from_sample(
    dataset: list[dict[str, Any]],
    possible_fields: list[str],
    field_operators_map: dict[str, list],
    num_constraints: int | None = None,
) -> list[dict[str, Any]]:
    """Build constraints by picking a random sample and random fields, then generating one constraint per field. Reduces duplication across view/generate functions."""
    if not dataset:
        return []
    if num_constraints is None:
        num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, min(num_constraints, len(possible_fields)))
    sample = random.choice(dataset)
    constraints_list: list[dict[str, Any]] = []
    for field in selected_fields:
        allowed_ops = field_operators_map.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = sample.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


async def generate_view_matter_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    data = await _get_crm_entity_list(task_url, dataset, "matters", method="distribute", filter_key="status")
    if test_types == "data_extraction_only":
        if not data:
            return []
        matter = random.choice(data)
        result = _build_data_extraction_result(matter, VISIBLE_FIELDS_MATTER_DETAIL, question_fields_override=["name"])
        return result if result is not None else []
    constraints_list: list[dict[str, Any]] = []
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return constraints_list
    return _generate_constraints_from_sample(data, ["name", "client", "status", "updated"], FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER, num_constraints=random.randint(2, 4))


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


async def generate_view_client_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    data = await _get_crm_entity_list(task_url, dataset, "clients", method="distribute", filter_key="status")
    if test_types == "data_extraction_only":
        if not data:
            return []
        client = random.choice(data)
        result = _build_data_extraction_result(client, VISIBLE_FIELDS_CLIENT_DETAIL, question_fields_override=["name"])
        return result if result is not None else []
    constraints_list: list[dict[str, Any]] = []
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return constraints_list
    return _generate_constraints_from_sample(data, ["name", "email", "status", "matters"], FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER)


async def generate_search_client_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        client_data = await _get_crm_entity_list(task_url, dataset, "clients", method="distribute", filter_key="status")
        if not client_data:
            return []
        client = random.choice(client_data)
        result = _build_data_extraction_result(client, VISIBLE_FIELDS_SEARCH_CLIENT, question_fields_override=["name"])
        return result if result is not None else []
    constraints_list: list[dict[str, Any]] = []
    client_data = await _get_crm_entity_list(task_url, dataset, "clients", method="distribute", filter_key="status")
    if not client_data:
        print(ERROR_NO_DATASET_MSG)
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


async def generate_search_matter_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    matter_data = await _get_crm_entity_list(task_url, dataset, "matters", method="distribute", filter_key="status")
    if test_types == "data_extraction_only":
        if not matter_data:
            return []
        matter = random.choice(matter_data)
        result = _build_data_extraction_result(matter, VISIBLE_FIELDS_SEARCH_MATTER, question_fields_override=["name"])
        return result if result is not None else []
    constraints_list: list[dict[str, Any]] = []
    if not matter_data:
        print(ERROR_NO_DATASET_MSG)
        return constraints_list

    field = "name"
    field_map = {"name": "query"}
    allowed_ops = FIELD_OPERATORS_MAP_MATTER.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))

    sample_matter = random.choice(matter_data)
    field_value = sample_matter.get(field)
    value = _generate_constraint_value(operator, field_value, field, dataset=matter_data)

    if value is not None:
        constraints_list.append(create_constraint_dict(field_map[field], operator, value))

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


async def generate_document_deleted_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        data = await _get_crm_entity_list(task_url, dataset, "files", method="", filter_key="")
        if not data:
            return []
        doc = random.choice(data)
        result = _build_data_extraction_result(doc, VISIBLE_FIELDS_DOCUMENT, question_fields_override=["name"])
        return result if result is not None else []
    constraints_list: list[dict[str, Any]] = []
    data = await _get_crm_entity_list(task_url, dataset, "files", method="", filter_key="")
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return constraints_list
    possible_fields = ["name", "size", "version", "status"]
    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    document_data = random.choice(data)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MAP_DOCUMENT.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = document_data.get(field)
        value = _generate_value_for_document_field(field, field_value, operator, data) if field == "size" else _generate_constraint_value(operator, field_value, field, dataset=data)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


# Document rename: allowed new names for constraint generation
NEW_DOCUMENT_NAMES = [
    "Report-102.pdf",
    "Invoice-511.docx",
    "Statement-743.xlsx",
    "Summary-928.pdf",
    "Agreement-337.docx",
    "Form-684.xlsx",
    "Proposal-219.pdf",
    "Record-570.docx",
    "Analysis-803.xlsx",
    "Notes-445.pdf",
    "Plan-122.docx",
    "Schedule-699.xlsx",
    "Brief-911.pdf",
    "Memo-318.docx",
    "Budget-472.xlsx",
    "Guide-856.pdf",
    "Outline-394.docx",
    "Registry-640.xlsx",
]


async def generate_document_renamed_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        docs = await _get_crm_entity_list(task_url, dataset, "files")
        if not docs:
            return []
        doc = random.choice(docs)
        result = _build_data_extraction_result(doc, VISIBLE_FIELDS_DOCUMENT, question_fields_override=["name"])
        return result if result is not None else []
    constraints: list[dict[str, Any]] = []
    docs = await _get_crm_entity_list(task_url, dataset, "files")
    new_names_as_dataset = [{"new_name": name} for name in NEW_DOCUMENT_NAMES]

    if docs:
        doc = random.choice(docs)
        for field in ["new_name", "previous_name"]:
            allowed_ops = FIELD_OPERATORS_MAP_DOCUMENT_RENAME.get(field, [])
            if not allowed_ops:
                continue
            operator = ComparisonOperator(random.choice(allowed_ops))
            if field == "new_name":
                field_value = random.choice(NEW_DOCUMENT_NAMES)
                value = _generate_constraint_value(operator, field_value, field, dataset=new_names_as_dataset)
                if value is not None:
                    constraints.append(create_constraint_dict(field, operator, value))
            elif field == "previous_name":
                value = _generate_constraint_value(operator, doc.get("name", "Document"), field, docs)
                if value is not None:
                    constraints.append(create_constraint_dict(field, operator, value))
    return constraints


async def generate_billing_search_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    logs = await _get_crm_entity_list(task_url, dataset, "logs")
    if test_types == "data_extraction_only":
        if not logs:
            return []
        log = random.choice(logs)
        h = log.get("hours")
        if h is not None:
            if isinstance(h, str) and h.endswith("h"):
                log["hours"] = h
            else:
                log["hours"] = f"{h}h"
        result = _build_data_extraction_result(log, VISIBLE_FIELDS_LOG, question_fields_override=["matter"])
        return result if result is not None else []

    constraints: list[dict[str, Any]] = []
    sample = random.choice(logs) if logs else {"matter": "Review", "description": "Review"}
    fields = ["query", "date_filter"]
    for field in fields:
        allowed_ops = FIELD_OPERATORS_MAP_BILLING_SEARCH.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        value = sample.get("matter") if field == "query" else random.choice(["Today", "This week", "Previous 2 weeks", "This month", "All", "Specific date"])
        if value == "Specific date":
            operator = ComparisonOperator(random.choice(FIELD_OPERATORS_MAP_BILLING_SEARCH.get("custom_date")))
            today = datetime.today()

            random_days = random.randint(0, 30)
            random_date = today - timedelta(days=random_days)

            value = random_date.strftime("%Y-%m-%d")  # format as 'YYYY-MM-DD'
        constraints.append(create_constraint_dict(field, operator, value))
    return constraints


async def generate_add_client_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    clients = await _get_crm_entity_list(task_url, dataset, "clients", method="distribute", filter_key="status")
    if not clients:
        clients = [{"name": "New Client", "email": "new@example.com", "matters": 1, "status": "Active", "last": "Today"}]
    if test_types == "data_extraction_only":
        client = random.choice(clients)
        result = _build_data_extraction_result(client, VISIBLE_FIELDS_CLIENT_DETAIL, question_fields_override=["name"])
        return result if result is not None else []
    sample = random.choice(clients)
    constraints: list[dict[str, Any]] = []
    for field in ["name", "email", "matters", "status", "last"]:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        constraints.append(create_constraint_dict(field, op, sample.get(field)))
    return constraints


async def generate_delete_client_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    return await generate_add_client_constraints(task_url, dataset, test_types)


async def generate_filter_clients_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    clients = await _get_crm_entity_list(task_url, dataset, "clients", method="distribute", filter_key="status")
    if test_types == "data_extraction_only":
        if not clients:
            return []
        client = random.choice(clients)
        result = _build_data_extraction_result(client, VISIBLE_FIELDS_CLIENT_DETAIL, question_fields_override=["name"])
        return result if result is not None else []
    constraints: list[dict[str, Any]] = []
    sample = random.choice(clients) if clients else {"status": "Active", "matters": 2}
    for field in ["status", "matters"]:
        allowed_ops = FIELD_OPERATORS_MAP_CLIENT_FILTERS.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        value = sample.get("status") if field == "status" else random.choice(["All", "1-2", "3-4", "5+"])
        constraints.append(create_constraint_dict(field, op, value))
    return constraints


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


def generate_new_calendar_event_constraints() -> list[dict[str, Any]]:
    fields = ["label", "time", "date", "event_type"]
    constraints = []
    for field in fields:
        op_str = random.choice(FIELD_OPERATORS_MAP_CALENDAR[field])
        operator = ComparisonOperator(op_str)

        if field == "date":
            today = date.today()
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
    data = await _get_crm_entity_list(task_url, dataset, "logs")
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return []
    return _generate_constraints_from_sample(data, ["matter", "hours", "description"], FIELD_OPERATORS_MAP_NEW_LOG)


async def generate_log_edited_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    data = await _get_crm_entity_list(task_url, dataset, "logs", method="", filter_key="")
    if test_types == "data_extraction_only":
        if not data:
            return []
        log = random.choice(data)
        h = log.get("hours")
        if h is not None:
            if isinstance(h, str) and h.endswith("h"):
                log["hours"] = h
            else:
                log["hours"] = f"{h}h"
        result = _build_data_extraction_result(log, VISIBLE_FIELDS_LOG, question_fields_override=["matter"])
        return result if result is not None else []
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return []
    return _generate_constraints_from_sample(data, ["matter", "hours", "description", "client", "status"], FIELD_OPERATORS_MAP_LOG)


async def generate_delete_log_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    data = await _get_crm_entity_list(task_url, dataset, "logs", method="", filter_key="")
    if test_types == "data_extraction_only":
        if not data:
            return []
        log = random.choice(data)
        h = log.get("hours")
        if h is not None:
            if isinstance(h, str) and h.endswith("h"):
                log["hours"] = h
            else:
                log["hours"] = f"{h}h"
        result = _build_data_extraction_result(log, VISIBLE_FIELDS_LOG, question_fields_override=["matter"])
        return result if result is not None else []
    if not data:
        print(ERROR_NO_DATASET_MSG)
        return []
    return _generate_constraints_from_sample(data, ["matter", "hours", "client", "status"], FIELD_OPERATORS_MAP_LOG)


async def generate_filter_matter_status_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]]:
    matter_data = await _get_crm_entity_list(task_url, dataset, "matters", method="distribute", filter_key="status")
    if test_types == "data_extraction_only":
        if not matter_data:
            return []
        matter = random.choice(matter_data)
        result = _build_data_extraction_result(matter, VISIBLE_FIELDS_MATTER_DETAIL, question_fields_override=["name"], verify_field="status")
        return result if result is not None else []
    constraints: list[dict[str, Any]] = []
    if not matter_data:
        print(ERROR_NO_DATASET_MSG)
        return constraints

    statuses = [m.get("status") for m in matter_data if m.get("status")]
    if not statuses:
        return constraints

    field = "status"
    allowed_ops = FIELD_OPERATORS_MAP_MATTER.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))
    sample_status = random.choice(statuses)
    value = _generate_constraint_value(operator, sample_status, field, dataset=matter_data)
    if value is not None:
        constraints.append(create_constraint_dict(field, operator, value))

    return constraints


def generate_sort_matter_constraints() -> list[dict[str, Any]]:
    directions = ["asc", "desc"]
    operator = ComparisonOperator.EQUALS
    direction = random.choice(directions)
    return [create_constraint_dict("direction", operator, direction)]


async def generate_update_matter_constraints(
    task_url: str | None = None,
    dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        matter_data = await _get_crm_entity_list(task_url, dataset, "matters", method="distribute", filter_key="status")
        if not matter_data:
            return []
        matter = random.choice(matter_data)
        result = _build_data_extraction_result(matter, VISIBLE_FIELDS_MATTER_DETAIL, question_fields_override=["name"])
        return result if result is not None else []
    matter_data = await _get_crm_entity_list(task_url, dataset, "matters", method="distribute", filter_key="status")
    if not matter_data:
        print(ERROR_NO_DATASET_MSG)
        return []
    return _generate_constraints_from_sample(matter_data, ["name", "client", "status", "updated"], FIELD_OPERATORS_MAP_MATTER)


async def generate_view_pending_events_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    events_data = await _get_crm_entity_list(task_url, dataset, "events", method="", filter_key="")
    if not events_data:
        print(ERROR_NO_DATASET_MSG)
        return constraints

    sorted_events = sorted(events_data, key=lambda e: e.get("date", ""))
    earliest_date = sorted_events[0].get("date", "") if sorted_events else ""

    if earliest_date:
        earliest_operator = random.choice([ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS])
        constraints.append(create_constraint_dict("earliest", earliest_operator, earliest_date))

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
