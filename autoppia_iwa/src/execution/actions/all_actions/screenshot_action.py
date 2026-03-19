from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class ScreenshotAction(BaseAction):
    """Takes a screenshot of the current page."""

    type: Literal["ScreenshotAction"] = "ScreenshotAction"
    browser_use_tool_name: ClassVar[str] = "screenshot"
    file_path: str = Field(default="", description="The file path where the screenshot should be saved.")
    full_page: bool = Field(False, description="Whether to capture the full scrollable page.")

    @log_action("ScreenshotAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ScreenshotAction")
        if self.file_path:
            await page.screenshot(path=self.file_path, full_page=self.full_page)
        else:
            await page.screenshot(full_page=self.full_page)
