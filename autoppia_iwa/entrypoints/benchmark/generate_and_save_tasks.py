"""
Script to generate tasks for one or more use cases and save them to JSON.
Usage: python -m autoppia_iwa.entrypoints.benchmark.generate_and_save_tasks
Set USE_CASE_NAMES to a list of use case names, or None to generate for all use cases.
"""

import asyncio
from pathlib import Path

from loguru import logger

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids
from autoppia_iwa.entrypoints.benchmark.utils.tasks import save_tasks_to_json
from autoppia_iwa.src.data_generation.tasks.classes import TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.demo_webs.config import demo_web_projects

# Configuration
PROJECT_ID = "autobooks"  # Web 1 autocinema
USE_CASE_NAMES = ["SEARCH_BOOK"]  # List of use case names, or None for all use cases
NUM_TASKS = 2
DYNAMIC = True  # Set to False if you don't want dynamic seeds

# Cache directory (same as benchmark uses)
CACHE_DIR = str(PROJECT_BASE_DIR.parent / "benchmark-output" / "cache" / "tasks")


async def main():
    """Generate tasks for one or more use cases and save to JSON."""
    # Get project
    projects = get_projects_by_ids(demo_web_projects, [PROJECT_ID])
    if not projects:
        logger.error(f"Project '{PROJECT_ID}' not found")
        return

    project = projects[0]

    # Log which use cases we're generating for
    if USE_CASE_NAMES is None:
        logger.info(f"Generating {NUM_TASKS} tasks for ALL use cases in project '{project.name}'")
    else:
        logger.info(f"Generating {NUM_TASKS} tasks for {len(USE_CASE_NAMES)} use case(s): {USE_CASE_NAMES} in project '{project.name}'")

    # Create cache directory
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)

    # Generate tasks
    config = TaskGenerationConfig(
        prompts_per_use_case=NUM_TASKS,
        use_cases=USE_CASE_NAMES,  # Pass the list directly, not wrapped in another list
        dynamic=DYNAMIC,
    )

    pipeline = TaskGenerationPipeline(web_project=project, config=config)
    tasks = await pipeline.generate()

    if not tasks:
        logger.error("No tasks generated")
        return

    # Filter tasks for the specific use cases (if USE_CASE_NAMES is provided)
    filtered_tasks = [task for task in tasks if task.use_case and task.use_case.name in USE_CASE_NAMES] if USE_CASE_NAMES is not None else tasks

    if not filtered_tasks:
        if USE_CASE_NAMES:
            logger.warning(f"No tasks found for use cases: {USE_CASE_NAMES}")
        else:
            logger.warning("No tasks found")
        return

    # Log summary by use case
    from collections import defaultdict

    tasks_by_use_case = defaultdict(list)
    for task in filtered_tasks:
        if task.use_case:
            tasks_by_use_case[task.use_case.name].append(task)

    logger.info(f"Generated {len(filtered_tasks)} total tasks:")
    for uc_name, uc_tasks in sorted(tasks_by_use_case.items()):
        logger.info(f"  - {uc_name}: {len(uc_tasks)} tasks")

    # Save to JSON
    success = await save_tasks_to_json(filtered_tasks, project, CACHE_DIR)

    if success:
        logger.info(f"✅ Successfully saved {len(filtered_tasks)} tasks to cache")
        logger.info(f"Cache location: {CACHE_DIR}")
    else:
        logger.error("Failed to save tasks to cache")


if __name__ == "__main__":
    asyncio.run(main())
