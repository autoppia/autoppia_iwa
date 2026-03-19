from typing import Any, ClassVar, Literal

from loguru import logger
from pydantic import Field, model_validator

from ..base import BaseAction, Selector
from .helpers import _ensure_page, log_action


class WaitAction(BaseAction):
    """Waits for a specific condition: an element to appear or a fixed duration."""

    type: Literal["WaitAction"] = "WaitAction"
    browser_use_tool_name: ClassVar[str] = "wait"
    selector: Selector | None = Field(None, description="Selector for an element to wait for. If provided, waits for the element.")
    time_seconds: float | None = Field(None, description="Duration in seconds to wait. If provided without a selector, pauses execution.")
    timeout_seconds: float = Field(5.0, description="Maximum time in seconds to wait for the selector.")

    @model_validator(mode="before")
    @classmethod
    def check_wait_condition(cls, values):
        selector = values.get("selector")
        time_seconds = values.get("time_seconds")
        if selector is None and time_seconds is None:
            raise ValueError("WaitAction requires either 'selector' or 'time_seconds'.")
        if selector is not None and time_seconds is not None:
            logger.warning("Both 'selector' and 'time_seconds' provided for WaitAction. Selector will be prioritized for waiting, 'time_seconds' ignored.")
        return values

    @log_action("WaitAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "WaitAction")
        if self.selector:
            selector_str = self.selector.to_playwright_selector()
            timeout_ms = self.timeout_seconds * 1000
            await page.wait_for_selector(selector_str, state="visible", timeout=timeout_ms)
        elif self.time_seconds is not None:
            wait_ms = self.time_seconds * 1000
            await page.wait_for_timeout(wait_ms)
        else:
            raise ValueError("Invalid state: WaitAction has no condition.")
