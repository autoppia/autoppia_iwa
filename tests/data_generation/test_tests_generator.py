import json
import unittest

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.tasks.local.tests.test_generation_pipeline import LocalTestGenerationPipeline
from autoppia_iwa.src.data_generation.application.tasks_generation_pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.domain.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.utils import initialize_demo_webs_projects

# ============================================================
# GLOBAL CONFIGURATION
# ============================================================

TASKS_CACHE_DIR = PROJECT_BASE_DIR.parent / "tests/jobs_demo_website_tasks.json"

USE_CACHED_TASKS: bool = True
NUMBER_OF_TASKS: int = 3
NUM_OF_URLS: int = 3
RANDOM_URLS: bool = False
# ============================================================
# TASK CACHING FUNCTIONS
# ============================================================


async def load_tasks_from_json() -> list[Task] | None:
    """
    Loads tasks from a project-specific JSON file if available and valid.
    """
    try:
        with TASKS_CACHE_DIR.open() as f:
            cache_data = json.load(f)
        tasks = [Task.deserialize(task_data) for task_data in cache_data.get("tasks_without_tests", [])]
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
        cached_tasks = await load_tasks_from_json()
        if cached_tasks and len(cached_tasks) > 0:
            print(f"Using {len(cached_tasks)} cached tasks for project '{demo_project.name}'")
            return cached_tasks
        else:
            print(f"No valid cached tasks found for project '{demo_project.name}', generating new tasks...")

    config = TaskGenerationConfig(
        save_task_in_db=False,
        num_of_urls=NUM_OF_URLS,
        random_urls=RANDOM_URLS,
    )

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    return await pipeline.generate()


# ============================================================
# UNIT TESTS
# ============================================================


class TestTaskTestGenerationWithWebAnalysis(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        """Initialize test environment."""
        self.app_bootstrap = AppBootstrap()
        self.llm_service = self.app_bootstrap.container.llm_service()

    async def _generate_tests_for_web_project(self) -> list[Task]:
        """Helper method to generate tasks and test cases."""
        web_project = await initialize_demo_webs_projects(demo_web_projects)
        tasks = await generate_tasks_for_project(web_project[0])

        test_generator = LocalTestGenerationPipeline(web_project=web_project[0], llm_service=self.llm_service)
        tasks_with_tests = await test_generator.add_tests_to_tasks(tasks=tasks)

        self.assertIsInstance(tasks_with_tests, list, "Tasks with tests should be a list.")
        self.assertGreater(len(tasks_with_tests), 0, "At least one task should be generated.")
        return tasks_with_tests

    async def test_task_test_generation_for_local_web(self) -> None:
        """Test generating task-based tests for a local web application."""
        tasks_with_tests = await self._generate_tests_for_web_project()
        self.assertTrue(tasks_with_tests, "No tasks generated for local web.")

        # for debugging
        for task in tasks_with_tests:
            print(task.tests)


if __name__ == "__main__":
    unittest.main()
