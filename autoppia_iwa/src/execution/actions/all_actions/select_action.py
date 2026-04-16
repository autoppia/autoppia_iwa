from typing import Any, Literal

from pydantic import Field

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, log_action


class SelectAction(BaseActionWithSelector):
    """Selects an option in a dropdown (<select>) element."""

    type: Literal["SelectAction"] = "SelectAction"
    value: str = Field(..., description="The value, label, or index of the option to select.")

    @log_action("SelectAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SelectAction")
        sel_str = self.get_playwright_selector()
        await page.select_option(sel_str, self.value)
