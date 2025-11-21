"""
Shared dataset helpers for autodelivery_7.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_autodelivery_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 100,
) -> list[dict]:
    """Fetch data for the requested entity type."""
    from .main import FRONTEND_PORT_INDEX, autodelivery_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autodelivery_project.id}"

    items = await load_dataset_data(
        backend_url=autodelivery_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method=method if method else None,
        filter_key=filter_key if filter_key else None,
    )
    return items or []
