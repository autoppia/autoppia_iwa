import asyncio
import base64
import contextlib
import json
from datetime import UTC, datetime
from typing import Any

from playwright.async_api import Error as PlaywrightError, Page, TimeoutError as PWTimeout

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot


def _parse_event_timestamp(event: Any) -> datetime | None:
    """
    Parse timestamp from a backend event dict.
    Supports top-level "timestamp" or legacy "data.timestamp".
    Returns datetime in UTC or None if missing/invalid.
    """
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
    except (ValueError, TypeError):
        return None


def _minimal_snapshot(html: str = "", url: str = "", error: str = "") -> dict[str, str]:
    """Build a minimal snapshot dict (no screenshot) for lightweight recording paths."""
    return {"html": html, "screenshot": "", "url": url, "error": error}


def _action_execution_exception_types():
    """Exception types caught during action execution (Sonar duplication fix)."""
    return (AssertionError, PlaywrightError, PWTimeout, RuntimeError, ValueError, TypeError)


_SUPPRESS_PLAYWRIGHT = (PlaywrightError, PWTimeout, RuntimeError)
_NON_NAVIGATING_ACTIONS = {
    "TypeAction",
    "SelectAction",
    "SelectDropDownOptionAction",
    "HoverAction",
    "ExtractAction",
    "EvaluateAction",
    "ScreenshotAction",
    "MouseMoveAction",
    "MouseDownAction",
    "MouseUpAction",
    "HoldKeyAction",
    "SendKeysIWAAction",
}
_STABILIZE_LOAD_STATE_TIMEOUT_MS = 1200


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

    @staticmethod
    def _normalize_action_output(value: Any) -> Any:
        if value is None or isinstance(value, str | int | float | bool):
            return value
        if isinstance(value, list):
            return [PlaywrightBrowserExecutor._normalize_action_output(item) for item in value]
        if isinstance(value, dict):
            return {str(key): PlaywrightBrowserExecutor._normalize_action_output(item) for key, item in value.items()}
        try:
            json.dumps(value)
            return value
        except Exception:
            return str(value)

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
            await self._before_action(action, iteration)

            # Capture state before action execution
            if should_record:
                snapshot_before = await self._capture_snapshot()
            else:
                snapshot_before = _minimal_snapshot()
            # Execute the action
            action_output = await action.execute(self.page, self.backend_demo_webs_service, web_agent_id)
            execution_time = (datetime.now(UTC) - start_time).total_seconds()

            # Capture backend events and updated browser state. Do not force
            # text-entry and other non-navigation actions through a full
            # navigation-style load wait.
            await self._stabilize_after_action(action)
            await self._after_action(action, iteration)

            # backend_events = await self._get_backend_events(web_agent_id, is_web_real)
            if should_record:
                snapshot_after = await self._capture_snapshot()
            else:
                snapshot_after = await self._get_minimal_snapshot_from_page()

            backend_events = await self._get_backend_events_for_action(web_agent_id, start_time, is_web_real)

            if not should_record:
                snapshot_after = await self._get_minimal_snapshot_from_page()

            browser_snapshot = BrowserSnapshot(
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

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                successfully_executed=True,
                action_output=self._normalize_action_output(action_output),
                execution_time=execution_time,
                browser_snapshot=browser_snapshot,
                action=action,
                error=None,
            )

        except _action_execution_exception_types() as e:
            await self._on_action_error(action, iteration, e)
            if should_record:
                snapshot_error = await self._capture_snapshot()
            else:
                snapshot_error = await self._get_minimal_snapshot_from_page(error=str(e))

            backend_events = await self._get_backend_events_for_action(web_agent_id, start_time, is_web_real)

            # Create error snapshot
            browser_snapshot = BrowserSnapshot(
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

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                action=action,
                successfully_executed=False,
                error=str(e),
                action_output=None,
                execution_time=0,
                browser_snapshot=browser_snapshot,
            )

    async def _fetch_backend_events_filtered(self, web_agent_id: str, start_time: datetime) -> list[Any]:
        """
        Fetch backend events with retries.

        Keep full scoped event history for the current web_agent/validator and
        let evaluator-side scoring apply recency pruning for the active step.
        This avoids dropping valid events that are emitted asynchronously after
        the action has already completed.
        """
        backend_events: list[Any] = []
        for _ in range(3):
            try:
                backend_events = await self.backend_demo_webs_service.get_backend_events(web_agent_id)
            except (RuntimeError, ConnectionError, TimeoutError):
                backend_events = []
            if backend_events:
                break
            await asyncio.sleep(0.2)
        return backend_events or []

    async def _get_backend_events_for_action(self, web_agent_id: str, start_time: datetime, is_web_real: bool) -> list[Any]:
        """Fetch backend events for this action or return empty list (centralizes duplicate condition)."""
        if self.backend_demo_webs_service and not is_web_real:
            return await self._fetch_backend_events_filtered(web_agent_id, start_time)
        return []

    async def _get_minimal_snapshot_from_page(self, error: str = "") -> dict[str, str]:
        """Build minimal snapshot from current page state (html/url) with suppressed exceptions."""
        html, url = "", ""
        with contextlib.suppress(*_SUPPRESS_PLAYWRIGHT):
            html = await self.page.content()
        with contextlib.suppress(*_SUPPRESS_PLAYWRIGHT):
            url = self.page.url
        return _minimal_snapshot(html=html, url=url, error=error)

    async def _capture_snapshot(self) -> dict:
        """Helper function to capture browser state."""
        try:
            html = await self.page.content()
            screenshot = await self.page.screenshot(type="jpeg", full_page=False, quality=85)
            encoded_screenshot = base64.b64encode(screenshot).decode("utf-8")
            current_url = self.page.url
            return {"html": html, "screenshot": encoded_screenshot, "url": current_url}
        except (PlaywrightError, PWTimeout, RuntimeError, ValueError) as e:
            return _minimal_snapshot(error=str(e))

    async def _stabilize_after_action(self, action: BaseAction) -> None:
        if not self.page:
            return
        if type(action).__name__ in _NON_NAVIGATING_ACTIONS:
            return
        with contextlib.suppress(PWTimeout, PlaywrightError, RuntimeError):
            await self.page.wait_for_load_state(
                "domcontentloaded",
                timeout=_STABILIZE_LOAD_STATE_TIMEOUT_MS,
            )

    async def _before_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed right before each action. Subclasses can override to inject dynamic behavior.
        """
        # Intentionally empty - subclasses can override

    async def _after_action(self, action: BaseAction, iteration: int) -> None:
        """
        Hook executed after action execution (and after DOMContentLoaded) but before snapshots.
        """
        # Intentionally empty - subclasses can override

    async def _on_action_error(self, action: BaseAction, iteration: int, error: Exception) -> None:
        """
        Hook executed when an action fails. Subclasses may perform cleanup or reporting.
        """
        # Intentionally empty - subclasses can override
