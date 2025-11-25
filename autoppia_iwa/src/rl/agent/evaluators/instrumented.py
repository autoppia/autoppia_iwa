from __future__ import annotations

from pathlib import Path
from loguru import logger
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

from autoppia_iwa.config.config import EVALUATOR_HEADLESS, VALIDATOR_ID
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.evaluator.evaluator import ConcurrentEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult
from autoppia_iwa.src.web_agents.classes import TaskSolution

from ..data.trace_writer import EvaluationTraceWriter
from ..execution.instrumented_executor import InstrumentedBrowserExecutor
from ..instrumentation.proxy_backend import ProxyBackendDemoWebService


class InstrumentationConfig(BaseModel):
    """Controls whether JS/DOM traces are persisted during evaluation."""

    enabled: bool = Field(default=True, description="If False, evaluator behaves like the stock version without logging")
    output_dir: Path = Field(default=Path("data/rm/raw_traces"), description="Directory to store JSONL traces")
    capture_screenshots: bool = Field(default=False, description="Capture base64 screenshots per action")
    force_proxy_backend: bool = Field(default=True, description="Route backend interactions through the webs_server proxy")


class JsInstrumentedEvaluator(ConcurrentEvaluator):
    """Concurrent evaluator variant that records JS runtime events for each action."""

    def __init__(self, web_project: WebProject, config: EvaluatorConfig, instrumentation: InstrumentationConfig | None = None):
        super().__init__(web_project, config)
        self._instrumentation = instrumentation or InstrumentationConfig()
        self._trace_writer = EvaluationTraceWriter(self._instrumentation.output_dir)
        if self._instrumentation.force_proxy_backend:
            self.backend_demo_webs_service = ProxyBackendDemoWebService(web_project=web_project)

    async def _evaluate_single_task_solution(self, task: Task, task_solution: TaskSolution):  # type: ignore[override]
        result = await super()._evaluate_single_task_solution(task, task_solution)
        if (
            self._instrumentation.enabled
            and result
            and result.execution_history
        ):
            try:
                self._trace_writer.write_episode(
                    self.web_project,
                    task,
                    task_solution.web_agent_id or "unknown",
                    result.execution_history,
                )
            except Exception as exc:  # pragma: no cover - logging only
                logger.warning("Failed to persist JS trace: %s", exc)
        return result

    async def _evaluate_in_browser(  # type: ignore[override]
        self,
        task: Task,
        web_agent_id: str,
        actions: list[BaseAction],
        is_web_real: bool,
    ) -> tuple[list[ActionExecutionResult], list[float]]:
        action_execution_times: list[float] = []
        action_results: list[ActionExecutionResult] = []

        async with async_playwright() as playwright:
            browser = None
            context = None
            try:
                specs = task.specifications or BrowserSpecification()
                browser = await playwright.chromium.launch(headless=EVALUATOR_HEADLESS, args=[f"--window-size={specs.screen_width},{specs.screen_height}"])
                context = await browser.new_context(
                    extra_http_headers={"X-WebAgent-Id": web_agent_id, "X-Validator-Id": VALIDATOR_ID},
                    no_viewport=True,
                )
                context.set_default_timeout(self.config.browser_timeout)
                page = await context.new_page()
                executor = InstrumentedBrowserExecutor(
                    browser_config=specs,
                    page=page,
                    backend_demo_webs_service=self.backend_demo_webs_service,
                    capture_screenshots=self._instrumentation.capture_screenshots,
                )

                for i, action in enumerate(actions):
                    start = self._time()
                    try:
                        result = await executor.execute_single_action(action, web_agent_id, iteration=i, is_web_real=is_web_real, should_record=self.config.should_record_gif)
                        action_results.append(result)
                        elapsed = self._time() - start
                        action_execution_times.append(elapsed)
                        self.action_type_timing[action.type].append(elapsed)
                        if i < len(actions) - 1 and self.config.task_delay_in_seconds > 0:
                            await self._sleep(self.config.task_delay_in_seconds)
                    except Exception as exc:
                        logger.warning("Instrumented action failed: %s", exc)
                        action_execution_times.append(self._time() - start)
                        break

                return action_results, action_execution_times
            finally:
                if context:
                    await context.close()
                if browser:
                    await browser.close()

    # Small indirections allow deterministic testing/mocking
    @staticmethod
    def _time() -> float:
        import time

        return time.time()

    @staticmethod
    async def _sleep(delay: float) -> None:
        import asyncio

        await asyncio.sleep(delay)
