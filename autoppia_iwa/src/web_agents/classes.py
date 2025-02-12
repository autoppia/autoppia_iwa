from typing import List, Optional

from pydantic import BaseModel, Field

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.actions.base import BaseAction


class TaskSolution(BaseModel):
    task: Task
    actions: List[BaseAction] = Field(default_factory=list)
    web_agent_id: Optional[str] = None
