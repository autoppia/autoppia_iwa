from __future__ import annotations

from typing import Any, Protocol

from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.execution.browser_executor import PlaywrightBrowserExecutor
from autoppia_iwa.src.execution.classes import ActionExecutionResult


class RewardFn(Protocol):
    async def __call__(
        self,
        *,
        task: Any,
        step_idx: int,
        last_action_dict: dict[str, Any],
        last_action_obj: BaseAction | None,
        executor: PlaywrightBrowserExecutor,
        trajectory: list[dict[str, Any]],
        obs: dict[str, Any],
        result: ActionExecutionResult | None,
    ) -> tuple[float, bool, dict[str, Any]]: ...
