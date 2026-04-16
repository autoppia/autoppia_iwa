from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class SendKeysIWAAction(BaseAction):
    """Presses keyboard keys. Can be used for shortcuts or special keys."""

    type: Literal["SendKeysIWAAction"] = "SendKeysIWAAction"
    browser_use_tool_name: ClassVar[str] = "send_keys"
    keys: str = Field(..., description="The key or key combination to press (e.g., 'Enter', 'Control+C', 'ArrowDown').")

    @log_action("SendKeysIWAAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SendKeysIWAAction")
        await page.keyboard.press(self.keys)
