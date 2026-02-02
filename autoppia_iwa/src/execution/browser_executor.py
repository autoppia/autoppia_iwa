import asyncio
import base64
from datetime import datetime

from playwright.async_api import Page

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
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

    async def execute_single_action(self, action: BaseAction, web_agent_id: str, iteration: int, is_web_real: bool, should_record: bool = False) -> ActionExecutionResult:
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
            await self._before_action(action, iteration)

            # Capture state before action execution
            if should_record:
                snapshot_before = await self._capture_snapshot()
            else:
                snapshot_before = {"html": "", "screenshot": "", "url": "", "error": ""}
            start_time = datetime.now()

            # Execute the action
            await action.execute(self.page, self.backend_demo_webs_service, web_agent_id)
            execution_time = (datetime.now() - start_time).total_seconds()

            # Capture backend events and updated browser state
            await self.page.wait_for_load_state("domcontentloaded")
            await self._after_action(action, iteration)

            # backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            # Always capture URL/HTML for tests; only include screenshot if recording is enabled
            if should_record:
                snapshot_after = await self._capture_snapshot()
            else:
                html = await self.page.content()
                snapshot_after = {"html": html, "screenshot": "", "url": self.page.url, "error": ""}

            # Fetch backend events (for demo webs) if available, with a short retry
            # loop to allow the backend service to flush events.
            backend_events = []
            if self.backend_demo_webs_service and not is_web_real:
                for _ in range(3):
                    try:
                        backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)
                    except Exception:
                        backend_events = []
                    if backend_events:
                        break
                    await asyncio.sleep(0.2)

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
                error=None,
            )

        except Exception as e:
            await self._on_action_error(action, iteration, e)
            # backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            if should_record:
                snapshot_error = await self._capture_snapshot()
            else:
                # Capture minimal state for debugging/tests
                try:
                    html = await self.page.content()
                except Exception:
                    html = ""
                url = ""
                try:
                    url = self.page.url
                except Exception:
                    url = ""
                snapshot_error = {"html": html, "screenshot": "", "url": url, "error": str(e)}

            # Fetch backend events (best-effort) on error as well, with retries.
            backend_events = []
            if self.backend_demo_webs_service and not is_web_real:
                for _ in range(3):
                    try:
                        backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)
                    except Exception:
                        backend_events = []
                    if backend_events:
                        break
                    await asyncio.sleep(0.2)

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

    async def _before_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed right before each action. Subclasses can override to inject dynamic behavior.
        """
        return None

    async def _after_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed after action execution (and after DOMContentLoaded) but before snapshots.
        """
        return None

    async def _on_action_error(self, action: BaseAction, iteration: int, error: Exception) -> None:
        """
        Hook executed when an action fails. Subclasses may perform cleanup or reporting.
        """
        return None
