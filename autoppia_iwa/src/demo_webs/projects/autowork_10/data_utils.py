"""
Shared dataset helpers for autowork_10.
"""

from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data


async def fetch_experts_data(seed_value: int | None = None, count: int = 50) -> list[dict]:
    """Fetch and normalize experts data."""
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


async def get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    """Main data loader function for autowork_10."""
    return await fetch_experts_data(seed_value=seed_value, count=count)


async def get_all_data(seed_value: int | None = None, count: int = 100) -> dict[str, list[dict]]:
    """Load complete dataset for this project."""
    experts = await get_data(seed_value=seed_value, count=count)
    return {"experts": experts}
