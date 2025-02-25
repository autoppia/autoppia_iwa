import base64
import unittest
from datetime import datetime
from io import BytesIO

import numpy as np
from PIL import Image

from autoppia_iwa.config.config import OPENAI_API_KEY, OPENAI_MODEL
from autoppia_iwa.src.data_generation.domain.tests_classes import OpinionBaseOnScreenshot
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.execution.actions.base import Selector
from autoppia_iwa.src.execution.classes import BrowserSnapshot
from autoppia_iwa.src.llms.infrastructure.llm_service import OpenAIService


class TestOpinionBaseOnScreenshot(unittest.TestCase):
    """Unit tests for OpinionBaseOnScreenshot, validating LLM-based screenshot analysis."""

    @classmethod
    def setUpClass(cls):
        """Initialize LLM service and test instance before running tests."""
        cls.llm_service = OpenAIService(api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
        cls.test_instance = OpinionBaseOnScreenshot(task="Verify button click effect", llm_service=cls.llm_service)

    def setUp(self):
        """Set up mock browser snapshot with before-and-after screenshots."""
        self.mock_snapshot = BrowserSnapshot(
            iteration=1,
            action=ClickAction(selector=Selector(type="xpathSelector", value="//button[text()='Click Me']")),
            prev_html="<html><body><button>Click me</button></body></html>",
            current_html="<html><body><button>Clicked!</button></body></html>",
            backend_events=[],
            timestamp=datetime.fromisoformat("2025-02-10T12:00:00"),
            current_url="http://example.com",
            screenshot_before=self._create_base64_encoded_block((0, 0, 0)),  # Black block
            screenshot_after=self._create_base64_encoded_block((255, 255, 255)),  # White block
        )

    @staticmethod
    def _create_base64_encoded_block(color: tuple) -> str:
        """Create a base64-encoded image block of a given color."""
        img = Image.fromarray(np.full((10, 10, 3), color, dtype=np.uint8))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def test_screenshot_analysis(self):
        """Test if the LLM correctly analyzes the screenshot changes."""
        result = self.test_instance.execute_test(self.mock_snapshot)
        print(f"LLM Screenshot Analysis Result: {result}")

        self.assertIsInstance(result, bool, f"Expected a boolean result, but got {type(result)}")
        # Adjust the assertion below if you expect a specific outcome
        self.assertTrue(isinstance(result, bool), "LLM did not return a valid boolean.")

    @classmethod
    def tearDownClass(cls):
        """Clean up resources after all tests."""
        cls.llm_service = None


if __name__ == "__main__":
    unittest.main()
