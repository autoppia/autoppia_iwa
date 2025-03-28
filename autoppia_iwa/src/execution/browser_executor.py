import base64
from datetime import datetime

from playwright.async_api import Page

from autoppia_iwa.src.data_generation.domain.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot


class PlaywrightBrowserExecutor:
    def __init__(self, browser_config: BrowserSpecification, page: Page | None = None, backend_demo_webs_service: BackendDemoWebService = None):
        """
        Initializes the PlaywrightBrowserExecutor with a backend service and an optional Playwright page.

        Args:
            backend_demo_webs_service: Service for interacting with the backend.
            page: Optional Playwright page object.
        """
        self.browser_config = browser_config
        self.page: Page | None = page
        self.action_execution_results: list[ActionExecutionResult] = []
        self.backend_demo_webs_service: BackendDemoWebService = backend_demo_webs_service

    async def execute_single_action(self, action: BaseAction, web_agent_id: str, iteration: int, is_web_real: bool) -> ActionExecutionResult:
        """
        Executes a single action and records results, including browser snapshots.

        Args:
            action: The action to execute.
            web_agent_id: Identifier for the web agent.
            iteration: The iteration number of the action.

        Returns:
            ActionExecutionResult: The result of the action execution.
        """
        if not self.page:
            raise RuntimeError("Playwright page is not initialized.")

        try:
            # Capture state before action execution
            snapshot_before = await self._capture_snapshot()
            start_time = datetime.now()

            # Execute the action
            await action.execute(self.page, self.backend_demo_webs_service, web_agent_id)
            execution_time = (datetime.now() - start_time).total_seconds()

            # Capture backend events and updated browser state
            await self.page.wait_for_load_state("domcontentloaded")
            backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            snapshot_after = await self._capture_snapshot()

            # Create a detailed browser snapshot
            browser_snapshot = BrowserSnapshot(
                iteration=iteration,
                action=action,
                prev_html=snapshot_before["html"],
                current_html=snapshot_after["html"],
                backend_events=backend_events,
                timestamp=datetime.now(),
                current_url=snapshot_after["url"],
                screenshot_before=snapshot_before["screenshot"],
                screenshot_after=snapshot_after["screenshot"],
            )

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                successfully_executed=True,
                execution_time=execution_time,
                browser_snapshot=browser_snapshot,
                action=action,
            )

        except Exception as e:
            backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            snapshot_error = await self._capture_snapshot()

            # Create error snapshot
            browser_snapshot = BrowserSnapshot(
                iteration=iteration,
                action=action,
                prev_html=snapshot_error.get("html", ""),
                current_html=snapshot_error.get("html", ""),
                backend_events=backend_events,
                timestamp=datetime.now(),
                current_url=snapshot_error.get("url", ""),
                screenshot_before=snapshot_error.get("screenshot", ""),
                screenshot_after=snapshot_error.get("screenshot", ""),
            )

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                action=action,
                successfully_executed=False,
                error=str(e),
                execution_time=0,
                browser_snapshot=browser_snapshot,
            )

    async def _capture_snapshot(self) -> dict:
        """Helper function to capture browser state."""
        try:
            html = await self.page.content()
            screenshot = await self.page.screenshot(type="jpeg", full_page=False, quality=85)
            encoded_screenshot = base64.b64encode(screenshot).decode("utf-8")
            current_url = self.page.url
            return {"html": html, "screenshot": encoded_screenshot, "url": current_url}
        except Exception as e:
            # Gracefully handle any errors during snapshot
            return {"html": "", "screenshot": "", "url": "", "error": str(e)}

    async def _get_backend_events(self, web_agent_id: str, is_web_real: bool) -> list[BackendEvent]:
        if not is_web_real:
            return await self.backend_demo_webs_service.get_backend_events(web_agent_id)
        return []
