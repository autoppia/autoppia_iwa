"""
Shared restaurant dataset helpers for autodining_4.
"""

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data

_RESTAURANT_DATA_CACHE: dict[tuple[int | None, int], list[dict]] = {}


def _apply_mapping(record: dict, mapping: dict) -> dict:
    new_record: dict = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value
    return new_record


def _transform_all(records: list[dict], mapping: dict) -> list[dict]:
    return [_apply_mapping(record, mapping) for record in records]


async def fetch_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """
    Fetch restaurant data from the backend with a small in-memory cache.

    This is the unified function replacing:
    - fetch_restaurant_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of normalized restaurants
    """
    from .main import FRONTEND_PORT_INDEX, autodining_project

    cache_key = (seed_value, count)
    if cache_key in _RESTAURANT_DATA_CACHE:
        return _RESTAURANT_DATA_CACHE[cache_key]

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autodining_project.id}"

    try:
        items = await load_dataset_data(
            backend_url=autodining_project.backend_url,
            project_key=project_key,
            entity_type="restaurants",
            seed_value=seed_value if seed_value is not None else 0,
            limit=count,
            method="distribute",
            filter_key="cuisine",
        )
        if items:
            field_mapping = {
                "namepool": "name",
                "staticBookings": "bookings",
                "staticReviews": "reviews",
                "staticStars": "rating",
                "staticPrices": "price",
            }
            mapped_items = _transform_all(items, field_mapping)
            _RESTAURANT_DATA_CACHE[cache_key] = mapped_items
            logger.debug(f"Fetched and cached {len(mapped_items)} restaurants (seed={seed_value}, count={count})")
            return mapped_items
        logger.warning(f"No restaurant data returned from API (seed={seed_value}, count={count})")
    except Exception as exc:  # pragma: no cover - best effort
        logger.error(f"Failed to fetch restaurant data from API: {exc}")
    return []
