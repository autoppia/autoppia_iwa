from typing import Any, Literal

from ..base import BaseAction
from .helpers import log_action


class UndefinedAction(BaseAction):
    """Represents an undefined or placeholder action. Does nothing."""

    type: Literal["UndefinedAction"] = "UndefinedAction"

    @log_action("UndefinedAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        pass
