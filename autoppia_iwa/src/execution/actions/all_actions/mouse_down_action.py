from typing import Any, Literal

from .base_click import BaseClickAction
from .helpers import _ensure_page, _move_mouse_to, log_action


class MouseDownAction(BaseClickAction):
    """Presses the left mouse button down on a selector or at coordinates."""

    type: Literal["MouseDownAction"] = "MouseDownAction"

    @log_action("MouseDownAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseDownAction")

        sel = self.get_playwright_selector() if self.selector else None
        await _move_mouse_to(page, sel, self.x, self.y)
        await page.mouse.down(button="left")
