import random
from typing import Any

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, ClickAction
from autoppia_iwa.src.web_agents.classes import BaseAgent, TaskSolution


class RandomClickerWebAgent(BaseAgent):
    """
    Web Agent that executes random actions within the screen dimensions.
    """

    def __init__(self, id: str | None = None, name="Random clicker", is_random: bool = True):
        super().__init__(id=id, name=name)
        self.is_random = is_random
        self._cached_solution: TaskSolution | None = None

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        """
        Act method for stateful mode. For concurrent mode agents, this returns
        all actions on the first step (step_index == 0) and empty list afterwards.
        """
        if step_index == 0:
            # First call: generate solution and cache it
            solution = await self.solve_task(task)
            self._cached_solution = solution
            return solution.actions
        else:
            # Subsequent calls: return empty list (all actions already returned)
            return []

    async def solve_task(self, task: Task) -> TaskSolution:
        """
        Generates a list of random click actions within the screen dimensions.
        :param task: The task for which actions are being generated.
        :return: A TaskSolution containing the generated actions.
        """
        # actions = [NavigateAction(url=task.url)]
        actions = []
        for _ in range(1):  # Generate 10 random click actions
            if self.is_random:
                # Random x coordinate
                x = random.randint(0, task.specifications.screen_width - 1)
                # Random y coordinate
                y = random.randint(0, task.specifications.screen_height - 1)
            else:
                # This reduce overhead on evaluator.
                x = 0
                y = 0

            actions.append(ClickAction(selector=None, x=x, y=y))

        return TaskSolution(task_id=task.id, actions=actions, web_agent_id=self.id or self.name)
