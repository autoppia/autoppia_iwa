"""
Shared dataset helpers for autohealth_14.
"""

from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.data_provider import load_dataset_data


def _load_initial_data_fallback(entity_type: str, count: int = 50) -> list[dict]:
    """Fallback dataset hook used when backend dataset service returns no rows."""
    _ = entity_type
    _ = count
    return []


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
    if not items:
        logger.error("Dataset fetch failed for {}.", entity_type)
        return _load_initial_data_fallback(entity_type, count)
    return items


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
        if "consultationFee" in new_data:
            new_data["consultation_fee"] = new_data.pop("consultationFee")
        fee = new_data.get("consultation_fee")
        if fee is not None:
            if fee < 150:
                new_data["pricing"] = "under150"
            elif fee <= 250:
                new_data["pricing"] = "150-250"
            else:
                new_data["pricing"] = "250+"
        if "rating" in new_data and new_data.get("rating") is not None:
            try:
                rating = float(new_data["rating"])
                rating = max(0.0, min(5.0, rating))
                new_data["rating"] = round(rating, 1)
            except (TypeError, ValueError):
                pass
        langs = new_data.get("languages") or []
        new_data["primary_language"] = langs[0] if langs else None
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
        if "doctorName" in new_data:
            new_data["doctor_name"] = new_data.pop("doctorName")
        modified.append(new_data)
    return modified
