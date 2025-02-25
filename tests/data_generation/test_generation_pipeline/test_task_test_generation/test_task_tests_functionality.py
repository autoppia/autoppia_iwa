import unittest
from datetime import datetime

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest, CheckEventEmittedTest, CheckPageViewEventTest, FindInHtmlTest, OpinionBaseOnHTML, OpinionBaseOnScreenshot
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.execution.actions.base import Selector
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestTaskFunctionality(unittest.TestCase):
    """Unit tests for task test assignment and HTML model dumping."""

    @classmethod
    def setUpClass(cls):
        """Initialize shared test dependencies."""
        cls.app = AppBootstrap()
        cls.llm_service = cls.app.container.llm_service()

        # Mock browser snapshot
        cls.test_snapshot = BrowserSnapshot(
            iteration=1,
            action=ClickAction(selector=Selector(type="xpathSelector", value="//button[text()='Click Me']")),
            prev_html="<div><button>Click Me</button></div>",
            current_html="<div><button>Click Me</button><p>Success</p></div>",
            screenshot_before="",
            screenshot_after="",
            backend_events=[],
            timestamp=datetime.fromisoformat("2025-02-10T12:00:00Z"),
            current_url="https://example.com",
        )

        cls.test_instance = OpinionBaseOnHTML(llm_service=cls.llm_service)

    def test_assign_tests_valid_configs(self):
        """Test that `assign_tests` correctly assigns tests based on valid configurations."""
        test_configs = [
            {"test_type": "frontend", "keywords": ["example"]},
            {"test_type": "frontend", "name": "OpinionBaseOnHTML"},
            {"test_type": "frontend", "name": "OpinionBaseOnScreenshot", "task": "example task"},
            {"test_type": "backend", "page_view_url": "https://example.com"},
            {"test_type": "backend", "event_name": "test_event"},
        ]

        assigned_tests = BaseTaskTest.assign_tests(test_configs)

        self.assertEqual(len(assigned_tests), 5, "Incorrect number of tests assigned")
        self.assertIsInstance(assigned_tests[0], FindInHtmlTest, "Test 1 is not FindInHtmlTest")
        self.assertIsInstance(assigned_tests[1], OpinionBaseOnHTML, "Test 2 is not OpinionBaseOnHTML")
        self.assertIsInstance(assigned_tests[2], OpinionBaseOnScreenshot, "Test 3 is not OpinionBaseOnScreenshot")
        self.assertIsInstance(assigned_tests[3], CheckPageViewEventTest, "Test 4 is not CheckPageViewEventTest")
        self.assertIsInstance(assigned_tests[4], CheckEventEmittedTest, "Test 5 is not CheckEventEmittedTest")

    def test_assign_tests_invalid_config(self):
        """Test that `assign_tests` raises a ValueError for unsupported configurations."""
        invalid_config = [{"test_type": "unknown", "name": "InvalidTest"}]

        with self.assertRaises(ValueError, msg="assign_tests did not raise ValueError for invalid config"):
            BaseTaskTest.assign_tests(invalid_config)

    def test_html_model_dump(self):
        """Test the `model_dump` method and its ability to rebuild test instances."""
        try:
            result = self.test_instance.model_dump()
            self.assertIsInstance(result, dict, "model_dump() did not return a dictionary")
            self.assertGreater(len(result), 0, "model_dump() returned an empty dictionary")

            rebuilt_tests = BaseTaskTest.assign_tests([result])
            self.assertEqual(len(rebuilt_tests), 1, "assign_tests() did not rebuild a single test instance")
            self.assertIsInstance(rebuilt_tests[0], OpinionBaseOnHTML, "Rebuilt instance is not of type OpinionBaseOnHTML")

        except Exception as e:
            self.fail(f"model_dump() raised an unexpected exception: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests."""
        cls.app = None
        cls.llm_service = None


if __name__ == "__main__":
    unittest.main()
