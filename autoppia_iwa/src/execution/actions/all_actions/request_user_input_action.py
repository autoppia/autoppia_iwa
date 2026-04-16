from typing import Any, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import log_action


class RequestUserInputAction(BaseAction):
    """Request structured input from the user before continuing execution."""

    type: Literal["RequestUserInputAction"] = "RequestUserInputAction"
    prompt: str = Field(..., description="Prompt/question presented to the user.")
    options: list[str] | None = Field(None, description="Optional list of suggested choices.")
    allow_free_form: bool = Field(True, description="Whether the user can answer outside the suggested options.")
    question_id: str | None = Field(None, description="Optional stable identifier for mapping the answer.")
    required: bool = Field(True, description="Whether answering this question is required to continue.")

    @log_action("RequestUserInputAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        return None
