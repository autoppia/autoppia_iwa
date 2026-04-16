from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class NavigateAction(BaseAction):
    """Navigates the browser to a URL, or goes back/forward in history."""

    type: Literal["NavigateAction"] = "NavigateAction"
    browser_use_tool_name: ClassVar[str] = "navigate"
    url: str | None = Field(None, description="The URL to navigate to. Required unless go_back or go_forward is true.")
    go_back: bool = Field(False, description="If true, navigates to the previous page in history.")
    go_forward: bool = Field(False, description="If true, navigates to the next page in history.")

    @model_validator(mode="before")
    @classmethod
    def check_navigation_target(cls, values):
        url = values.get("url")
        go_back = values.get("go_back", False)
        go_forward = values.get("go_forward", False)
        if sum([bool(url), go_back, go_forward]) != 1:
            raise ValueError("NavigateAction requires exactly one of 'url', 'go_back=True', or 'go_forward=True'.")
        return values

    @log_action("NavigateAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "NavigateAction")
        if self.go_back:
            await page.go_back()
        elif self.go_forward:
            await page.go_forward()
        elif self.url:
            await page.goto(self.url)
        else:
            raise ValueError("Invalid state: NavigateAction has no target.")
