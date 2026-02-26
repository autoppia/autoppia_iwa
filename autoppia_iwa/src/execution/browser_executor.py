import asyncio
import base64
import contextlib
from datetime import UTC, datetime
from typing import Any

from playwright.async_api import Page

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _parse_event_timestamp(event: Any) -> datetime | None:
    """Parse timestamp from backend event."""
    if not isinstance(event, dict):
        return None
    ts = event.get("timestamp")
    if not ts and isinstance(event.get("data"), dict):
        ts = event["data"].get("timestamp")
    if not isinstance(ts, str) or not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except Exception:
        return None


def _filter_events_by_timestamp(events: list[Any], start_time: datetime) -> list[Any]:
    """Filter out events that happened before start_time."""
    filtered: list[Any] = []
    for ev in events:
        ev_ts = _parse_event_timestamp(ev)
        if ev_ts is None or ev_ts >= start_time:
            filtered.append(ev)
    return filtered


# ============================================================================
# PLAYWRIGHT BROWSER EXECUTOR CLASS
# ============================================================================


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

    # ============================================================================
    # SNAPSHOT HELPERS
    # ============================================================================

    async def _capture_snapshot(self) -> dict:
        """Helper function to capture browser state."""
        try:
            html = await self.page.content()
            screenshot = await self.page.screenshot(type="jpeg", full_page=False, quality=85)
            encoded_screenshot = base64.b64encode(screenshot).decode("utf-8")
            current_url = self.page.url
            return {"html": html, "screenshot": encoded_screenshot, "url": current_url}
        except Exception as e:
            return {"html": "", "screenshot": "", "url": "", "error": str(e)}

    def _create_empty_snapshot(self) -> dict:
        """Create an empty snapshot dictionary."""
        return {"html": "", "screenshot": "", "url": "", "error": ""}

    async def _capture_minimal_snapshot(self) -> dict:
        """Capture minimal snapshot without screenshot."""
        html = ""
        url = ""
        with contextlib.suppress(Exception):
            html = await self.page.content()
        with contextlib.suppress(Exception):
            url = self.page.url
        return {"html": html, "screenshot": "", "url": url, "error": ""}

    async def _capture_snapshot_after_action(self, should_record: bool) -> dict:
        """Capture snapshot after action execution."""
        if should_record:
            return await self._capture_snapshot()
        html = await self.page.content()
        return {"html": html, "screenshot": "", "url": self.page.url, "error": ""}

    async def _update_snapshot_after_events(self, snapshot: dict) -> None:
        """Update snapshot HTML/URL after backend events polling."""
        with contextlib.suppress(Exception):
            snapshot["html"] = await self.page.content()
        with contextlib.suppress(Exception):
            snapshot["url"] = self.page.url

    # ============================================================================
    # BACKEND EVENTS HELPERS
    # ============================================================================

    async def _fetch_backend_events_with_retry(self, web_agent_id: str, max_retries: int = 3) -> list[Any]:
        """Fetch backend events with retry loop."""
        for _ in range(max_retries):
            try:
                events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)
                if events:
                    return events
            except Exception:
                pass
            await asyncio.sleep(0.2)
        return []

    async def _get_backend_events(self, web_agent_id: str, is_web_real: bool, start_time: datetime) -> list[Any]:
        """Get and filter backend events."""
        if not self.backend_demo_webs_service or is_web_real:
            return []
        events = await self._fetch_backend_events_with_retry(web_agent_id)
        return _filter_events_by_timestamp(events, start_time)

    # ============================================================================
    # BROWSER SNAPSHOT CREATION HELPERS
    # ============================================================================

    def _create_browser_snapshot(self, iteration: int, action: BaseAction, snapshot_before: dict, snapshot_after: dict, backend_events: list[Any]) -> BrowserSnapshot:
        """Create a BrowserSnapshot from snapshot dictionaries."""
        return BrowserSnapshot(
            iteration=iteration,
            action=action,
            prev_html=snapshot_before["html"],
            current_html=snapshot_after["html"],
            backend_events=backend_events,
            timestamp=datetime.now(UTC),
            current_url=snapshot_after["url"],
            screenshot_before=snapshot_before["screenshot"],
            screenshot_after=snapshot_after["screenshot"],
        )

    def _create_error_snapshot(self, snapshot_error: dict, backend_events: list[Any], iteration: int, action: BaseAction) -> BrowserSnapshot:
        """Create a BrowserSnapshot for error cases."""
        return BrowserSnapshot(
            iteration=iteration,
            action=action,
            prev_html=snapshot_error.get("html", ""),
            current_html=snapshot_error.get("html", ""),
            backend_events=backend_events,
            timestamp=datetime.now(UTC),
            current_url=snapshot_error.get("url", ""),
            screenshot_before=snapshot_error.get("screenshot", ""),
            screenshot_after=snapshot_error.get("screenshot", ""),
        )

    # ============================================================================
    # ACTION EXECUTION RESULT CREATION HELPERS
    # ============================================================================

    def _create_success_result(self, action: BaseAction, execution_time: float, browser_snapshot: BrowserSnapshot) -> ActionExecutionResult:
        """Create ActionExecutionResult for successful execution."""
        return ActionExecutionResult(
            action_event=action.__class__.__name__,
            successfully_executed=True,
            execution_time=execution_time,
            browser_snapshot=browser_snapshot,
            action=action,
            error=None,
        )

    def _create_error_result(self, action: BaseAction, error: Exception, browser_snapshot: BrowserSnapshot) -> ActionExecutionResult:
        """Create ActionExecutionResult for error cases."""
        return ActionExecutionResult(
            action_event=action.__class__.__name__,
            action=action,
            successfully_executed=False,
            error=str(error),
            execution_time=0,
            browser_snapshot=browser_snapshot,
        )

    # ============================================================================
    # ACTION EXECUTION FLOW HELPERS
    # ============================================================================

    async def _execute_action_flow(self, action: BaseAction, web_agent_id: str, iteration: int, should_record: bool, start_time: datetime) -> tuple[dict, dict, float]:
        """Execute action and capture snapshots. Returns (snapshot_before, snapshot_after, execution_time)."""
        await self._before_action(action, iteration)

        snapshot_before = await self._capture_snapshot() if should_record else self._create_empty_snapshot()

        await action.execute(self.page, self.backend_demo_webs_service, web_agent_id)
        execution_time = (datetime.now(UTC) - start_time).total_seconds()

        await self.page.wait_for_load_state("domcontentloaded")
        await self._after_action(action, iteration)

        snapshot_after = await self._capture_snapshot_after_action(should_record)
        return snapshot_before, snapshot_after, execution_time

    async def _handle_error_snapshot(self, error: Exception, should_record: bool) -> dict:
        """Create error snapshot."""
        if should_record:
            return await self._capture_snapshot()
        return await self._capture_minimal_snapshot()

    # ============================================================================
    # MAIN ACTION EXECUTION METHOD
    # ============================================================================

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

        start_time = datetime.now(UTC)

        try:
            snapshot_before, snapshot_after, execution_time = await self._execute_action_flow(action, web_agent_id, iteration, should_record, start_time)

            backend_events = await self._get_backend_events(web_agent_id, is_web_real, start_time)

            if not should_record:
                await self._update_snapshot_after_events(snapshot_after)

            browser_snapshot = self._create_browser_snapshot(iteration, action, snapshot_before, snapshot_after, backend_events)
            return self._create_success_result(action, execution_time, browser_snapshot)

        except Exception as e:
            await self._on_action_error(action, iteration, e)
            # backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            snapshot_error = await self._handle_error_snapshot(e, should_record)
            snapshot_error["error"] = str(e)

            backend_events = await self._get_backend_events(web_agent_id, is_web_real, start_time)

            browser_snapshot = self._create_error_snapshot(snapshot_error, backend_events, iteration, action)
            return self._create_error_result(action, e, browser_snapshot)

    # ============================================================================
    # HOOK METHODS (for subclasses to override)
    # ============================================================================

    async def _before_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed right before each action. Subclasses can override to inject dynamic behavior.
        """
        # Hook method - parameters may be used by subclasses
        _ = action, iteration
        await asyncio.sleep(0)  # Allow async override in subclasses

    async def _after_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed after action execution (and after DOMContentLoaded) but before snapshots.
        """
        # Hook method - parameters may be used by subclasses
        _ = action, iteration
        await asyncio.sleep(0)  # Allow async override in subclasses

    async def _on_action_error(self, action: BaseAction, iteration: int, error: Exception) -> None:
        """
        Hook executed when an action fails. Subclasses may perform cleanup or reporting.
        """
        # Hook method - parameters may be used by subclasses
        _ = action, iteration, error
        await asyncio.sleep(0)  # Allow async override in subclasses
