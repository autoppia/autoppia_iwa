"""
Shared dataset helpers for autowork_10.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """
    Fetch and normalize experts data.

    This is the unified function replacing:
    - fetch_experts_data()
    - get_data()
    - get_all_data()

    Args:
        seed_value: Seed value for deterministic selection
        count: Number of items to fetch

    Returns:
        list[dict] of normalized experts
    """
    from .data import expert_data_modified
    from .main import FRONTEND_PORT_INDEX, work_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{work_project.id}"
    items = await load_dataset_data(
        backend_url=work_project.backend_url,
        project_key=project_key,
        entity_type="experts",
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="select",
    )
    if not items:
        return []
    return expert_data_modified(items)
