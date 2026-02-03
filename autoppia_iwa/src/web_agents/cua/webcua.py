from __future__ import annotations

from typing import Any, Awaitable, List, Optional, Protocol, runtime_checkable

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


class StepResult(Protocol):
    score: ScoreDetails
    snapshot: BrowserSnapshot
    action_result: Optional[ActionExecutionResult]


@runtime_checkable
class AsyncWebCUASession(Protocol):
    """
    Async interface for a step-wise browser + backend session over Autoppia tasks.
    """

    async def reset(self) -> StepResult:
        ...

    async def step(self, action: Optional[BaseAction]) -> StepResult:
        ...

    async def get_score_details(self) -> ScoreDetails:
        ...

    async def close(self) -> None:
        ...

    async def run_with_timeout(self, awaitable: Awaitable[Any], timeout_s: float) -> Any:
        ...

    @property
    def page(self) -> Page:
        ...

    @property
    def history(self) -> List[ActionExecutionResult]:
        ...


@runtime_checkable
class SyncWebCUASession(Protocol):
    """
    Sync wrapper interface around a WebCUA session, suitable for RL envs.
    """

    def reset(self) -> StepResult:
        ...

    def step(self, action: Optional[BaseAction]) -> StepResult:
        ...

    def get_score_details(self) -> ScoreDetails:
        ...

    def get_partial_score(self) -> ScoreDetails:
        ...

    def execute_action(self, action: BaseAction) -> StepResult:
        ...

    def run_with_timeout(self, awaitable: Awaitable[Any], timeout_s: float) -> Any:
        ...

    def close(self) -> None:
        ...

    @property
    def page(self) -> Page:
        ...

    @property
    def history(self) -> List[ActionExecutionResult]:
        ...


__all__ = [
    "AsyncWebCUASession",
    "SyncWebCUASession",
    "ScoreDetails",
    "BrowserSnapshot",
    "StepResult",
]

