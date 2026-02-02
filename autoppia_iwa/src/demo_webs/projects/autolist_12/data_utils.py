"""
Shared dataset helpers for autolist_12.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_tasks_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch and return the tasks dataset for autolist."""
    from .main import FRONTEND_PORT_INDEX, autolist_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{autolist_project.id}"
    items = await load_dataset_data(
        backend_url=autolist_project.backend_url,
        project_key=project_key,
        entity_type="tasks",
        seed_value=seed_value if seed_value is not None else 0,
        limit=count,
        method="distribute",
    )
    return items if items else []
