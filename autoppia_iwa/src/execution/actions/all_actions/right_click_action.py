from typing import Any, ClassVar, Literal

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _ensure_page, _maybe_wait_navigation, log_action


class RightClickAction(BaseClickAction):
    """Right-clicks an element identified by a selector or coordinates."""

    type: Literal["RightClickAction"] = "RightClickAction"
    browser_use_tool_name: ClassVar[str] = "rightclick"

    @log_action("RightClickAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "RightClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, button="right", no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, button="right")
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)

