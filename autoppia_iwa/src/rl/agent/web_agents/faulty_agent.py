from __future__ import annotations

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
from autoppia_iwa.src.web_agents.classes import BaseAgent, TaskSolution


class FaultyWebAgent(BaseAgent):
    """Agent that purposely issues an invalid selector to trigger action failures."""

    async def solve_task(self, task: Task) -> TaskSolution:
        selector = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="non-existent-element")
        action = ClickAction(selector=selector)
        return TaskSolution(task_id=task.id, actions=[action], web_agent_id=self.id)
