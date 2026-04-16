from typing import Any, ClassVar, Literal

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _ensure_page, _maybe_wait_navigation, log_action


class ClickAction(BaseClickAction):
    """Clicks an element identified by a selector, or at specific coordinates."""

    type: Literal["ClickAction"] = "ClickAction"
    browser_use_tool_name: ClassVar[str] = "click"

    @log_action("ClickAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y)
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)
