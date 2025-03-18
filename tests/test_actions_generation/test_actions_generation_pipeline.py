import json
import unittest

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from tests.test_di_container import TestDIContainer

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

TASKS_CACHE_DIR = PROJECT_BASE_DIR.parent / "tests/jobs_demo_website_tasks.json"

USE_CACHED_TASKS = True
NUMBER_OF_TASKS = 1


def load_tasks_from_json() -> list[Task] | None:
    """
    Loads tasks from a project-specific JSON file if available and valid.
    """
    try:
        with TASKS_CACHE_DIR.open() as f:
            cache_data = json.load(f)
        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks_with_tests", [])]
        print(f"Loaded {len(tasks)} tasks...")
        return tasks[0:NUMBER_OF_TASKS]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Cache loading error': {e}")
        return None


# ============================================================
# TASK AND TEST GENERATION FUNCTIONS
# ============================================================


async def generate_tasks_for_project(demo_project: WebProject) -> list[Task]:
    """
    Generates tasks for the given demo project.
    If USE_CACHED_TASKS is True, attempts to load from the project-specific cache first.

    Args:
        demo_project: The web project for which to generate tasks.

    Returns:
        List of Task objects.
    """
    if USE_CACHED_TASKS:
        if NUMBER_OF_TASKS > 5:
            raise ValueError("Select any number between 1 and 5.")
        cached_tasks = load_tasks_from_json()
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for project '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for project '{demo_project.name}', generating new tasks...")

    config = TaskGenerationConfig(save_task_in_db=False, num_of_urls=1, random_urls=False, prompts_per_url=NUMBER_OF_TASKS)

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    return await pipeline.generate()


class TestActionsGeneration(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for generating new actions based on task configurations.
    """

    async def asyncSetUp(self):
        """
        Set up shared resources for all tests in the class.
        """
        # Initialize the application bootstrap and LLM service
        self.app_bootstrap = AppBootstrap()
        self.llm_service = self.app_bootstrap.container.llm_service()
        web_project = (await initialize_demo_webs_projects(demo_web_projects))[0]

        # Create the task configuration
        self.tasks = await generate_tasks_for_project(web_project)

    async def test_new_actions_generation(self):
        """Test that actions are generated correctly from a goal and URL."""

        for task in self.tasks:
            # Generate actions using the configured task
            web_agent: ApifiedWebAgent = TestDIContainer().web_agent()

            task_solution = web_agent.solve_task_sync(task=task)

            # Assertions
            self.assertTrue(task_solution, "No task solution were generated.")
            self.assertTrue(task_solution.actions, "No actions were generated. The action list is empty.")

            # Debugging output (optional)
            print(f"Generated {len(task_solution.actions)} actions:")
            for idx, action in enumerate(task_solution.actions, start=1):
                print(f"{idx}: {action!r}")


if __name__ == "__main__":
    unittest.main()
