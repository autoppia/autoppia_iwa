"""
Shared data helpers for autocinema_1.
Provides a single place to fetch and transform the movies dataset so other modules
don't need to duplicate the logic.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


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
    return new_record


def transform_all(records: list[dict], mapping: dict) -> list[dict]:
    """Apply field mapping to a list of dictionaries."""
    return [apply_mapping(record, mapping) for record in records]


async def fetch_movies_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Fetch and normalize movies data from the backend API."""
    from .main import FRONTEND_PORT_INDEX, cinema_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{cinema_project.id}"
    entity_type = "movies"

    items = await load_dataset_data(
        backend_url=cinema_project.backend_url,
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


async def _get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Main data loader function for autocinema_1."""
    return await fetch_movies_data(seed_value=seed_value, count=count)
