from __future__ import annotations

from loguru import logger

try:
    from autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
    from autoppia_iwa.src.web_agents.classes import TaskSolution
except ModuleNotFoundError:  # pragma: no cover - source-tree fallback
    from autoppia_iwa.autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent
    from autoppia_iwa.autoppia_iwa.src.web_agents.classes import TaskSolution


class RemoteAgentClient:
    """Thin wrapper around ApifiedWebAgent to talk to miner endpoints."""

    def __init__(self, base_url: str, timeout: float, web_agent_name: str):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.web_agent_name = web_agent_name
        self._agent = ApifiedWebAgent(base_url=self.base_url, timeout=self.timeout, name=web_agent_name, id=web_agent_name)

    async def solve_task(self, task: Task) -> TaskSolution:
        """Send the task to the miner and convert the response into a TaskSolution."""

        # Send task WITH placeholders - agent should return actions with placeholders
        solution = await self._agent.solve_task(task)
        if not getattr(solution, "web_agent_id", None):
            solution.web_agent_id = self.web_agent_name
        # Replace credential placeholders in actions BEFORE returning
        solution.replace_credentials(self.web_agent_name)
        logger.info("Received %s actions for task %s from %s", len(solution.actions), task.id, self.web_agent_name)
        return solution
