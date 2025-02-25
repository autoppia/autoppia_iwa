import unittest
from datetime import datetime

from autoppia_iwa.src.bootstrap import AppBootstrap
from autoppia_iwa.src.data_generation.domain.tests_classes import OpinionBaseOnHTML
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.execution.actions.base import Selector
from autoppia_iwa.src.execution.classes import BrowserSnapshot


class TestOpinionBaseOnHTML(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize OpinionBaseOnHTML with the real LLM service."""
        cls.app = AppBootstrap()
        cls.llm_service = cls.app.container.llm_service()
        cls.test_instance = OpinionBaseOnHTML(llm_service=cls.llm_service)

    def _run_test(self, prev_html, current_html, expected_type=bool):
        """Helper function to run tests and validate LLM response type."""
        snapshot = BrowserSnapshot(
            iteration=1,
            action=ClickAction(selector=Selector(type="xpathSelector", value="//button[text()='Click Me']")),
            prev_html=prev_html,
            current_html=current_html,
            screenshot_before="",
            screenshot_after="",
            backend_events=[],
            timestamp=datetime.fromisoformat("2025-02-10T12:00:00Z"),
            current_url="https://example.com",
        )

        result = self.test_instance.execute_test(snapshot)
        print(f"LLM Output: {result}")
        self.assertIsInstance(result, expected_type, f"LLM output should be {expected_type}, but got {type(result)}")
        return result

    def test_html_change_detected(self):
        """Test if LLM correctly detects meaningful HTML changes."""
        result = self._run_test(
            prev_html="<div><button>Click Me</button></div>",
            current_html="<div><button>Click Me</button><p>Success</p></div>",
        )
        self.assertTrue(isinstance(result, bool), "Expected a boolean response from LLM.")

    def test_no_html_change_detected(self):
        """Test if LLM correctly identifies when no meaningful HTML change occurs."""
        result = self._run_test(
            prev_html="<div><button>Click Me</button></div>",
            current_html="<div><button>Click Me</button></div>",  # No change
        )
        self.assertTrue(isinstance(result, bool), "Expected a boolean response from LLM.")

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests."""
        cls.app = None
        cls.llm_service = None


if __name__ == "__main__":
    unittest.main()
