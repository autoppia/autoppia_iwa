"""
Shared dataset helpers for autodelivery_7.
"""

from autoppia_iwa.src.demo_webs.data_provider import load_dataset_data


def _enrich_restaurants_menu_derived_fields(restaurants: list[dict]) -> list[dict]:
    """Set menu-derived fields not from the server: ``dishes``, ``names_of_menu_items``."""
    for row in restaurants:
        if not isinstance(row, dict):
            continue
        menu = row.get("menu")
        if not isinstance(menu, list):
            row["dishes"] = 0
            row["names_of_menu_items"] = []
            continue
        row["dishes"] = len(menu)
        row["names_of_menu_items"] = [str(entry["name"]) for entry in menu if isinstance(entry, dict) and entry.get("name") is not None and str(entry["name"]).strip()]
    return restaurants


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
        list[dict] of restaurant data with ``dishes`` (menu length) and ``names_of_menu_items``
        (non-empty menu item ``name`` strings), derived from each row's ``menu``.
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
    items = items or []
    _enrich_restaurants_menu_derived_fields(items)
    return items
