import asyncio

import aiohttp

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.execution.actions.actions import ACTION_CLASS_MAP, BaseAction
from autoppia_iwa.src.web_agents.classes import TaskSolution


class ApifiedWebAgent:
    """
    Calls a remote /solve_task endpoint and rebuilds a TaskSolution.
    """

    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.base_url = f"http://{host}:{port}"

    async def solve_task(self, task: Task) -> TaskSolution:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/solve_task", json=task.nested_model_dump()) as response:
                response_json = await response.json()

                # Extract data
                task_data = response_json.get("task", {})
                actions_data = response_json.get("actions", [])
                web_agent_id = response_json.get("web_agent_id", "unknown")

                # Rebuild
                rebuilt_task = Task.from_dict(task_data)
                print(f"Rebuilt Task: {rebuilt_task}")
                rebuilt_actions = BaseAction.from_response(actions_data, ACTION_CLASS_MAP)
                print(f"Rebuilt Actions: {rebuilt_actions}")

                return TaskSolution(task=rebuilt_task, actions=rebuilt_actions, web_agent_id=web_agent_id)

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
