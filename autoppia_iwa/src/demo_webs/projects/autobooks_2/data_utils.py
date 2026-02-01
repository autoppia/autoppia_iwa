"""
Shared data helpers for autobooks_2.
Consolidates the dataset loading + mapping logic so other modules avoid duplication.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


def _apply_mapping(record: dict, mapping: dict) -> dict:
    """Rename fields in a single dictionary according to mapping rules."""
    new_record: dict = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value
    return new_record


def _transform_all(records: list[dict], mapping: dict) -> list[dict]:
    """Apply field mapping to a list of dictionaries."""
    return [_apply_mapping(record, mapping) for record in records]


async def fetch_books_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Fetch and normalize books data from the backend API."""
    from .main import FRONTEND_PORT_INDEX, books_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{books_project.id}"
    entity_type = "books"

    items = await load_dataset_data(
        backend_url=books_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
    )
    if items:
        field_mapping = {"director": "author", "duration": "page_count", "img": "img_file"}
        return _transform_all(items, field_mapping)
    return []


async def get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Main data loader function for autobooks_2."""
    return await fetch_books_data(seed_value=seed_value, count=count)


async def get_all_data(seed_value: int | None = None, count: int = 100) -> dict[str, list[dict]]:
    """Load complete dataset for this project."""
    books = await get_data(seed_value=seed_value, count=count)
    return {"books": books}
