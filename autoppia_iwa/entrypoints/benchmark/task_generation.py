"""
Thin wrapper for generating tasks with optional per-project caching.
Keeps your existing generation pipeline and JSON cache format.
"""

from loguru import logger

from autoppia_iwa.entrypoints.benchmark.utils.tasks import (
    generate_tasks_for_web_project as _generate,
    load_tasks_from_json,
    save_tasks_to_json,
)
from autoppia_iwa.src.demo_webs.classes import WebProject


async def generate_tasks_for_project(
    project: WebProject,
    use_cached: bool,
    cache_dir: str,
    prompts_per_use_case: int,
    num_use_cases: int,
    use_cases: list[str] | None = None,
):
    """
    Generate tasks for the given project, preferring cache when requested.

    Returns:
        list[Task]: generated or cached tasks.
    """
    try:
        if use_cached:
            try:
                cached = await load_tasks_from_json(project, cache_dir)
                if cached:
                    logger.info(f"[tasks] Using cache ({len(cached)} tasks) for '{project.name}'")
                    return cached
                else:
                    logger.info(f"[tasks] No valid cache found for '{project.name}', generating new tasks...")
            except Exception as e:
                logger.warning(f"[tasks] Failed to load cache for '{project.name}': {e}, generating new tasks...")

        logger.info(f"[tasks] Generating tasks for '{project.name}'...")
        tasks = await _generate(
            project,
            use_cached_tasks=False,  # force generation if no valid cache
            task_cache_dir=cache_dir,
            prompts_per_use_case=prompts_per_use_case,
            num_of_use_cases=num_use_cases,
            use_cases=use_cases,
        )

        if tasks and cache_dir:
            logger.info(f"[tasks] Generated {len(tasks)} tasks for '{project.name}'")
            try:
                await save_tasks_to_json(tasks, project, cache_dir)
            except Exception as e:
                logger.warning(f"[tasks] Failed to save tasks to cache for '{project.name}': {e}")
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
