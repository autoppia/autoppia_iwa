"""
Shared dataset helpers for autohealth_14.
"""

from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 50,
) -> list[dict]:
    """
    Fetch dataset rows for the given entity type.

    This is the unified function replacing:
    - fetch_health_data()
    - get_data()
    - get_all_data()

    Args:
        entity_type: Type of entity to fetch (appointments, doctors, prescriptions, etc.)
        method: Selection method (select, etc.)
        filter_key: Key to filter on
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of data for the requested entity type
    """
    from .main import FRONTEND_PORT_INDEX, health_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{health_project.id}"

    items = await load_dataset_data(
        backend_url=health_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method=method if method else "select",
        filter_key=filter_key if filter_key else None,
    )
    return items or []


def extract_health_dataset(dataset: Any, entity_type: str) -> list[dict[str, Any]] | None:
    """Return the list for the requested entity from a shared dataset payload."""
    if dataset is None:
        return None
    if isinstance(dataset, list):
        return dataset
    if isinstance(dataset, dict):
        value = dataset.get(entity_type)
        if isinstance(value, list):
            return value
    return None


def transform_appointments_to_modified(appointments: list[dict]) -> list[dict]:
    """Transform appointments from backend format (camelCase) to MODIFIED format (snake_case)."""
    modified = []
    for appt in appointments:
        new_appt = appt.copy()
        if "doctorName" in new_appt:
            new_appt["doctor_name"] = new_appt.pop("doctorName")
        if "specialty" in new_appt:
            new_appt["speciality"] = new_appt.pop("specialty")
        modified.append(new_appt)
    return modified


def transform_doctors_to_modified(doctors: list[dict]) -> list[dict]:
    """Transform doctors from backend format (camelCase) to MODIFIED format (snake_case)."""
    modified = []
    for data in doctors:
        new_data = data.copy()
        if "name" in new_data:
            new_data["doctor_name"] = new_data.pop("name")
        if "specialty" in new_data:
            new_data["speciality"] = new_data.pop("specialty")
        modified.append(new_data)
    return modified


def transform_prescriptions_to_modified(prescriptions: list[dict]) -> list[dict]:
    """Transform prescriptions from backend format (camelCase) to MODIFIED format (snake_case)."""
    modified = []
    for pres in prescriptions:
        new_pres = pres.copy()
        if "medicineName" in new_pres:
            new_pres["medicine_name"] = new_pres.pop("medicineName")
        if "doctorName" in new_pres:
            new_pres["doctor_name"] = new_pres.pop("doctorName")
        if "startDate" in new_pres:
            new_pres["start_date"] = new_pres.pop("startDate")
        if "refillsRemaining" in new_pres:
            new_pres["refills_remaining"] = new_pres.pop("refillsRemaining")
        modified.append(new_pres)
    return modified


def transform_medical_records_to_modified(medical_records: list[dict]) -> list[dict]:
    """Transform medical records from backend format (camelCase) to MODIFIED format (snake_case)."""
    modified = []
    for data in medical_records:
        new_data = data.copy()
        if "title" in new_data:
            new_data["record_title"] = new_data.pop("title")
        if "date" in new_data:
            new_data["record_date"] = new_data.pop("date")
        if "type" in new_data:
            new_data["record_type"] = new_data.pop("type")
        modified.append(new_data)
    return modified
