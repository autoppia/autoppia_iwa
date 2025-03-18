import uuid

from pydantic import BaseModel, Field

from autoppia_iwa.src.execution.actions.base import BaseAction


class TaskSolution(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task, auto-generated using UUID4")
    actions: list[BaseAction] = Field(default_factory=list)
    web_agent_id: str | None = None

    def nested_model_dump(self, *args, **kwargs) -> str:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["actions"] = [action.model_dump() for action in self.actions]
        return base_dump
