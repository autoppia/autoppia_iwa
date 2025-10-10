import json
import os
from datetime import datetime
from pathlib import Path

from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject


def get_cache_filename(project: WebProject, task_cache_dir: str) -> str:
    """
    Generate a project-specific cache filename based on the project's name or ID.
    """
    safe_name = project.name.replace(" ", "_").lower()
    return os.path.join(task_cache_dir, f"{safe_name}_tasks.json")


async def save_tasks_to_json(tasks: list[Task], project: WebProject, task_cache_dir: str) -> bool:
    """
    Append new tasks to existing project-specific JSON file without duplicating tasks.
    """
    filename = get_cache_filename(project, task_cache_dir)
    try:
        # Load existing tasks if file exists
        existing_tasks = []
        if Path(filename).exists():
            with open(filename) as f:
                data = json.load(f)
                existing_tasks = data.get("tasks", [])

        # Serialize new tasks and merge (avoiding duplicates by 'id')
        new_serialized = [task.serialize() for task in tasks]
        all_tasks_by_id = {task["id"]: task for task in existing_tasks}
        for new_task in new_serialized:
            all_tasks_by_id[new_task["id"]] = new_task

        # Compose final cache data
        cache_data = {"project_id": project.id, "project_name": project.name, "timestamp": datetime.now().isoformat(), "tasks": list(all_tasks_by_id.values())}

        with open(filename, "w") as f:
            json.dump(cache_data, f, indent=2)

        print(f"Tasks for project '{project.name}' saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving tasks to {filename}: {e!s}")
        return False


async def load_tasks_from_json(project: WebProject, task_cache_dir: str) -> list[Task] | None:
    """
    Load tasks from a project-specific JSON file if it exists.
    """
    filename = get_cache_filename(project, task_cache_dir)
    if not os.path.exists(filename):
        print(f"Cache file {filename} not found for project '{project.name}'")
        return None

    try:
        with open(filename) as f:
            cache_data = json.load(f)

        # Verify this cache belongs to the correct project
        if cache_data.get("project_id") != project.id and cache_data.get("project_name") != project.name:
            print("Cache file belongs to a different project.")
            return None

        tasks_data = cache_data.get("tasks", [])
        tasks = [Task.deserialize(tdata) for tdata in tasks_data]

        print(f"Loaded {len(tasks)} tasks for project '{project.name}' from {filename}")
        return tasks
    except Exception as e:
        print(f"Error loading tasks from {filename}: {e!s}")
        return None


async def generate_tasks_for_web_project(
    project: WebProject, use_cached_tasks: bool, task_cache_dir: str, prompts_per_use_case: int = 1, num_of_use_cases: int = 1, use_cases: list[str] | None = None
) -> list[Task]:
    """
    Generate tasks for the given demo project, possibly using cached tasks.
    """
    if use_cached_tasks:
        cached_tasks = await load_tasks_from_json(project, task_cache_dir)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for '{project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for '{project.name}', generating new tasks...")

    config = TaskGenerationConfig(prompts_per_use_case=prompts_per_use_case, num_use_cases=num_of_use_cases, use_cases=use_cases)

    print(f"Generating tasks for {project.name}...")
    pipeline = TaskGenerationPipeline(web_project=project, config=config)
    tasks = await pipeline.generate()

    if tasks:
        await save_tasks_to_json(tasks, project, task_cache_dir)

    return tasks
