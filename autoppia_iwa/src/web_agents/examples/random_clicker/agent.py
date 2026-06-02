import random
from typing import Any

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, ClickAction
from autoppia_iwa.src.web_agents.classes import BaseAgent


class RandomClickerWebAgent(BaseAgent):
    """Web Agent that executes random click actions within the screen dimensions."""

    def __init__(self, id: str | None = None, name="Random clicker", is_random: bool = True):
        super().__init__(id=id, name=name)
        self.is_random = is_random

    async def step(
        self,
        *,
        task: Task,
        html: str = "",
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
        snapshot_html: str | None = None,
    ) -> list[BaseAction]:
        if self.is_random:
            x = random.randint(0, task.specifications.screen_width - 1)
            y = random.randint(0, task.specifications.screen_height - 1)
        else:
            x = 0
            y = 0
        return [ClickAction(selector=None, x=x, y=y)]

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str = "",
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
        screenshot: str | bytes | None = None,
    ) -> list[BaseAction]:
        """Compatibility alias for benchmark paths that call /act-style agents."""
        return await self.step(
            task=task,
            html=snapshot_html,
            screenshot=screenshot,
            url=url,
            step_index=step_index,
            history=history,
            snapshot_html=snapshot_html,
        )
