from __future__ import annotations

"""
Async-first stateful evaluator for Autoppia IWA tasks.

This module provides:
- AsyncStatefulEvaluator: async WebCUA-compatible session over a single Task.
- StatefulEvaluator: sync wrapper around AsyncStatefulEvaluator for PPO/RL envs.
"""

import asyncio
import contextlib
import os
from dataclasses import dataclass
from typing import Any

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS, VALIDATOR_ID
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.shared.utils import run_partial_tests
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import replace_credentials_in_action
from autoppia_iwa.src.web_agents.cua import AsyncWebCUASession, SyncWebCUASession


@dataclass
class ScoreDetails:
    raw_score: float = 0.0
    tests_passed: int = 0
    total_tests: int = 0
    success: bool = False


@dataclass
class BrowserSnapshot:
    html: str
    url: str
    screenshot: bytes | None = None


@dataclass
class StepResult:
    score: ScoreDetails
    snapshot: BrowserSnapshot
    action_result: ActionExecutionResult | None = None


@dataclass
class EvaluatorConfig:
    """
    Lightweight configuration for StatefulEvaluator behaviour.
    """

    action_timeout_s: float = 15.0
    page_default_timeout_ms: int = 10_000


class AsyncStatefulEvaluator(AsyncWebCUASession):
    """
    Async WebCUA-compatible session for a single Task.
    """

    def __init__(
        self,
        task: Task,
        web_agent_id: str = "autoppia-rl-env",
        should_record_gif: bool = False,
        capture_screenshot: bool = False,
        config: EvaluatorConfig | None = None,
    ) -> None:
        self.task = task
        self.web_agent_id = web_agent_id
        self.should_record_gif = should_record_gif
        self.capture_screenshot = capture_screenshot
        self.config = config or EvaluatorConfig()

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._backend: BackendDemoWebService | None = None
        self._project: WebProject | None = None
        self._executor: PlaywrightBrowserExecutor | None = None
        self._history: list[ActionExecutionResult] = []

    async def reset(self) -> StepResult:
        logger.info("[AsyncStatefulEvaluator] reset start")
        await self._close_async()
        await self._init_async()

        nav = NavigateAction(url=self.task.url)
        logger.info(f"[AsyncStatefulEvaluator] navigate {self.task.url}")
        res = await self._executor.execute_single_action(  # type: ignore[union-attr]
            nav,
            self.web_agent_id,
            iteration=0,
            is_web_real=self.task.is_web_real,
            should_record=self.should_record_gif,
        )
        self._history.clear()
        self._history.append(res)

        score = await self._score_async()
        snapshot = await self._snapshot_async()
        return StepResult(score=score, snapshot=snapshot, action_result=res)

    async def step(self, action: BaseAction | None) -> StepResult:
        logger.info(
            "[AsyncStatefulEvaluator] step action={} i={}",
            type(action).__name__ if action is not None else "NOOP",
            len(self._history),
        )
        return await self._step_async(action)

    async def get_score_details(self) -> ScoreDetails:
        return await self._score_async()

    async def close(self) -> None:
        await self._close_async()

    async def run_with_timeout(self, awaitable: Any, timeout_s: float) -> Any:
        return await asyncio.wait_for(awaitable, timeout_s)

    async def _init_async(self) -> None:
        project: WebProject | None = None
        try:
            if getattr(self.task, "web_project_id", None):
                pid = str(self.task.web_project_id)
                for p in demo_web_projects:
                    if getattr(p, "id", None) == pid:
                        project = p
                        break
        except Exception:
            project = None

        if project is None:
            raise RuntimeError("AsyncStatefulEvaluator: could not resolve WebProject from Task")
        self._project = project

        self._backend = BackendDemoWebService(web_project=project, web_agent_id=self.web_agent_id)
        logger.info("[AsyncStatefulEvaluator] reset backend")
        await self._backend.reset_database()
        logger.info("[AsyncStatefulEvaluator] backend ok")

        logger.info("[AsyncStatefulEvaluator] launching browser")
        self._playwright = await async_playwright().start()
        specs = self.task.specifications or BrowserSpecification()
        self._browser = await self._playwright.chromium.launch(
            headless=EVALUATOR_HEADLESS,
            args=[f"--window-size={specs.screen_width},{specs.screen_height}"],
        )
        validator_id = VALIDATOR_ID or os.getenv("VALIDATOR_ID", "validator_001")
        self._context = await self._browser.new_context(
            no_viewport=True,
            extra_http_headers={
                "X-WebAgent-Id": self.web_agent_id,
                "X-Validator-Id": validator_id,
            },
        )
        with contextlib.suppress(Exception):
            self._context.set_default_timeout(self.config.page_default_timeout_ms)
        self._page = await self._context.new_page()

        self._executor = PlaywrightBrowserExecutor(specs, self._page, self._backend)

    async def _step_async(self, action: BaseAction | None) -> StepResult:
        action_result: ActionExecutionResult | None = None
        if action is not None:
            if not self._executor:
                raise RuntimeError("AsyncStatefulEvaluator: not initialized. Call reset() first.")
            replace_credentials_in_action(action, self.web_agent_id)
            idx = len(self._history)
            try:
                action_result = await asyncio.wait_for(
                    self._executor.execute_single_action(
                        action,
                        self.web_agent_id,
                        iteration=idx,
                        is_web_real=self.task.is_web_real,
                        should_record=self.should_record_gif,
                    ),
                    timeout=self.config.action_timeout_s,
                )
            except TimeoutError:
                logger.warning("[AsyncStatefulEvaluator] execute timeout")
                action_result = ActionExecutionResult(
                    successfully_executed=False,
                    error="timeout",
                    action=action,
                    browser_snapshot=None,
                    execution_time=0.0,
                )
            self._history.append(action_result)

        score = await self._score_async()
        snapshot = await self._snapshot_async()
        return StepResult(score=score, snapshot=snapshot, action_result=action_result)

    async def _score_async(self) -> ScoreDetails:
        if not self._project:
            return ScoreDetails()
        matrix = await run_partial_tests(self._project, self.task, self._history)
        if not matrix:
            return ScoreDetails()
        last = matrix[-1] if matrix else []
        passed = sum(1 for r in last if getattr(r, "success", False))
        total = len(last)
        raw = (passed / total) if total > 0 else 0.0
        return ScoreDetails(
            raw_score=raw,
            tests_passed=passed,
            total_tests=total,
            success=(total > 0 and passed == total),
        )

    async def _snapshot_async(self) -> BrowserSnapshot:
        if not self._page:
            return BrowserSnapshot(html="", url="", screenshot=None)
        html = await self._page.content()
        url = self._page.url
        screenshot = None
        if self.capture_screenshot:
            try:
                screenshot = await self._page.screenshot(full_page=True)
            except Exception as e:
                logger.warning(f"[AsyncStatefulEvaluator] screenshot failed: {e}")
        return BrowserSnapshot(html=html, url=url, screenshot=screenshot)

    async def _close_async(self) -> None:
        try:
            if self._context:
                await self._context.close()
        finally:
            self._context = None

        try:
            if self._browser:
                await self._browser.close()
        finally:
            self._browser = None

        try:
            if self._playwright:
                await self._playwright.stop()
        finally:
            self._playwright = None

        try:
            if self._backend:
                await self._backend.close()
        finally:
            self._backend = None

    @property
    def page(self):
        return self._page

    @property
    def history(self) -> list[ActionExecutionResult]:
        return list(self._history)


class StatefulEvaluator(SyncWebCUASession):
    """
    Sync wrapper around AsyncStatefulEvaluator for PPO/RL envs and non-async callers.
    """

    def __init__(
        self,
        task: Task,
        web_agent_id: str = "autoppia-rl-env",
        should_record_gif: bool = False,
        capture_screenshot: bool = False,
        config: EvaluatorConfig | None = None,
    ) -> None:
        self._async = AsyncStatefulEvaluator(
            task=task,
            web_agent_id=web_agent_id,
            should_record_gif=should_record_gif,
            capture_screenshot=capture_screenshot,
            config=config,
        )
        self._loop: asyncio.AbstractEventLoop | None = None

    def __enter__(self) -> StatefulEvaluator:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _ensure_loop(self) -> None:
        if self._loop is None or getattr(self._loop, "is_closed", lambda: False)():
            self._loop = asyncio.new_event_loop()

    def _run(self, awaitable: Any) -> Any:
        assert self._loop is not None
        return self._loop.run_until_complete(awaitable)

    def run_with_timeout(self, awaitable: Any, timeout_s: float) -> Any:
        self._ensure_loop()
        return self._run(asyncio.wait_for(awaitable, timeout_s))

    def reset(self) -> StepResult:
        self._ensure_loop()
        logger.info("[StatefulEvaluator] reset start")
        return self._run(self._async.reset())

    def step(self, action: BaseAction | None) -> StepResult:
        self._ensure_loop()
        logger.info(
            "[StatefulEvaluator] step action={} i={}",
            type(action).__name__ if action is not None else "NOOP",
            len(self.history),
        )
        return self._run(self._async.step(action))

    def get_score_details(self) -> ScoreDetails:
        self._ensure_loop()
        return self._run(self._async.get_score_details())

    def get_partial_score(self) -> ScoreDetails:
        return self.get_score_details()

    def execute_action(self, action: BaseAction) -> StepResult:
        return self.step(action)

    def close(self) -> None:
        if self._loop is None:
            return
        try:
            self._run(self._async.close())
        finally:
            with contextlib.suppress(Exception):
                self._loop.close()
            self._loop = None

    @property
    def page(self):
        return self._async.page

    @property
    def history(self) -> list[ActionExecutionResult]:
        return self._async.history


__all__ = [
    "AsyncStatefulEvaluator",
    "BrowserSnapshot",
    "EvaluatorConfig",
    "ScoreDetails",
    "StatefulEvaluator",
    "StepResult",
]
