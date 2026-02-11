"""
Unified task generation module with both API endpoint and CLI capabilities.
Usage as API: python -m autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint
Usage as CLI: python -m autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint --cli
"""

import argparse
import asyncio
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import (
    generate_tasks_for_project,
    get_projects_by_ids,
    save_tasks_to_json,
)
from autoppia_iwa.src.demo_webs.config import demo_web_projects

# =====================
# Constants / Settings
# =====================
DEFAULT_PORT: int = 5080
DEFAULT_HOST: str = "0.0.0.0"

# CLI Configuration
PROJECT_ID = "autobooks"  # Web 1 autocinema
USE_CASE_NAMES = ["SEARCH_BOOK"]  # List of use case names, or None for all use cases
NUM_TASKS = 2
DYNAMIC = True  # Set to False if you don't want dynamic seeds

# Cache directory (same as benchmark uses)
CACHE_DIR = str(PROJECT_BASE_DIR.parent / "benchmark-output" / "cache" / "tasks")

router = APIRouter()


# =====================
# Dataclass / Model
# =====================
class GenerateTaskConfig(BaseModel):
    """
    Configuration model for task generation.
    """

    projects: list[str] = Field(..., description="List of project IDs to generate tasks for")
    prompts_per_use_case: int = Field(1, description="Number of prompts per use case")
    selective_use_cases: list[str] = Field(
        default_factory=list,
        description="List of specific use cases to include. If empty, uses all available use cases.",
    )
    runs: int = Field(1, description="Number of runs for each task generation")
    dynamic: bool = Field(False, description="If True, tasks will include random seeds for dynamic content generation")


# =====================
# API Endpoint
# =====================
@router.post("/generate-tasks")
async def generate_tasks(config: GenerateTaskConfig) -> Any:
    """
    Generate benchmark tasks for the given projects.
    """

    # Get project objects based on the provided IDs
    web_projects = get_projects_by_ids(demo_web_projects, config.projects)

    all_results = {}

    for run_index in range(1, config.runs + 1):
        print(f"▶️ Run {run_index}/{config.runs}")

        # Generate tasks per project
        for project in web_projects:
            tasks = await generate_tasks_for_project(
                project=project,
                prompts_per_use_case=config.prompts_per_use_case,
                use_cases=config.selective_use_cases if config.selective_use_cases else None,
                dynamic=config.dynamic,
            )

            # Initialize project entry if not already present
            if project.id not in all_results:
                all_results[project.id] = {}

            # Group and merge prompts by use case name
            for task in tasks:
                use_case = task.use_case.name
                prompt = task.prompt

                # Initialize use case if not present
                if use_case not in all_results[project.id]:
                    all_results[project.id][use_case] = []

                # Append the new prompt
                all_results[project.id][use_case].append(prompt)

    # ✅ Final formatted result
    final_result = []
    for project_id, usecases in all_results.items():
        final_result.append({"project_id": project_id, "tasks": usecases})

    return {"generated_tasks": final_result}


# =====================
# CLI Mode
# =====================
async def cli_main():
    """Generate tasks for one or more use cases and save to JSON (CLI mode)."""
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
    tasks = await generate_tasks_for_project(
        project=project,
        prompts_per_use_case=NUM_TASKS,
        use_cases=USE_CASE_NAMES,
        dynamic=DYNAMIC,
    )

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


# =====================
# App Initialization
# =====================
app = FastAPI(
    title="Task Generation API",
    description="API to generate benchmark tasks for demo web projects.",
    version="1.0.0",
)

app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# Main Entrypoint
# =====================
def main():
    parser = argparse.ArgumentParser(description="Run the Task Generation API server or CLI mode.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the server on")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Host to bind the server to")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode (generate tasks using constants and save to files, then exit)",
    )
    args = parser.parse_args()

    if args.cli:
        # CLI mode: generate and save tasks using constants
        asyncio.run(cli_main())
    else:
        # API mode: start FastAPI server
        uvicorn.run(app, host=args.host, port=args.port, log_level=os.getenv("UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
