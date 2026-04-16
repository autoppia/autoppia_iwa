"""
Shared email dataset helpers for automail_6.
"""

from autoppia_iwa.src.demo_webs.data_provider import load_dataset_data


def _apply_mapping(record: dict, mapping: dict) -> dict:
    new_record = {}
    for key, value in record.items():
        new_key = mapping.get(key, key)
        new_record[new_key] = value
    return new_record


def _transform_all(records: list[dict], mapping: dict) -> list[dict]:
    return [_apply_mapping(record, mapping) for record in records]


async def fetch_data(
    seed_value: int | None = None,
    count: int = 50,
    entity_type: str | None = None,
    method: str | None = None,
    filter_key: str | None = None,
) -> list[dict]:
    """
    Fetch project data from the backend.

    This is the unified function replacing:
    - fetch_emails_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch
        entity_type: Type of entity to fetch
        method: Method used to fetch the data
        filter_key: Filter key applied to the dataset

    Returns:
        list[dict] records. For `entity_type="emails"` records are normalized.
    """
    from .main import FRONTEND_PORT_INDEX, automail_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{automail_project.id}"
    items = await load_dataset_data(
        backend_url=automail_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
        method=method,
        filter_key=filter_key,
    )
    if not items:
        return []

    if entity_type == "emails":
        from .data import transform_emails_list

        field_mapping = {"isRead": "is_read", "isStarred": "is_starred", "isDraft": "is_draft", "isImportant": "is_important"}
        modified_emails = transform_emails_list(items)
        return _transform_all(modified_emails, field_mapping)

    return items
