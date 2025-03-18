import json
import os
from datetime import datetime

from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.di_container import DIContainer


def get_cache_filename(project: WebProject, task_cache_dir: str) -> str:
    """
    Generate a project-specific cache filename based on the project's name or ID.
    """
    safe_name = project.name.replace(" ", "_").lower()
    return os.path.join(task_cache_dir, f"{safe_name}_tasks.json")


async def save_tasks_to_json(tasks: list[Task], project: WebProject, task_cache_dir: str) -> bool:
    """
    Save tasks to a project-specific JSON file.
    """
    filename = get_cache_filename(project, task_cache_dir)
    try:
        cache_data = {"project_id": project.id, "project_name": project.name, "timestamp": datetime.now().isoformat(), "tasks": [task.serialize() for task in tasks]}

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


async def generate_tasks_for_project(demo_project: WebProject, use_cached_tasks: bool, task_cache_dir: str, prompts_per_url: int, num_of_urls: int, prompts_per_use_case: int = 1) -> list[Task]:
    """
    Generate tasks for the given demo project, possibly using cached tasks.
    """
    if use_cached_tasks:
        cached_tasks = await load_tasks_from_json(demo_project, task_cache_dir)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for '{demo_project.name}', generating new tasks...")

    config = TaskGenerationConfig(save_task_in_db=False, prompts_per_url=prompts_per_url, num_of_urls=num_of_urls, prompts_per_use_case=prompts_per_use_case)

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    tasks = await pipeline.generate()

    if tasks:
        await save_tasks_to_json(tasks, demo_project, task_cache_dir)

    return tasks


async def add_tests_to_tasks(tasks: list[Task], demo_project: WebProject, task_cache_dir: str) -> list[Task]:
    """
    Ensure each Task has test cases; if not present, generate them.
    """
    missing_tests = any(not getattr(t, "tests", None) for t in tasks)
    if missing_tests:
        print("Adding test cases to tasks...")
        llm_service = DIContainer.llm_service()
        test_pipeline = LocalTestGenerationPipeline(llm_service=llm_service, web_project=demo_project)
        tasks_with_tests = await test_pipeline.add_tests_to_tasks(tasks)

        if tasks_with_tests:
            await save_tasks_to_json(tasks_with_tests, demo_project, task_cache_dir)
            return tasks_with_tests
        else:
            return tasks
    else:
        print("All tasks already have test cases.")
        return tasks
