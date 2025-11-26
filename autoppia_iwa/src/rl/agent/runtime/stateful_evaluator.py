from __future__ import annotations

"""
StatefulEvaluator: envoltorio síncrono y minimalista para evaluar acciones
una a una en un navegador real, acumulando historial y score parcial tras
cada paso usando la misma lógica de tests que el ConcurrentEvaluator.

Diseño:
- Mantiene un Playwright browser/context/page vivos durante el episodio.
- Ejecuta acciones BaseAction con PlaywrightBrowserExecutor para registrar
  snapshots y resultados homogéneos.
- Expone get_partial_score() que corre tests globales sobre eventos backend
  acumulados hasta el momento, devolviendo raw_score y banderas.

Nota: Internamente usa asyncio.run(...) para operar con la API async.
"""

import asyncio
import contextlib
import os
from dataclasses import dataclass, field

from loguru import logger
from playwright.async_api import async_playwright

from autoppia_iwa.config.config import EVALUATOR_HEADLESS
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.demo_webs.demo_webs_service import BackendDemoWebService
from autoppia_iwa.src.evaluation.evaluator.utils import run_partial_tests
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult


@dataclass
class PartialScore:
    raw_score: float = 0.0
    tests_passed: int = 0
    total_tests: int = 0
    success: bool = False


@dataclass
class StatefulEvaluator:
    task: Task
    web_agent_id: str = "rl-env"
    should_record_gif: bool = False

    # Runtime
    _playwright: any = field(default=None, init=False, repr=False)
    _browser: any = field(default=None, init=False, repr=False)
    _context: any = field(default=None, init=False, repr=False)
    _page: any = field(default=None, init=False, repr=False)
    _backend: BackendDemoWebService | None = field(default=None, init=False, repr=False)
    _project: any = field(default=None, init=False, repr=False)
    _executor: PlaywrightBrowserExecutor | None = field(default=None, init=False, repr=False)
    _history: list[ActionExecutionResult] = field(default_factory=list, init=False, repr=False)
    _loop: asyncio.AbstractEventLoop | None = field(default=None, init=False, repr=False)

    # -----------------------------
    # Lifecycle (sync wrappers)
    # -----------------------------
    def _ensure_loop(self) -> None:
        if self._loop is None or getattr(self._loop, "is_closed", lambda: False)():
            self._loop = asyncio.new_event_loop()

    def _run(self, awaitable):
        assert self._loop is not None
        return self._loop.run_until_complete(awaitable)

    def run(self, awaitable):
        self._ensure_loop()
        return self._run(awaitable)

    def run_with_timeout(self, awaitable, timeout_s: float):
        self._ensure_loop()
        return self._run(asyncio.wait_for(awaitable, timeout_s))

    def reset(self) -> None:
        self._ensure_loop()
        logger.info("SE.reset: start")
        self._run(self._reset_async())

    def execute_action(self, action: BaseAction) -> ActionExecutionResult:
        self._ensure_loop()
        logger.info(f"SE.exec: action={type(action).__name__} i={len(self._history)}")
        return self._run(self._execute_action_async(action))

    def get_partial_score(self) -> PartialScore:
        self._ensure_loop()
        return self._run(self._partial_score_async())

    def close(self) -> None:
        if self._loop is None:
            return
        try:
            self._run(self._close_async())
        finally:
            with contextlib.suppress(Exception):
                self._loop.close()
            self._loop = None

    # -----------------------------
    # Async impl
    # -----------------------------
    async def _reset_async(self) -> None:
        # Cerrar si ya hay sesión
        await self._close_async()

        # Resolver WebProject a partir de la Task
        project = None
        try:
            if getattr(self.task, "web_project_id", None):
                pid = str(self.task.web_project_id)
                for p in demo_web_projects:
                    if getattr(p, "id", None) == pid:
                        project = p
                        break
        except Exception:
            project = None

        # Reset DB backend y lanzar navegador (sin fallback/mocks)
        if project is None:
            raise RuntimeError("No se pudo resolver el WebProject desde la Task (web_project_id ausente o inválido)")
        self._project = project
        self._backend = BackendDemoWebService(web_project=project)
        # No ocultar errores de reset: si no hay endpoint o falla, que la ejecución falle
        logger.info("SE.reset: resetting backend")
        await self._backend.reset_database()
        logger.info("SE.reset: backend reset done")

        logger.info("SE.reset: launching browser")
        self._playwright = await async_playwright().start()
        specs = self.task.specifications or BrowserSpecification()
        self._browser = await self._playwright.chromium.launch(headless=EVALUATOR_HEADLESS, args=[f"--window-size={specs.screen_width},{specs.screen_height}"])
        # Propagate both agent and validator headers for demo webs instrumentation
        validator_id = os.getenv("VALIDATOR_ID", "validator_001")
        self._context = await self._browser.new_context(
            no_viewport=True,
            extra_http_headers={
                "X-WebAgent-Id": self.web_agent_id,
                "X-Validator-Id": validator_id,
            },
        )
        with contextlib.suppress(Exception):
            self._context.set_default_timeout(10_000)
        self._page = await self._context.new_page()

        # Executor homogéneo con tus snapshots
        self._executor = PlaywrightBrowserExecutor(specs, self._page, self._backend)
        self._history.clear()

        # Navegar a la URL inicial
        nav = NavigateAction(url=self.task.url)
        logger.info(f"SE.reset: navigating to {self.task.url}")
        res = await self._executor.execute_single_action(nav, self.web_agent_id, iteration=0, is_web_real=self.task.is_web_real, should_record=self.should_record_gif)
        self._history.append(res)

    async def _execute_action_async(self, action: BaseAction) -> ActionExecutionResult:
        if not self._executor:
            raise RuntimeError("Evaluator not initialized. Call reset() first.")
        idx = len(self._history)
        try:
            res = await asyncio.wait_for(
                self._executor.execute_single_action(
                    action,
                    self.web_agent_id,
                    iteration=idx,
                    is_web_real=self.task.is_web_real,
                    should_record=self.should_record_gif,
                ),
                timeout=15,
            )
        except TimeoutError:
            logger.warning("SE.exec: timeout waiting execute_single_action")
            # In a timeout, try to capture a minimal snapshot state to keep rolling
            try:
                if self._page:
                    await self._page.content()
                    # url read without await; playwright property
                    getattr(self._page, "url", "")
                else:
                    _html, _url = "", ""
            except Exception:
                _html, _url = "", ""
            # Return a minimal failed result
            res = ActionExecutionResult(
                successfully_executed=False,
                error="timeout",
                action=action,
                browser_snapshot=None,
                execution_time=0.0,
            )
        self._history.append(res)
        return res

    async def _partial_score_async(self) -> PartialScore:
        # Ejecutar tests parciales sobre el historial y tomar la última fila
        if not self._project:
            return PartialScore()
        matrix = await run_partial_tests(self._project, self.task, self._history)
        if not matrix:
            return PartialScore()
        last = matrix[-1] if matrix else []
        passed = sum(1 for r in last if getattr(r, "success", False))
        total = len(last)
        raw = (passed / total) if total > 0 else 0.0
        return PartialScore(raw_score=raw, tests_passed=passed, total_tests=total, success=(total > 0 and passed == total))

    async def _close_async(self) -> None:
        # Cerrar recursos en orden
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

    # -----------------------------
    # Exposición de la Page para BrowserManager
    # -----------------------------
    @property
    def page(self):  # type: ignore[override]
        return self._page

    @property
    def history(self) -> list[ActionExecutionResult]:
        return list(self._history)
