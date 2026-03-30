from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, Protocol, runtime_checkable

from playwright.async_api import Page

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class ScoreDetails(Protocol):
    raw_score: float
    tests_passed: int
    total_tests: int
    success: bool


class BrowserSnapshot(Protocol):
    html: str
    url: str
    screenshot: bytes | None


class StepResult(Protocol):
    score: ScoreDetails
    snapshot: BrowserSnapshot
    action_result: ActionExecutionResult | None


@runtime_checkable
class AsyncTaskExecutionSession(Protocol):
    """Async interface for a step-wise browser + backend session over one task execution."""

    async def reset(self) -> StepResult: ...

    async def step(self, action: BaseAction | None) -> StepResult: ...

    async def get_score_details(self) -> ScoreDetails: ...

    async def close(self) -> None: ...

    async def run_with_timeout(self, awaitable: Awaitable[Any], timeout_s: float) -> Any: ...

    @property
    def page(self) -> Page: ...

    @property
    def history(self) -> list[ActionExecutionResult]: ...


TaskExecutionSessionProtocol = AsyncTaskExecutionSession
AsyncWebAgentSession = AsyncTaskExecutionSession
WebAgentSession = AsyncTaskExecutionSession

__all__ = [
    "AsyncTaskExecutionSession",
    "AsyncWebAgentSession",
    "BrowserSnapshot",
    "ScoreDetails",
    "StepResult",
    "TaskExecutionSessionProtocol",
    "WebAgentSession",
]
