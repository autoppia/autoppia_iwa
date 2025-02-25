import asyncio
import unittest

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.application.task_tests_generator import TaskTestGenerator
from autoppia_iwa.src.data_generation.domain.classes import WebProject
from autoppia_iwa.src.web_analysis.application.web_analysis_pipeline import WebAnalysisPipeline
from modules.webs_demo.web_1_demo_django_jobs.events.events import EVENTS_ALLOWED


class TestTaskTestGenerationWithWebAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Set up class-level test environment."""
        cls.app_bootstrap = AppBootstrap()
        cls.analysis_repo = cls.app_bootstrap.container.analysis_repository()
        cls.llm_service = cls.app_bootstrap.container.llm_service()

        # Local web testing setup
        cls.local_test_config = {
            "url": "http://localhost:8000/",
            "task_description": "Click on the Login button and then introduce your username and password.",
            "enable_crawl": False,
            "is_real_web": False,
        }

        # Real web testing setup
        cls.example_test_config = {
            "url": "https://example.com/",
            "task_description": "Navigate to the homepage and verify the page title.",
            "enable_crawl": False,
            "is_real_web": True,
        }

        cls.loop = asyncio.get_event_loop()

    async def _generate_tests_for_web_project(self, url: str, task_description: str, enable_crawl: bool, is_real_web: bool) -> list:
        """
        Helper method to perform web analysis and generate task-based tests.

        Args:
            url (str): The target web page URL.
            task_description (str): Description of the task to be tested.
            enable_crawl (bool): Whether to enable crawling.
            is_real_web (bool): Whether the project is a real web test.

        Returns:
            list: Generated task tests.
        """
        # Perform web analysis
        web_analysis_pipeline = WebAnalysisPipeline(start_url=url, analysis_repository=self.analysis_repo, llm_service=self.llm_service)
        web_analysis = await web_analysis_pipeline.analyze(enable_crawl=enable_crawl, save_results_in_db=True)

        self.assertIsNotNone(web_analysis, f"Web analysis should not return None for {url}.")
        self.assertTrue(hasattr(web_analysis, "analyzed_urls"), f"Web analysis result should contain 'analyzed_urls' for {url}.")

        # Initialize Web Project
        web_project = WebProject(
            backend_url=url,
            frontend_url=url,
            name="Example Project" if is_real_web else "Local Web App",
            events_to_check=EVENTS_ALLOWED,
            is_real_web=is_real_web,
        )

        # Generate task-based tests
        task_test_generator = TaskTestGenerator(web_project=web_project, web_analysis=web_analysis, llm_service=self.llm_service)
        tests = await task_test_generator.generate_task_tests(task_description, url)

        self.assertIsInstance(tests, list, "Generated tests should be a list.")
        self.assertGreater(len(tests), 0, f"No tests were generated for {url}.")

        print(f"Generated {len(tests)} tests for {url}")
        return tests

    def _run_async_test(self, test_config):
        """Helper to run async tests inside a synchronous test case."""
        return self.loop.run_until_complete(self._generate_tests_for_web_project(**test_config))

    def test_task_test_generation_for_local_web(self):
        """Test task test generation for a local web application."""
        tests = self._run_async_test(self.local_test_config)
        print(f"Generated Tests (Local Web): {tests}")

    def test_task_test_generation_for_real_web_example(self):
        """Test task test generation for a real web application."""
        tests = self._run_async_test(self.example_test_config)
        print(f"Generated Tests (Real Web): {tests}")

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up resources after tests."""
        cls.loop.close()


if __name__ == "__main__":
    unittest.main()
