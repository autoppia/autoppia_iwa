import uuid
from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.execution.actions.base import BaseAction


class TaskSolution(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task, auto-generated using UUID4")
    actions: list[BaseAction] = Field(default_factory=list)
    web_agent_id: str | None = None
    recording: Any | None = Field(default=None, description="Optional recording data associated with the task solution.")

    def nested_model_dump(self, *args, **kwargs) -> dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["actions"] = [action.model_dump() for action in self.actions]
        return base_dump

    def replace_web_agent_id(self) -> list[BaseAction]:
        if self.web_agent_id is None:
            return self.actions

        for action in self.actions:
            for field in ("text", "url", "value"):
                if hasattr(action, field):
                    value = getattr(action, field)
                    if isinstance(value, str) and ("<web_agent_id>" in value or "your_book_id" in value):
                        new_val = value.replace("<web_agent_id>", str(self.web_agent_id)).replace("<your_book_id>", str(self.web_agent_id))
                        setattr(action, field, new_val)
        return self.actions
