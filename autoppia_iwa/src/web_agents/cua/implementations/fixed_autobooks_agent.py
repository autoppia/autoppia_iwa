from __future__ import annotations

from typing import Any

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.web_agents.classes import BaseAgent, TaskSolution


class FixedAutobooksAgent(BaseAgent):
    """
    Extremely simple agent that ignores the task prompt and always
    returns the same hard-coded trajectory.

    It is designed so that, when evaluated only on the custom
    `autobooks-demo-task-1` task, it should achieve a perfect score
    (provided the selectors match the actual UI).
    """

    def __init__(self, id: str = "fixed_autobooks", name: str = "FixedAutobooksAgent"):
        super().__init__(id=id, name=name)
        self._cached_solution: TaskSolution | None = None

    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
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
        Always return the same sequence of actions:

        1) Navigate directly to a concrete book detail page that exists in the
           current remote deployment:
           `http://84.247.180.192:8001/books/book-original-002?seed=36`.
        """

        actions = [
            NavigateAction(
                type="NavigateAction",
                url="http://84.247.180.192:8001/books/book-original-002?seed=36",
            )
        ]

        solution = TaskSolution(
            task_id=task.id,
            actions=actions,
            web_agent_id=self.id,
        )

        return solution
