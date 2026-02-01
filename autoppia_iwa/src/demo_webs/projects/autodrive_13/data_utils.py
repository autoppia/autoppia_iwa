"""
Shared dataset helpers for autodrive_13.
"""

from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_drive_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 100,
) -> list[dict]:
    """Fetch dataset rows for the given entity type."""
    from .main import FRONTEND_PORT_INDEX, drive_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{drive_project.id}"

    items = await load_dataset_data(
        backend_url=drive_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method=method if method else "select",
        filter_key=filter_key if filter_key else None,
    )
    return items or []


def extract_drive_dataset(dataset: Any, entity_type: str) -> list[dict[str, Any]] | None:
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


async def _get_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 100,
) -> list[dict]:
    """Main data loader function for autodrive_13."""
    return await fetch_drive_data(
        entity_type=entity_type,
        method=method,
        filter_key=filter_key,
        seed_value=seed_value,
        count=count,
    )
