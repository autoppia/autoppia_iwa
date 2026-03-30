from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import log_action


class DoneAction(BaseAction):
    """Explicit completion signal for step-wise agent loops."""

    type: Literal["DoneAction"] = "DoneAction"
    browser_use_tool_name: ClassVar[str] = "done"
    reason: str | None = Field(None, description="Optional completion reason for logs/debugging.")

    @log_action("DoneAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        return None
