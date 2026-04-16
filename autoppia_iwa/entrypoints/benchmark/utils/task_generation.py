"""Task generation utilities for benchmark projects."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import WebProject


def get_cache_filename(project: WebProject, task_cache_dir: str) -> Path:
    """Generate a project-specific cache filename based on the project's name or ID."""
    safe_name = project.id.replace("/", "_").replace("\\", "_")
    cache_dir = Path(task_cache_dir)
    is_data_extraction_cache = "dataextraction" in cache_dir.as_posix().lower()
    filename = f"{safe_name}_DE_tasks.json" if is_data_extraction_cache else f"{safe_name}_tasks.json"
    return cache_dir / filename


def _write_tasks_to_file(filename: Path, cache_data: dict) -> None:
    """Synchronous helper to write tasks to JSON file."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)


async def save_tasks_to_json(tasks: list[Task], project: WebProject, task_cache_dir: str) -> bool:
    """Save tasks to a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        serialized_tasks = [task.serialize() for task in tasks]
        cache_data = {"project_id": project.id, "project_name": project.name, "timestamp": datetime.now().isoformat(), "tasks": serialized_tasks}
        await asyncio.to_thread(_write_tasks_to_file, filename, cache_data)
        logger.info(f"Tasks for project '{project.name}' saved to {filename}")
        return True
    except (OSError, TypeError) as e:
        logger.error(f"Error saving tasks to {filename}: {e!s}")
        return False


def _read_tasks_from_file(filename: Path) -> dict:
    """Synchronous helper to read tasks from JSON file."""
    with open(filename, encoding="utf-8") as f:
        return json.load(f)


def filter_tasks_by_use_cases(
    tasks: list[Task],
    use_cases: list[str] | None,
    *,
    test_types: str = "event_only",
) -> list[Task]:
    """
    Keep tasks whose use_case.name matches one of use_cases (case-insensitive).

    When use_cases is None or empty, returns tasks unchanged.

    For data-extraction-only tasks without ``use_case`` (for example, tasks
    generated through ``generate_de_tasks``), we also match ``de_use_case_name``.
    """
    if not use_cases:
        return tasks
    wanted = {u.strip().casefold() for u in use_cases if u and str(u).strip()}
    if not wanted:
        return tasks

    out: list[Task] = []
    for task in tasks:
        use_case = getattr(task, "use_case", None)
        name = getattr(use_case, "name", None) if use_case is not None else None
        if isinstance(name, str) and name.strip().casefold() in wanted:
            out.append(task)
            continue
        if test_types == "data_extraction_only":
            de_name = getattr(task, "de_use_case_name", None)
            if isinstance(de_name, str) and de_name.strip().casefold() in wanted:
                out.append(task)
    return out


def load_tasks_from_custom_json(
    tasks_json_path: Path | str,
    projects_by_id: dict[str, WebProject],
) -> tuple[WebProject, list[Task]]:
    """
    Load tasks from a custom JSON file. Same shape as cache: project_id, project_name, tasks.

    Raises:
        FileNotFoundError: Path does not exist.
        ValueError: Path is not a file, invalid JSON, missing keys, empty tasks, or unknown project_id.
        Exception: Task deserialization failure (re-raised with index context).
    """
    path = Path(tasks_json_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"tasks_json_path does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"tasks_json_path must be a file, not a directory: {path}")

    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        raise OSError(f"Failed to read tasks file {path}: {e}") from e

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in tasks file {path}: {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Tasks file must contain a JSON object; got {type(data).__name__} at {path}")

    project_id = data.get("project_id")
    if project_id is None:
        raise ValueError(f"Tasks file {path} is missing required key 'project_id'")
    if not isinstance(project_id, str):
        raise ValueError(f"Tasks file {path}: 'project_id' must be a string; got {type(project_id).__name__}")

    tasks_data = data.get("tasks")
    if tasks_data is None:
        raise ValueError(f"Tasks file {path} is missing required key 'tasks'")
    if not isinstance(tasks_data, list):
        raise ValueError(f"Tasks file {path}: 'tasks' must be a list; got {type(tasks_data).__name__}")
    if len(tasks_data) == 0:
        raise ValueError(f"Tasks file {path}: tasks array is empty")

    project = projects_by_id.get(project_id)
    if project is None:
        available = ", ".join(sorted(projects_by_id.keys()))
        raise ValueError(f"Unknown project_id '{project_id}' in tasks file {path}. Available: {available}")

    tasks: list[Task] = []
    for i, task_data in enumerate(tasks_data):
        if not isinstance(task_data, dict):
            raise ValueError(f"Task at index {i} in {path} is not a JSON object; got {type(task_data).__name__}")
        try:
            tasks.append(Task.deserialize(task_data))
        except Exception as e:
            task_id = task_data.get("id", "?")
            logger.error(f"Task at index {i} (id={task_id}) failed to deserialize: {e}")
            raise ValueError(f"Task at index {i} failed to deserialize: {e}") from e

    logger.info(f"Loaded {len(tasks)} tasks from custom file {path} for project '{project.name}'")
    return (project, tasks)


async def load_tasks_from_json(project: WebProject, task_cache_dir: str) -> list[Task] | None:
    """Load tasks from a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        if not filename.exists():
            return None

        data = await asyncio.to_thread(_read_tasks_from_file, filename)
        tasks_data = data.get("tasks", [])
        if not tasks_data:
            return None

        tasks = [Task.deserialize(task_data) for task_data in tasks_data]
        logger.info(f"Loaded {len(tasks)} tasks from cache for '{project.name}'")
        return tasks
    except (OSError, json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error loading tasks from {filename}: {e!s}")
        return None


async def generate_tasks_for_project(
    project: WebProject,
    prompts_per_use_case: int = 1,
    use_cases: list[str] | None = None,
    dynamic: bool = False,
) -> list[Task]:
    """Generate tasks for the given project."""
    try:
        config = TaskGenerationConfig(
            prompts_per_use_case=prompts_per_use_case,
            use_cases=use_cases,
            dynamic=dynamic,
        )

        pipeline = TaskGenerationPipeline(web_project=project, config=config)
        tasks = await pipeline.generate()
        if not tasks:
            logger.warning(f"No tasks generated for '{project.name}'")
        return tasks
    except Exception as e:
        logger.error(f"[tasks] Failed to generate tasks for '{project.name}': {e}", exc_info=True)
        return []


def get_projects_by_ids(all_projects: list[WebProject], ids_to_run: list[str]) -> list[WebProject]:
    """
    Return projects whose id is in ids_to_run.
    """
    if not all_projects:
        logger.error("No projects available in all_projects")
        return []

    if not ids_to_run:
        logger.warning("No project IDs specified in ids_to_run")
        return []

    projects_by_id = {p.id: p for p in all_projects}
    missing_ids = [pid for pid in ids_to_run if pid not in projects_by_id]
    if missing_ids:
        available_ids = list(projects_by_id.keys())
        logger.error(f"Project IDs not found: {missing_ids}. Available projects: {available_ids}")
        raise ValueError(f"Project IDs not found: {missing_ids}")

    return [projects_by_id[pid] for pid in ids_to_run]
