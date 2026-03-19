from typing import Any, Literal

from .base_click import BaseClickAction
from .helpers import _ensure_page, _move_mouse_to, log_action


class MouseUpAction(BaseClickAction):
    """Releases the left mouse button on a selector or at coordinates."""

    type: Literal["MouseUpAction"] = "MouseUpAction"

    @log_action("MouseUpAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseUpAction")

        sel = self.get_playwright_selector() if self.selector else None
        if sel or (self.x is not None and self.y is not None):
            await _move_mouse_to(page, sel, self.x, self.y)
        await page.mouse.up(button="left")

