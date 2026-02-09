"""
Shared dataset helpers for autolodge_8.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """
    Fetch and normalize hotel data.

    This is the unified function replacing:
    - fetch_hotels_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of normalized hotels
    """
    from .data import get_modify_data
    from .main import FRONTEND_PORT_INDEX, lodge_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{lodge_project.id}"

    items = await load_dataset_data(
        backend_url=lodge_project.backend_url,
        project_key=project_key,
        entity_type="hotels",
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
        filter_key="location",
    )
    if not items:
        return []
    return get_modify_data(items)
