"""
Shared dataset helpers for autolodge_8.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_hotels_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Fetch and normalize hotel data."""
    from .data import get_modify_data
    from .main import FRONTEND_PORT_INDEX, lodge_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{lodge_project.id}"

    items = await load_dataset_data(
        backend_url=lodge_project.backend_url,
        project_key=project_key,
        entity_type="hotels",
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
    )
    if not items:
        return []
    return get_modify_data(items)


async def _get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Main data loader function for autolodge_8."""
    return await fetch_hotels_data(seed_value=seed_value, count=count)
