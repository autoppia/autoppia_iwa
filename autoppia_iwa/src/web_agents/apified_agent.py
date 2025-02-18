import asyncio
import aiohttp

from ..data_generation.domain.classes import Task
from ..execution.actions.actions import BaseAction
from .base import IWebAgent
from .classes import TaskSolution


class ApifiedWebAgent(IWebAgent):
    """
    Calls a remote /solve_task endpoint and rebuilds a TaskSolution.
    """

    def __init__(self, name: str, host: str, port: int, timeout=45):
        self.name = name
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        super().__init__()

    async def solve_task(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f"{self.base_url}/solve_task", json=task.nested_model_dump()) as response:
                    response_json = await response.json()

                    # Extract data
                    actions_data = response_json.get("actions", [])
                    web_agent_id = response_json.get("web_agent_id", "unknown")

                # Rebuild
                rebuilt_actions = [BaseAction.create_action(action) for action in actions_data]
                print(f"Rebuilt Actions: {rebuilt_actions}")

                return TaskSolution(task=task, actions=rebuilt_actions, web_agent_id=web_agent_id)
            except Exception as e:
                print(f"Error during HTTP request: {e}")
                return TaskSolution(task=task, actions=[], web_agent_id="unknown")

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
