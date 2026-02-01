"""
Shared dataset helper for autocrm_5 (matters, clients, logs, etc.).
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_crm_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 50,
) -> list[dict]:
    """Fetch CRM data for the requested entity type."""
    from .main import FRONTEND_PORT_INDEX, crm_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{crm_project.id}"
    items = await load_dataset_data(
        backend_url=crm_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
        method=method if method else None,
        filter_key=filter_key if filter_key else None,
    )
    return items or []


async def get_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 50,
) -> list[dict]:
    """Main data loader function for autocrm_5."""
    return await fetch_crm_data(entity_type, method=method, filter_key=filter_key, seed_value=seed_value, count=count)
