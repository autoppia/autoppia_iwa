from typing import Any, Literal

from pydantic import Field, model_validator

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class HoldKeyAction(BaseAction):
    """Hold a keyboard key down, optionally for a duration, and release it."""

    type: Literal["HoldKeyAction"] = "HoldKeyAction"
    key: str = Field(..., description="Keyboard key to hold/release. Use Playwright key names.")
    duration_ms: int | float | None = Field(None, description="Optional duration in ms to hold before releasing.")
    release: bool = Field(False, description="If true, only releases the key instead of pressing it.")

    @model_validator(mode="before")
    @classmethod
    def _validate_params(cls, values):
        key = values.get("key")
        if not key or not isinstance(key, str):
            raise ValueError("A valid 'key' string is required.")
        dur = values.get("duration_ms")
        rel = values.get("release", False)
        if dur is not None and (not isinstance(dur, int | float) or dur < 0):
            raise ValueError(r"'duration_ms' must be a non-negative number if provided.")
        if rel and dur is not None:
            raise ValueError("Provide either 'release=True' or 'duration_ms', not both.")
        return values

    @log_action("HoldKeyAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "HoldKeyAction")
        if self.release:
            await page.keyboard.up(self.key)
            return

        await page.keyboard.down(self.key)
        if self.duration_ms is not None:
            await page.wait_for_timeout(int(self.duration_ms))
            await page.keyboard.up(self.key)
