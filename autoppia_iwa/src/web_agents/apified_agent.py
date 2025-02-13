import random
import string
from abc import ABC, abstractmethod
import asyncio
import aiohttp

from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.execution.actions.actions import BaseAction, ACTION_CLASS_MAP


class IWebAgent(ABC):
    @abstractmethod
    async def solve_task(self, task: Task) -> TaskSolution:
        pass


class BaseAgent(IWebAgent):
    def __init__(self, name=None):
        self.id = self._generate_random_web_agent_id()
        self.name = name if name is not None else f"Agent {self.id}"

    def _generate_random_web_agent_id(self, length=16):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))


class ApifiedWebAgent:
    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.base_url = f"http://{host}:{port}"

    async def solve_task(self, task: Task) -> TaskSolution:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/solve_task",
                json=task.model_dump()
            ) as response:
                response_json = await response.json()
                task_data = response_json.get("task", {})
                actions_data = response_json.get("actions", [])
                web_agent_id = response_json.get("web_agent_id", "unknown")

                parsed_task = Task.model_validate(task_data)
                iwa_actions = BaseAction.from_response(actions_data, ACTION_CLASS_MAP)

                return TaskSolution(
                    task=parsed_task,
                    actions=iwa_actions,
                    web_agent_id=web_agent_id
                )

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
