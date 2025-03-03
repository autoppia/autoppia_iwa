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

# ============================================================
# TASK CACHING FUNCTIONS
# ============================================================


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
        num_or_urls=num_of_urls,
    )

    print(f"Generating tasks for {demo_project.name}...")
    pipeline = TaskGenerationPipeline(web_project=demo_project, config=config)
    return await pipeline.generate()


# ============================================================
# UNIT TESTS
# ============================================================


class TestTaskTestGenerationWithWebAnalysis(unittest.IsolatedAsyncioTestCase):
    LOCAL_PAGE_URL = "http://localhost:8000/"
    EXAMPLE_URL = "https://example.com/"

    async def asyncSetUp(self) -> None:
        """Initialize test environment."""
        self.app_bootstrap = AppBootstrap()
        self.llm_service = self.app_bootstrap.container.llm_service()

    async def _generate_tests_for_web_project(self, url: str) -> List[Task]:
        """Helper method to generate tasks and test cases."""
        web_project = await initialize_demo_webs_projects()
        tasks = await generate_tasks_for_project(web_project[0])

        test_generator = TestGenerationPipeline(web_project=web_project[0], llm_service=self.llm_service)
        tasks_with_tests = await test_generator.add_tests_to_tasks(tasks=tasks)

        self.assertIsInstance(tasks_with_tests, list, "Tasks with tests should be a list.")
        self.assertGreater(len(tasks_with_tests), 0, "At least one task should be generated.")
        return tasks_with_tests

    async def test_task_test_generation_for_local_web(self) -> None:
        """Test generating task-based tests for a local web application."""
        tasks_with_tests = await self._generate_tests_for_web_project(url=self.LOCAL_PAGE_URL)
        self.assertTrue(tasks_with_tests, "No tasks generated for local web.")

    async def test_task_test_generation_for_real_web_example(self) -> None:
        """Test generating task-based tests for a real web application."""
        tasks_with_tests = await self._generate_tests_for_web_project(url=self.EXAMPLE_URL)
        self.assertTrue(tasks_with_tests, "No tasks generated for real web.")


if __name__ == "__main__":
    unittest.main()
