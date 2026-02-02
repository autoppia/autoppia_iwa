"""
Shared data helpers for autozone_3.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_products_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch products data for Autozone."""
    from .main import FRONTEND_PORT_INDEX, omnizone_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{omnizone_project.id}"

    items = await load_dataset_data(
        backend_url=omnizone_project.backend_url,
        project_key=project_key,
        entity_type="products",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
    )
    return items or []


async def get_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Main data loader function for autozone_3."""
    return await fetch_products_data(seed_value=seed_value, count=count)


async def get_all_data(seed_value: int | None = None, count: int = 50) -> dict[str, list[dict]]:
    """Load complete dataset for this project."""
    products = await get_data(seed_value=seed_value, count=count)
    return {"products": products}
