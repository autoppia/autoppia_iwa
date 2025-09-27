"""
Thin wrapper for generating tasks with optional per-project caching.
Keeps your existing generation pipeline and JSON cache format.
"""

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
):
    """
    Generate tasks for the given project, preferring cache when requested.

    Returns:
        list[Task]: generated or cached tasks.
    """
    if use_cached:
        cached = await load_tasks_from_json(project, cache_dir)
        if cached:
            print(f"[tasks] Using cache ({len(cached)}) for '{project.name}'")
            return cached

    tasks = await _generate(
        project,
        use_cached_tasks=False,  # force generation if no valid cache
        task_cache_dir=cache_dir,
        prompts_per_use_case=prompts_per_use_case,
        num_of_use_cases=num_use_cases,
    )
    if tasks:
        await save_tasks_to_json(tasks, project, cache_dir)
    return tasks


def get_projects_by_ids(all_projects: list[WebProject], ids_to_run: list[str]) -> list[WebProject]:
    """
    Devuelve los proyectos cuyo id esté en ids_to_run.
    """
    # indexar por id para búsqueda rápida
    projects_by_id = {p.id: p for p in all_projects}

    # devolver solo los que están en ids_to_run
    return [projects_by_id[pid] for pid in ids_to_run if pid in projects_by_id]
