import asyncio
import json
import unittest
from typing import List, Optional

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.application.tests.test_generation_pipeline import TestGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects
from autoppia_iwa.src.di_container import DIContainer
from autoppia_iwa.src.shared.visualizator import SubnetVisualizer, visualize_task
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from tests import test_container

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

TASKS_PARENT_DIR = PROJECT_BASE_DIR.parent / "tests/data_generation"
OUTPUT_DIR = TASKS_PARENT_DIR / "results"
TASKS_CACHE_DIR = TASKS_PARENT_DIR / "tasks_cache"

# Ensure cache directory exists
TASKS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

USE_CACHED_TASKS = True
NUMBER_OF_TASKS = 3

visualizer = SubnetVisualizer()

# ============================================================
# TASK CACHING FUNCTIONS
# ============================================================


@visualize_task(visualizer)
async def add_tests_to_tasks(tasks: List[Task], test_pipeline: TestGenerationPipeline) -> List[Task]:
    """
    Adds tests to the generated tasks and visualizes them.

    Args:
        tasks: List of tasks to add tests to.
        test_pipeline: Pipeline for test generation.

    Returns:
        List of tasks with added tests.
    """
    print(f"Generating tests for {len(tasks)} tasks...")
    return await test_pipeline.add_tests_to_tasks(tasks)


async def load_tasks_from_json(project: WebProject) -> Optional[List[Task]]:
    """
    Loads tasks from a project-specific JSON file if available and valid.
    """
    filename = TASKS_CACHE_DIR / f"{project.name.replace(' ', '_').lower()}_tasks.json"
    if not filename.is_file():
        print(f"Cache file {filename} not found for project '{project.name}'")
        return None

    try:
        with filename.open() as f:
            cache_data = json.load(f)

        if cache_data.get("project_id") != project.id and cache_data.get("project_name") != project.name:
            print(f"Cache file exists but for a different project. Expected '{project.name}', found '{cache_data.get('project_name')}'")
            return None

        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks", [])]
        print(f"Loaded {len(tasks)} tasks for project '{project.name}' from {filename}")
        return tasks[0:NUMBER_OF_TASKS]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Cache loading error for '{project.name}': {e}")
        return None


# ============================================================
# TASK AND TEST GENERATION FUNCTIONS
# ============================================================


async def generate_tasks_for_project(demo_project: WebProject, num_of_urls: int = 3) -> List[Task]:
    """
    Generates tasks for the given demo project.
    If USE_CACHED_TASKS is True, attempts to load from the project-specific cache first.

    Args:
        demo_project: The web project for which to generate tasks.
        num_of_urls: Number of URLs to include in task generation.

    Returns:
        List of Task objects.
    """
    if USE_CACHED_TASKS:
        cached_tasks = await load_tasks_from_json(demo_project)
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for project '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for project '{demo_project.name}', generating new tasks...")

    config = TaskGenerationConfig(
        save_web_analysis_in_db=True,
        save_task_in_db=False,
        number_of_prompts_per_task=1,
        num_or_urls=num_of_urls,
    )

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    task_results = await pipeline.generate()
    test_pipeline = TestGenerationPipeline(llm_service=DIContainer.llm_service(), web_project=demo_project)
    tasks_with_tests = await add_tests_to_tasks(task_results.tasks, test_pipeline)
    return tasks_with_tests


class TestNewActionsGeneration(unittest.TestCase):
    """
    Unit tests for generating new actions based on task configurations.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up shared resources for all tests in the class.
        """
        # Initialize the application bootstrap and LLM service
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.web_agent: ApifiedWebAgent = test_container.web_agent()
        web_project = asyncio.run(initialize_demo_webs_projects())
        # Create the task configuration
        cls.tasks = asyncio.run(generate_tasks_for_project(web_project))

    def test_new_actions_generation(self):
        """Test that actions are generated correctly from a goal and URL."""
        for task in self.tasks:
            # Generate actions using the configured task
            task_solution = self.web_agent.solve_task_sync(task=task)

            # Assertions
            self.assertTrue(task_solution, "No task solution were generated.")
            self.assertTrue(task_solution.actions, "No actions were generated. The action list is empty.")

            # Debugging output (optional)
            print(f"Generated {len(task_solution.actions)} actions:")
            for idx, action in enumerate(task_solution.actions, start=1):
                print(f"{idx}: {repr(action)}")


if __name__ == "__main__":
    unittest.main()
