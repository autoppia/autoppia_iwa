from typing import Any, ClassVar, Literal

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, log_action


class HoverAction(BaseActionWithSelector):
    """Hovers the mouse cursor over an element identified by a selector."""

    type: Literal["HoverAction"] = "HoverAction"
    browser_use_tool_name: ClassVar[str] = "hover"

    @log_action("HoverAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "HoverAction")
        sel_str = self.get_playwright_selector()
        await page.hover(sel_str)
