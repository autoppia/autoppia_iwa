from typing import Any, ClassVar, Literal

from .base_click import BaseClickAction
from .helpers import SELECTOR_OR_COORDS_REQUIRED_MSG, _ensure_page, log_action


class TripleClickAction(BaseClickAction):
    """Triple-clicks an element identified by a selector or coordinates."""

    type: Literal["TripleClickAction"] = "TripleClickAction"
    browser_use_tool_name: ClassVar[str] = "tripleclick"

    @log_action("TripleClickAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "TripleClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, click_count=3, no_wait_after=True)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, click_count=3)
            return

        raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)

