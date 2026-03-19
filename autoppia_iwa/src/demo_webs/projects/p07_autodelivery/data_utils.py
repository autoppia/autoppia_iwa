"""
Shared dataset helpers for autodelivery_7.
"""

from autoppia_iwa.src.demo_webs.data_provider import load_dataset_data


async def fetch_data(
    seed_value: int | None = None,
    count: int = 50,
) -> list[dict]:
    """
    Fetch restaurant data for autodelivery.

    This is the unified function replacing:
    - fetch_autodelivery_data()
    - get_data()
    - get_all_data()

    Args:
        method: Selection method (distribute, etc.)
        filter_key: Key to filter on
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of restaurant data
    """
    from .main import FRONTEND_PORT_INDEX, autodelivery_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autodelivery_project.id}"

    items = await load_dataset_data(
        backend_url=autodelivery_project.backend_url,
        project_key=project_key,
        entity_type="restaurants",
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
        filter_key="cuisine",
    )
    return items or []
