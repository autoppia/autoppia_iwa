"""Data schemas for reward-model pipeline.

These mirror the evaluation artefacts emitted by the Autoppia IWA runtime while
remaining self-contained so the reward-model package can operate without
importing the full evaluation stack.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class BackendEvent(BaseModel):
    """Minimal representation of a backend event captured during evaluation."""

    event_name: str = Field(..., description="Identifier of the backend event")
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: float | str | None = Field(default=None, description="Event timestamp (seconds or ISO string)")


class BaseAction(BaseModel):
    """Simplified action description."""

    kind: str
    args: dict[str, Any] = Field(default_factory=dict)


class BrowserSnapshot(BaseModel):
    """Snapshot of the browser state before and after executing an action."""

    iteration: int
    action: BaseAction
    prev_html: str
    current_html: str
    screenshot_before: str | None = None
    screenshot_after: str | None = None
    backend_events: list[BackendEvent] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    current_url: str

    def public_dump(self) -> dict[str, Any]:
        """Return observation-friendly content (no privileged assets)."""

        return {
            "iteration": self.iteration,
            "current_url": self.current_url,
            "current_html": self.current_html,
        }


class ActionExecutionResult(BaseModel):
    """Result wrapper for an executed action."""

    action: BaseAction
    action_event: str
    successfully_executed: bool
    error: str | None = None
    execution_time: float | None = None
    browser_snapshot: BrowserSnapshot


class TestResult(BaseModel):
    name: str
    passed: bool
    details: dict[str, Any] = Field(default_factory=dict)


class EvaluationStep(BaseModel):
    index: int
    action_result: ActionExecutionResult
    tests: list[TestResult] = Field(default_factory=list)


class EvaluationEpisode(BaseModel):
    episode_id: str
    project_id: str | None = None
    task_id: str | None = None
    steps: list[EvaluationStep]
    final_score: float


class SemanticLabel(BaseModel):
    page_type: str
    goal_progress: float = Field(ge=0.0, le=1.0)
    affordances: dict[str, bool] = Field(default_factory=dict)
    salient_entities: list[str] = Field(default_factory=list)
    is_on_wrong_product: bool | None = None


class ObsPublic(BaseModel):
    url_tokens: list[str]
    dom_excerpt: str
    dyn: dict[str, float]
    action_prev: str | None = None


class ObsAugmented(BaseModel):
    public: ObsPublic
    semantic: SemanticLabel
