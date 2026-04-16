from typing import Any, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class AssertAction(BaseAction):
    """Asserts that specific text exists within the page's main frame content."""

    type: Literal["AssertAction"] = "AssertAction"
    text_to_assert: str = Field(..., description="The text content to check for existence on the page.")

    @log_action("AssertAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "AssertAction")
        content = await page.content()
        if self.text_to_assert not in content:
            raise AssertionError(f"'{self.text_to_assert}' not found in page source.")
