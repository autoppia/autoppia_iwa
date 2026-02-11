"""
Shared data helpers for autozone_3.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """
    Fetch products data for Autozone.

    This is the unified function replacing:
    - fetch_products_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of products
    """
    from .main import FRONTEND_PORT_INDEX, autozone_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autozone_project.id}"

    items = await load_dataset_data(
        backend_url=autozone_project.backend_url,
        project_key=project_key,
        entity_type="products",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
    )
    return items or []
