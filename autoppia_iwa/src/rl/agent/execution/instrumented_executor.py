from __future__ import annotations

import base64
import difflib
from datetime import datetime
from typing import Any

from playwright.async_api import Page

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult

from ..instrumentation.js_events import JsEventCollector
from .snapshots import InstrumentedBrowserSnapshot


class InstrumentedBrowserExecutor:
    """Playwright executor that records DOM/html plus runtime JS events per action."""

    def __init__(
        self,
        browser_config: BrowserSpecification,
        page: Page | None = None,
        backend_demo_webs_service: BackendDemoWebService | None = None,
        capture_screenshots: bool = False,
    ) -> None:
        self.browser_config = browser_config
        self.page: Page | None = page
        self.backend_demo_webs_service = backend_demo_webs_service
        self.capture_screenshots = capture_screenshots
        self._collector = JsEventCollector(page) if page else None

    async def execute_single_action(
        self,
        action: BaseAction,
        web_agent_id: str,
        iteration: int,
        is_web_real: bool,
        should_record: bool = False,
    ) -> ActionExecutionResult:
        if not self.page:
            raise RuntimeError("Playwright page is not initialized.")

        collector = self._collector
        if collector:
            collector.rollover()

        try:
            backend_events_before = await self._fetch_backend_events(is_web_real, web_agent_id)
            snapshot_before = await self._capture_snapshot(include_screenshot=should_record or self.capture_screenshots)
            start_time = datetime.now()
            await action.execute(self.page, self.backend_demo_webs_service, web_agent_id)
            execution_time = (datetime.now() - start_time).total_seconds()

            await self.page.wait_for_load_state("domcontentloaded")
            snapshot_after = await self._capture_snapshot(include_screenshot=should_record or self.capture_screenshots)
            backend_events_after = await self._fetch_backend_events(is_web_real, web_agent_id)
            js_events = collector.flush() if collector else []

            html_diff = difflib.unified_diff(
                (snapshot_before.get("html") or "").splitlines(),
                (snapshot_after.get("html") or "").splitlines(),
                lineterm="",
            )
            diff_text = "\n".join(list(html_diff)[:200])  # cap diff size

            browser_snapshot = InstrumentedBrowserSnapshot(
                iteration=iteration,
                action=action,
                prev_html=snapshot_before.get("html", ""),
                current_html=snapshot_after.get("html", ""),
                backend_events=backend_events_after,
                backend_events_before=backend_events_before,
                html_diff=diff_text or None,
                timestamp=datetime.now(),
                current_url=snapshot_after.get("url", ""),
                screenshot_before=snapshot_before.get("screenshot", ""),
                screenshot_after=snapshot_after.get("screenshot", ""),
                js_events=js_events,
            )

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                successfully_executed=True,
                execution_time=execution_time,
                browser_snapshot=browser_snapshot,
                action=action,
                error=None,
            )

        except Exception as exc:
            backend_events_before = await self._fetch_backend_events(is_web_real, web_agent_id)
            snapshot_error = await self._capture_snapshot(include_screenshot=False)
            backend_events_after = await self._fetch_backend_events(is_web_real, web_agent_id)
            js_events = collector.flush() if collector else []

            html_diff = difflib.unified_diff(
                (snapshot_before.get("html") or "").splitlines(),
                (snapshot_error.get("html") or "").splitlines(),
                lineterm="",
            )
            diff_text = "\n".join(list(html_diff)[:200])

            browser_snapshot = InstrumentedBrowserSnapshot(
                iteration=iteration,
                action=action,
                prev_html=snapshot_error.get("html", ""),
                current_html=snapshot_error.get("html", ""),
                backend_events=backend_events_after,
                backend_events_before=backend_events_before,
                html_diff=diff_text or None,
                timestamp=datetime.now(),
                current_url=snapshot_error.get("url", ""),
                screenshot_before=snapshot_error.get("screenshot", ""),
                screenshot_after=snapshot_error.get("screenshot", ""),
                js_events=js_events,
            )

            return ActionExecutionResult(
                action_event=action.__class__.__name__,
                action=action,
                successfully_executed=False,
                error=str(exc),
                execution_time=0,
                browser_snapshot=browser_snapshot,
            )

    async def _fetch_backend_events(self, is_web_real: bool, web_agent_id: str):
        if not self.backend_demo_webs_service or is_web_real:
            return []
        try:
            return await self.backend_demo_webs_service.get_backend_events(web_agent_id)
        except Exception:
            return []

    async def _capture_snapshot(self, include_screenshot: bool) -> dict[str, Any]:
        if not self.page:
            return {"html": "", "screenshot": "", "url": ""}
        try:
            html = await self.page.content()
            screenshot_data = ""
            if include_screenshot:
                screenshot = await self.page.screenshot(type="jpeg", full_page=False, quality=70)
                screenshot_data = base64.b64encode(screenshot).decode("utf-8")
            return {"html": html, "screenshot": screenshot_data, "url": self.page.url}
        except Exception as exc:
            return {"html": "", "screenshot": "", "url": getattr(self.page, "url", ""), "error": str(exc)}
