from typing import Any, Literal

from pydantic import Field

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _element_center, _ensure_page, log_action


class MouseMoveAction(BaseClickAction):
    """Moves the mouse to a selector center or to specific coordinates."""

    type: Literal["MouseMoveAction"] = "MouseMoveAction"
    steps: int = Field(1, description="Number of intermediate mouse move steps (animation).")

    @log_action("MouseMoveAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseMoveAction")

        if self.selector:
            sel = self.get_playwright_selector()
            cx, cy = await _element_center(page, sel)
            await page.mouse.move(cx, cy, steps=self.steps)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.move(self.x, self.y, steps=self.steps)
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)

