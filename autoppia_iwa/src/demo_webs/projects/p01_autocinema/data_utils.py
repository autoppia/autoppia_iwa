"""
Shared data helpers for autocinema_1.
Provides a single place to fetch and transform the movies dataset so other modules
don't need to duplicate the logic.
"""

from typing import Any

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


def _normalize_rating(value: Any) -> Any:
    """If rating is a whole float (8.0, 7.0), return int (8, 7); otherwise return as-is (e.g. 8.1, 5.7)."""
    if value is None:
        return None
    if isinstance(value, float) and value == int(value):
        return int(value)
    return value


def apply_mapping(record: dict, mapping: dict) -> dict:
    """Rename fields in a single dictionary according to mapping rules."""
    new_record = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value

        # Convert ONLY `cast` field list → comma-separated string
        if key == "cast" and isinstance(value, list):
            value = ", ".join(value)

        new_record[new_key] = value

    # Process director field:
    # - If single director: keep as string (use operators: equals, not_equals, contains, not_contains)
    # - If multiple directors (comma-separated): convert to list (use operators: contains, not_contains, in_list, not_in_list)
    if "director" in new_record and isinstance(new_record["director"], str):
        director_value = new_record["director"].strip()
        if "," in director_value:
            # Multiple directors: convert to list
            directors_list = [d.strip() for d in director_value.split(",") if d.strip()]
            new_record["director"] = directors_list
        # If single director, keep as string (no change needed)

    # Normalize rating: 8.0 -> 8, 7.0 -> 7; leave 8.1, 5.7 etc. as-is
    if "rating" in new_record:
        new_record["rating"] = _normalize_rating(new_record["rating"])

    return new_record


def transform_all(records: list[dict], mapping: dict) -> list[dict]:
    """Apply field mapping to a list of dictionaries."""
    return [apply_mapping(record, mapping) for record in records]


async def fetch_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """
    Fetch and normalize movies data from the backend API.

    This is the unified function replacing:
    - fetch_movies_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of normalized movies
    """
    from .main import FRONTEND_PORT_INDEX, autocinema_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autocinema_project.id}"
    entity_type = "movies"

    items = await load_dataset_data(
        backend_url=autocinema_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
        filter_key="category",
    )
    if items:
        field_mapping = {
            "title": "name",
            "description": "desc",
            "image_path": "img_file",
        }
        mapped_items = transform_all(items, field_mapping)
        return mapped_items
    return []
