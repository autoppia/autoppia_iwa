import random

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.actions.actions import ClickAction
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


class RandomClickerWebAgent(BaseAgent):
    """
    Web Agent that executes random actions within the screen dimensions.
    """

    def __init__(self, id: str | None = None, name="Random clicker", is_random: bool = True):
        super().__init__(id=id, name=name)
        self.is_random = is_random

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
                x = random.randint(0, task.specifications.screen_width - 1)  # Random x coordinate
                y = random.randint(0, task.specifications.screen_height - 1)  # Random y coordinate
            else:
                # This reduce overhead on evaluator.
                x = 0
                y = 0

            actions.append(ClickAction(x=x, y=y))

        return TaskSolution(task_id=task.id, actions=actions)
