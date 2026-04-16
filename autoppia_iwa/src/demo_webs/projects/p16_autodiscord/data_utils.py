"""
Shared dataset helper for autodiscord_16 (servers, channels, messages, members).
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
    seed_value: int | None = None,
    count: int = 50,
) -> list[dict]:
    """
    Fetch Discord-like data for the requested entity type.

    Args:
        entity_type: Type of entity (servers, channels, messages, members)
        method: Selection method (distribute, select, etc.)
        filter_key: Key to filter on
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] for the requested entity type
    """
    from .main import FRONTEND_PORT_INDEX, discord_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{discord_project.id}"
    items = await load_dataset_data(
        backend_url=discord_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
        method=method if method else None,
        filter_key=filter_key if filter_key else None,
    )
    return items or []
