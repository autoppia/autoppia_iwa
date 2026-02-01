"""Task generation utilities for benchmark projects."""

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject


async def generate_tasks_for_web_project(
    project: WebProject,
    prompts_per_use_case: int = 1,
    use_cases: list[str] | None = None,
    dynamic: bool = False,
) -> list[Task]:
    """Generate tasks for the given demo project."""
    config = TaskGenerationConfig(
        prompts_per_use_case=prompts_per_use_case,
        use_cases=use_cases,
        dynamic=dynamic,
    )

    print(f"Generating tasks for {project.name}...")
    pipeline = TaskGenerationPipeline(web_project=project, config=config)
    tasks = await pipeline.generate()

    return tasks


async def generate_tasks_for_project(
    project: WebProject,
    prompts_per_use_case: int,
    use_cases: list[str] | None = None,
    dynamic: bool = False,
):
    """Generate tasks for the given project."""
    try:
        logger.info(f"[tasks] Generating tasks for '{project.name}'...")
        tasks = await generate_tasks_for_web_project(
            project,
            prompts_per_use_case=prompts_per_use_case,
            use_cases=use_cases,
            dynamic=dynamic,
        )

        if tasks:
            logger.info(f"[tasks] Generated {len(tasks)} tasks for '{project.name}'")
        else:
            logger.warning(f"[tasks] No tasks generated for '{project.name}'")

        return tasks

    except Exception as e:
        logger.error(f"[tasks] Failed to generate tasks for '{project.name}': {e}", exc_info=True)
        return []


def get_projects_by_ids(all_projects: list[WebProject], ids_to_run: list[str]) -> list[WebProject]:
    """
    Return projects whose id is in ids_to_run.

    Args:
        all_projects: List of all available projects
        ids_to_run: List of project IDs to filter for

    Returns:
        List of projects matching the requested IDs

    Raises:
        ValueError: If any requested project ID is not found
    """

    if not all_projects:
        logger.error("No projects available in all_projects")
        return []

    if not ids_to_run:
        logger.warning("No project IDs specified in ids_to_run")
        return []

    # Index by id for fast lookup
    projects_by_id = {p.id: p for p in all_projects}

    # Check for missing projects
    missing_ids = [pid for pid in ids_to_run if pid not in projects_by_id]
    if missing_ids:
        available_ids = list(projects_by_id.keys())
        logger.error(f"Project IDs not found: {missing_ids}. Available projects: {available_ids}")
        raise ValueError(f"Project IDs not found: {missing_ids}")

    # Return only the requested projects
    selected_projects = [projects_by_id[pid] for pid in ids_to_run]
    logger.info(f"Selected {len(selected_projects)} projects: {[p.name for p in selected_projects]}")

    return selected_projects
