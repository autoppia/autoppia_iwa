import random

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction
from autoppia_iwa.src.web_agents.base import BaseAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


class RandomClickerWebAgent(BaseAgent):
    """
    Web Agent that executes random actions within the screen dimensions.
    """

    def __init__(self, name="Random clicker"):
        super().__init__(name=name)

    async def solve_task(self, task: Task) -> TaskSolution:
        """
        Generates a list of random click actions within the screen dimensions.
        :param task: The task for which actions are being generated.
        :return: A TaskSolution containing the generated actions.
        """
        # actions = [NavigateAction(url=task.url)]
        actions = []
        for _ in range(1):  # Generate 10 random click actions
            x = random.randint(0, task.specifications.screen_width - 1)  # Random x coordinate
            y = random.randint(0, task.specifications.screen_height - 1)  # Random y coordinate
            actions.append(ClickAction(x=x, y=y))

        return TaskSolution(task=task, actions=actions)
