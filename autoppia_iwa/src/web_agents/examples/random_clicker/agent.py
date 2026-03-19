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
