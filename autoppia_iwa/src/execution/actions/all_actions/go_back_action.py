from typing import Any, ClassVar, Literal

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class GoBackAction(BaseAction):
    """Navigates to the previous page in browser history."""

    type: Literal["GoBackAction"] = "GoBackAction"
    browser_use_tool_name: ClassVar[str] = "go_back"

    @log_action("GoBackAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "GoBackAction")
        await page.go_back()
