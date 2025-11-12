import argparse
import os
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from autoppia_iwa.entrypoints.benchmark.task_generation import (
    generate_tasks_for_project,
    get_projects_by_ids,
)
from autoppia_iwa.src.demo_webs.config import demo_web_projects

# =====================
# Constants / Settings
# =====================
DEFAULT_PORT: int = 5080
DEFAULT_HOST: str = "0.0.0.0"

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
    num_use_cases: int = Field(0, description="Number of use cases to include (0 = all)")
    selective_use_cases: list[str] = Field(default_factory=list, description="List of specific use cases to include")
    runs: int = Field(1, description="Number of runs for each task generation")
    dynamic: list[str] = Field(default_factory=list, description="Array of dynamic features: v1 (assign seed), v2 (future), v3 (assign seed structure). Can select any combination.")


# =====================
# Endpoint
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
                use_cached=False,
                cache_dir="",
                prompts_per_use_case=config.prompts_per_use_case,
                num_use_cases=config.num_use_cases,
                use_cases=config.selective_use_cases if config.selective_use_cases else None,
                dynamic=config.dynamic if config.dynamic else None,
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
    parser = argparse.ArgumentParser(description="Run the Task Generation API server.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the server on")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Host to bind the server to")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level=os.getenv("UVICORN_LOG_LEVEL", "info"))


if __name__ == "__main__":
    main()
