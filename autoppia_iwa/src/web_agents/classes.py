from typing import List, Optional

from pydantic import BaseModel, Field

from ..data_generation.domain.classes import Task
from ..execution.actions.base import BaseAction


class TaskSolution(BaseModel):
    task: Task
    actions: List[BaseAction] = Field(default_factory=list)
    web_agent_id: Optional[str] = None

    def nested_model_dump(self, *args, **kwargs) -> str:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["task"] = self.task.nested_model_dump(*args, **kwargs)
        base_dump["actions"] = [action.model_dump() for action in self.actions]
        return base_dump
