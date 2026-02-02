"""
Shared email dataset helpers for automail_6.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


def _apply_mapping(record: dict, mapping: dict) -> dict:
    new_record = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value
    return new_record


def _transform_all(records: list[dict], mapping: dict) -> list[dict]:
    return [_apply_mapping(record, mapping) for record in records]


async def fetch_emails_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch and normalize emails data from the backend."""
    from .data import transform_emails_list
    from .main import FRONTEND_PORT_INDEX, automail_project

    field_mapping = {"isRead": "is_read", "isStarred": "is_starred", "isDraft": "is_draft", "isImportant": "is_important"}

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{automail_project.id}"
    items = await load_dataset_data(
        backend_url=automail_project.backend_url,
        project_key=project_key,
        entity_type="emails",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
        method="distribute",
        filter_key="category",
    )
    if not items:
        return []
    modified_emails = transform_emails_list(items)
    return _transform_all(modified_emails, field_mapping)


async def get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Main data loader function for automail_6."""
    return await fetch_emails_data(seed_value=seed_value, count=count)


async def get_all_data(seed_value: int | None = None, count: int = 100) -> dict[str, list[dict]]:
    """Load complete dataset for this project."""
    emails = await get_data(seed_value=seed_value, count=count)
    return {"emails": emails}
