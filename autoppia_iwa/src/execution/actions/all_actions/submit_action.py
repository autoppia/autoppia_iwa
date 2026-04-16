from typing import Any, Literal

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, log_action


class SubmitAction(BaseActionWithSelector):
    """Submits a form by pressing Enter on a specific element."""

    type: Literal["SubmitAction"] = "SubmitAction"

    @log_action("SubmitAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SubmitAction")
        sel_str = self.get_playwright_selector()
        await page.locator(sel_str).press("Enter")
