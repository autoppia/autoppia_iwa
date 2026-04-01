from typing import Any, ClassVar, Literal

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _ensure_page, _maybe_wait_navigation, log_action


class MiddleClickAction(BaseClickAction):
    """Middle-clicks an element identified by a selector or coordinates."""

    type: Literal["MiddleClickAction"] = "MiddleClickAction"
    browser_use_tool_name: ClassVar[str] = "middleclick"

    @log_action("MiddleClickAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MiddleClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, button="middle", no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, button="middle")
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)
