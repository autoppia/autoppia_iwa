import asyncio

import aiohttp

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


class ApifiedWebAgent(IWebAgent):
    """
    Calls a remote /solve_task endpoint and rebuilds a TaskSolution.
    """

    def __init__(self, host: str | None = None, port: int | None = None, id: str | None = None, name: str | None = None, timeout=180, base_url: str | None = None):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Agent {self.id}"
        if base_url:
            # Respect provided base_url as-is
            self.base_url = base_url.rstrip("/")
        else:
            if host is None:
                raise ValueError("host must be provided when base_url is not set")
            # If port is provided, include it; otherwise omit
            if port is not None:
                self.base_url = f"http://{host}:{port}"
            else:
                self.base_url = f"http://{host}"
        self.timeout = timeout
        super().__init__()

    async def solve_task(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f"{self.base_url}/solve_task", json=task.clean_task()) as response:
                    response.raise_for_status()
                    response_json = await response.json()
            except Exception as e:  # noqa: BLE001
                raise RuntimeError(f"Error during HTTP request to {self.base_url}/solve_task: {e}") from e

            actions_data = response_json.get("actions", [])
            web_agent_id = response_json.get("web_agent_id", "unknown")
            recording_str = response_json.get("recording", "")

        rebuilt_actions = [BaseAction.create_action(action) for action in actions_data]
        task_solution = TaskSolution(task_id=task.id, actions=rebuilt_actions, web_agent_id=web_agent_id, recording=recording_str)
        return task_solution

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
