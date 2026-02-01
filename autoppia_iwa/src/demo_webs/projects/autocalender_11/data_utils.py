"""
Shared dataset helpers for autocalender_11.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


def _apply_mapping(record: dict, mapping: dict) -> dict:
    new_record = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value
    return new_record


def _transform_all(records: list[dict], mapping: dict) -> list[dict]:
    return [_apply_mapping(record, mapping) for record in records]


async def fetch_events_data(seed_value: int | None = None, count: int = 200) -> list[dict]:
    """Fetch and normalize events data for autocalender."""
    from .main import FRONTEND_PORT_INDEX, autocalendar_project

    field_mapping = {"allDay": "all_day", "recurrenceEndDate": "recurrence_end_date"}

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autocalendar_project.id}"

    items = await load_dataset_data(
        backend_url=autocalendar_project.backend_url,
        project_key=project_key,
        entity_type="events",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
        method="select",
    )
    if not items:
        return []
    return _transform_all(items, field_mapping)


async def _get_data(seed_value: int | None = None, count: int = 200) -> list[dict]:
    """Main data loader function for autocalender_11."""
    return await fetch_events_data(seed_value=seed_value, count=count)
