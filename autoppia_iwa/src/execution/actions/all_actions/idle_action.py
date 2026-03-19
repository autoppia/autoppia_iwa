from typing import Any, Literal

from ..base import BaseAction
from .helpers import log_action


class IdleAction(BaseAction):
    """Represents an intentional idle state or pause. Does nothing."""

    type: Literal["IdleAction"] = "IdleAction"

    @log_action("IdleAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        pass
