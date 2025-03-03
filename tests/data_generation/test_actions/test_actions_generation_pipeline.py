import unittest

from autoppia_iwa.config.config import PROJECT_BASE_DIR
from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.demo_webs.config import initialize_demo_webs_projects
from autoppia_iwa.src.shared.entrypoints.tasks import generate_tasks_for_project
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
from tests import test_container


class TestActionsGeneration(unittest.IsolatedAsyncioTestCase):
    """
    Unit tests for generating new actions based on task configurations.
    """

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

    @classmethod
    async def asyncSetUpClass(cls):
        """
        Set up shared resources for all tests in the class.
        """
        # Initialize the application bootstrap and LLM service
        cls.app_bootstrap = AppBootstrap()
        cls.llm_service = cls.app_bootstrap.container.llm_service()
        cls.web_agent: ApifiedWebAgent = test_container.web_agent()
        web_project = await initialize_demo_webs_projects()

        # Create the task configuration
        cls.tasks = await generate_tasks_for_project(web_project, cls.USE_CACHED_TASKS, cls.TASKS_CACHE_DIR, 1, 3)

    async def test_new_actions_generation(self):
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
