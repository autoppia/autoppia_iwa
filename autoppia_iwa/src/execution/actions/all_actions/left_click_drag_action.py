from typing import Any, Literal

from pydantic import Field, model_validator

from ..base import BaseAction, Selector
from .helpers import _element_center, _ensure_page, _move_mouse_to, log_action


class LeftClickDragAction(BaseAction):
    r"""Left-click drag from a start selector/(x,y) to a target selector/(x,y)."""

    type: Literal["LeftClickDragAction"] = "LeftClickDragAction"
    selector: Selector | None = Field(None, description="Start selector. If omitted, x/y must be provided.")
    x: int | None = Field(None, description="Start X coordinate.")
    y: int | None = Field(None, description="Start Y coordinate.")
    targetSelector: Selector | None = Field(None, description="Target selector. If omitted, targetX/targetY must be provided.")
    targetX: int | None = Field(None, description="Target X coordinate.")
    targetY: int | None = Field(None, description="Target Y coordinate.")
    steps: int = Field(1, description="Number of intermediate mouse move steps during the drag.")

    @model_validator(mode="before")
    @classmethod
    def _validate_points(cls, values):
        has_start_sel = values.get("selector") is not None
        has_start_xy = values.get("x") is not None and values.get("y") is not None
        if not (has_start_sel or has_start_xy):
            raise ValueError("Provide a start 'selector' or both 'x' and 'y'.")

        has_target_sel = values.get("targetSelector") is not None
        has_target_xy = values.get("targetX") is not None and values.get("targetY") is not None
        if not (has_target_sel or has_target_xy):
            raise ValueError("Provide a target 'targetSelector' or both 'targetX' and 'targetY'.")

        steps = values.get("steps", 1)
        try:
            steps = int(steps)
        except (ValueError, TypeError):
            steps = 1
        values["steps"] = max(1, steps)
        return values

    @log_action("LeftClickDragAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "LeftClickDragAction")
        start_selector_str = self.selector.to_playwright_selector() if self.selector else None
        await _move_mouse_to(page, start_selector_str, self.x, self.y, steps=1)
        await page.mouse.down(button="left")

        if self.targetSelector:
            target_sel_str = self.targetSelector.to_playwright_selector()
            tx, ty = await _element_center(page, target_sel_str)
            await page.mouse.move(tx, ty, steps=self.steps)
            await page.hover(target_sel_str)
        else:
            if self.targetX is None or self.targetY is None:
                await page.mouse.up(button="left")
                raise ValueError("Target coordinates must include both 'targetX' and 'targetY'.")
            tx, ty = int(self.targetX), int(self.targetY)
            await page.mouse.move(tx, ty, steps=self.steps)

        await page.wait_for_timeout(50)
        await page.mouse.up(button="left")
