import unittest
from datetime import datetime

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.tests_classes import BaseTaskTest, OpinionBaseOnHTML
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.execution.actions.base import Selector
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestHtmlModelDump(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize resources for the test class."""
        cls.app = AppBootstrap()
        cls.llm_service = cls.app.container.llm_service()
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

    def test_html_model_dump(self):
        """
        Test the `model_dump` method to ensure it behaves as expected.
        """
        try:
            result = self.test_instance.model_dump()

            # Check if the method returns a non-empty result (adjust based on expected behavior)
            self.assertIsNotNone(result, "model_dump() returned None")
            self.assertIsInstance(result, dict, "model_dump() did not return a dictionary")
            self.assertGreater(len(result), 0, "model_dump() returned an empty dictionary")

            # Attempt to rebuild the test from the dumped model
            rebuilt_tests = BaseTaskTest.assign_tests([result])
            self.assertEqual(len(rebuilt_tests), 1, "assign_tests() did not rebuild a single test instance")
            self.assertIsInstance(rebuilt_tests[0], OpinionBaseOnHTML, "Rebuilt instance is not of type OpinionBaseOnHTML")

        except Exception as e:
            self.fail(f"model_dump() raised an unexpected exception: {e}")

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests are run."""
        cls.app = None
        cls.llm_service = None


if __name__ == "__main__":
    unittest.main()
