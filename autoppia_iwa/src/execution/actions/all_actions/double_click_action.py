from typing import Any, ClassVar, Literal

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _ensure_page, _maybe_wait_navigation, log_action


class DoubleClickAction(BaseClickAction):
    """Double-clicks an element identified by a selector or coordinates."""

    type: Literal["DoubleClickAction"] = "DoubleClickAction"
    browser_use_tool_name: ClassVar[str] = "dblclick"

    @log_action("DoubleClickAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "DoubleClickAction")

        if self.selector:
            selector_str = self.get_playwright_selector()
            await page.dblclick(selector_str, no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.dblclick(x=self.x, y=self.y)
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)
