import json
import os
from datetime import datetime
from pathlib import Path

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject


def get_cache_filename(project: WebProject, task_cache_dir: str) -> str:
    """Generate a project-specific cache filename based on the project's name or ID."""
    safe_name = project.id.replace("/", "_").replace("\\", "_")
    return os.path.join(task_cache_dir, f"{safe_name}_tasks.json")


async def save_tasks_to_json(tasks: list[Task], project: WebProject, task_cache_dir: str) -> bool:
    """Save tasks to a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        # Ensure directory exists
        os.makedirs(task_cache_dir, exist_ok=True)

        # Serialize tasks
        serialized_tasks = [task.serialize() for task in tasks]

        # Compose cache data
        cache_data = {"project_id": project.id, "project_name": project.name, "timestamp": datetime.now().isoformat(), "tasks": serialized_tasks}

        with open(filename, "w") as f:
            json.dump(cache_data, f, indent=2)

        print(f"Tasks for project '{project.name}' saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving tasks to {filename}: {e!s}")
        return False


async def load_tasks_from_json(project: WebProject, task_cache_dir: str) -> list[Task] | None:
    """Load tasks from a project-specific JSON file."""
    filename = get_cache_filename(project, task_cache_dir)
    try:
        if not Path(filename).exists():
            return None

        with open(filename) as f:
            data = json.load(f)

        tasks_data = data.get("tasks", [])
        if not tasks_data:
            return None

        # Deserialize tasks
        tasks = [Task.deserialize(task_data) for task_data in tasks_data]

        print(f"Loaded {len(tasks)} tasks from cache for '{project.name}'")
        return tasks
    except Exception as e:
        print(f"Error loading tasks from {filename}: {e!s}")
        return None
