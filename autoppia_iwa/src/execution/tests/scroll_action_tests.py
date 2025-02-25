import unittest
from unittest.mock import patch

from playwright.async_api import async_playwright

from autoppia_iwa.src.execution.actions.actions import ScrollAction


class TestScrollAction(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up Playwright and open a browser page for testing."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()

        # Navigate to a test page
        await self.page.goto("https://news.ycombinator.com/", timeout=60000)
        await self.page.wait_for_load_state("networkidle")

    async def asyncTearDown(self):
        """Close the browser after tests."""
        await self.browser.close()
        await self.playwright.stop()

    async def test_scroll_down(self):
        """Test scrolling down a fixed amount."""
        initial_scroll_y = await self.page.evaluate("window.scrollY")
        action = ScrollAction(down=True, value=500)
        await action.execute(self.page, backend_service=None, web_agent_id="agent_1")

        # Wait for the scroll to complete
        await self.page.wait_for_function("window.scrollY > 0")
        scroll_y = await self.page.evaluate("window.scrollY")

        self.assertGreater(scroll_y, initial_scroll_y, "Page should have scrolled down")

    # async def test_scroll_up(self):
    #     """Test scrolling up on the page."""
    #     initial_scroll_y = await self.page.evaluate("() => window.scrollY")
    #
    #     # Use ScrollAction instead of manual evaluation
    #     action = ScrollAction(up=True)
    #     await action.execute(self.page, backend_service=None, web_agent_id="agent_1")
    #
    #     # Wait until the page has scrolled up
    #     scroll_complete = await self.page.evaluate_handle("() => new Promise(resolve => { " "   requestAnimationFrame(() => setTimeout(() => resolve(window.scrollY), 100)); " "})")
    #     final_scroll_y = await scroll_complete.json_value()
    #
    #     self.assertLess(final_scroll_y, initial_scroll_y, "Page should have scrolled up")

    async def test_scroll_to_text_exists(self):
        """Test scrolling to a known text element."""
        action = ScrollAction(value="Hacker News")  # Ensure this text exists
        await action.execute(self.page, backend_service=None, web_agent_id="agent_1")

        element = self.page.get_by_text("Hacker News")
        is_visible = await element.is_visible()

        self.assertTrue(is_visible, "Page should have scrolled to the text element")
    #
    # async def test_scroll_to_text_not_exists(self):
    #     """Test scrolling to a text element that does not exist (should raise an error)."""
    #     action = ScrollAction(value="NonExistentText123")
    #
    #     with self.assertRaises(ValueError, msg="Expected ValueError for non-existent text"):
    #         await action.execute(self.page, backend_service=None, web_agent_id="agent_1")

    async def test_scroll_with_js_exception(self):
        """Test fallback scrolling when JavaScript fails."""
        action = ScrollAction(down=True, value="INVALID_JS")

        # Mock `evaluate` to simulate a JavaScript error
        with patch.object(self.page, "evaluate", side_effect=Exception("JavaScript error")):
            try:
                await action.execute(self.page, backend_service=None, web_agent_id="agent_1")
                success = True  # If fallback worked, test passes
            except Exception:
                success = False  # If it fails entirely, test fails

        self.assertTrue(success, "Should fall back to PageDown keyboard scroll on JS error")

    async def test_scroll_to_bottom(self):
        """Test scrolling to the bottom of the page."""
        initial_scroll_y = await self.page.evaluate("() => window.scrollY")
        # Use ScrollAction to scroll to the bottom
        action = ScrollAction(value="bottom")
        await action.execute(self.page, backend_service=None, web_agent_id="agent_1")

        # Wait for scroll completion using evaluate_handle() to avoid CSP issues
        scroll_complete = await self.page.evaluate_handle("() => new Promise(resolve => { " "   requestAnimationFrame(() => setTimeout(() => resolve(window.scrollY), 100)); " "})")
        final_scroll_y = await scroll_complete.json_value()

        self.assertGreater(final_scroll_y, initial_scroll_y, "Page should have scrolled to the bottom")


if __name__ == "__main__":
    unittest.main()
