"""Task generation utilities for benchmark projects."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject


# =====================
# Cache File Management
# =====================
def get_cache_filename(project: WebProject, task_cache_dir: str) -> Path:
    """Generate a project-specific cache filename based on the project's name or ID."""
    safe_name = project.id.replace("/", "_").replace("\\", "_")
    return Path(task_cache_dir) / f"{safe_name}_tasks.json"


def _write_tasks_to_file(filename: Path, cache_data: dict) -> None:
    """Synchronous helper to write tasks to JSON file."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)


async def save_tasks_to_json(tasks: list[Task], project: WebProject, task_cache_dir: str) -> bool:
    """Save tasks to a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        # Serialize tasks
        serialized_tasks = [task.serialize() for task in tasks]

        # Compose cache data
        cache_data = {"project_id": project.id, "project_name": project.name, "timestamp": datetime.now().isoformat(), "tasks": serialized_tasks}

        # Use async file I/O to avoid blocking event loop
        await asyncio.to_thread(_write_tasks_to_file, filename, cache_data)

        logger.info(f"Tasks for project '{project.name}' saved to {filename}")
        return True
    except (OSError, json.JSONEncodeError) as e:
        logger.error(f"Error saving tasks to {filename}: {e!s}")
        return False


def _read_tasks_from_file(filename: Path) -> dict:
    """Synchronous helper to read tasks from JSON file."""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


async def load_tasks_from_json(project: WebProject, task_cache_dir: str) -> list[Task] | None:
    """Load tasks from a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        if not filename.exists():
            return None

        # Use async file I/O to avoid blocking event loop
        data = await asyncio.to_thread(_read_tasks_from_file, filename)

        tasks_data = data.get("tasks", [])
        if not tasks_data:
            return None

        # Deserialize tasks
        tasks = [Task.deserialize(task_data) for task_data in tasks_data]

        logger.info(f"Loaded {len(tasks)} tasks from cache for '{project.name}'")
        return tasks
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error loading tasks from {filename}: {e!s}")
        return None


# =====================
# Task Generation
# =====================
async def generate_tasks_for_project(
    project: WebProject,
    prompts_per_use_case: int = 1,
    use_cases: list[str] | None = None,
    dynamic: bool = False,
) -> list[Task]:
    """Generate tasks for the given project."""
    try:
        logger.info(f"[tasks] Generating tasks for '{project.name}'...")

        config = TaskGenerationConfig(
            prompts_per_use_case=prompts_per_use_case,
            use_cases=use_cases,
            dynamic=dynamic,
        )

        pipeline = TaskGenerationPipeline(web_project=project, config=config)
        tasks = await pipeline.generate()

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
