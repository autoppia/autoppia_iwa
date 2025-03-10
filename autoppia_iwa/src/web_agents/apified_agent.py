import asyncio

import aiohttp

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction
from autoppia_iwa.src.shared.utils import generate_random_web_agent_id
from autoppia_iwa.src.web_agents.base import IWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


class ApifiedWebAgent(IWebAgent):
    """
    Calls a remote /solve_task endpoint and rebuilds a TaskSolution.
    """

    def __init__(self, host: str, port: int, id: str | None = None, name: str | None = None, timeout=180):
        self.id = id or generate_random_web_agent_id()
        self.name = name or f"Agent {self.id}"
        self.base_url = f"http://{host}:{port}"
        self.timeout = timeout
        super().__init__()

    async def solve_task(self, task: Task) -> TaskSolution:
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(f"{self.base_url}/solve_task", json=task.clean_task()) as response:
                    response_json = await response.json()

                    # Extract data
                    actions_data = response_json.get("actions", [])
                    web_agent_id = response_json.get("web_agent_id", "unknown")

                # Rebuild
                rebuilt_actions = [BaseAction.create_action(action) for action in actions_data]
                # print(f"Rebuilt Actions: {rebuilt_actions}")

                return TaskSolution(task_id=task.id, actions=rebuilt_actions, web_agent_id=web_agent_id)
            except Exception as e:
                print(f"Error during HTTP request: {e}")
                # print(traceback.format_exc())
                return TaskSolution(task_id=task.id, actions=[], web_agent_id="unknown")

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
