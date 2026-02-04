"""
Shared dataset helpers for autowork_10.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(
    entity_type: str = "experts",
    seed_value: int | None = None,
    count: int = 50,
    method: str = "select",
) -> list[dict]:
    """
    Fetch and normalize data for the specified entity type.

    This is the unified function replacing:
    - fetch_experts_data()
    - get_data()
    - get_all_data()

    Args:
        entity_type: Type of entity to fetch ("experts" or "skills")
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch
        method: Selection method (default: "select")

    Returns:
        list[dict] of normalized data
    """
    from .data import expert_data_modified
    from .main import FRONTEND_PORT_INDEX, work_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{work_project.id}"
    items = await load_dataset_data(
        backend_url=work_project.backend_url,
        project_key=project_key,
        entity_type=entity_type,
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method=method,
    )
    if not items:
        return []

    # Apply transformation only for experts
    if entity_type == "experts":
        return expert_data_modified(items)

    # Return skills as-is (list of dicts with "name" field, or list of strings)
    return items
