import random
import string
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.web_agents.classes import TaskSolution
from autoppia_iwa.src.execution.actions.actions import BaseAction, ACTION_CLASS_MAP


class IWebAgent(ABC):
    """

    The design allows for multiple web agents to implement this interface, ensuring standardized inputs and behaviors across different agents.

    Every web agent that implements this interface must define the required methods and properties, ensuring consistency and compatibility.

    Example:
    - An 'Autopilot Web Agent' would implement this interface, adhering to the standardized inputs and outputs specified here.

    The goal is to provide a common structure that all web agents will follow, facilitating integration and interoperability among them.
    """

    @abstractmethod
    async def solve_task(self, task: Task) -> TaskSolution:
        pass


class BaseAgent(IWebAgent):
    def __init__(self, name=None):
        self.id = self.generate_random_web_agent_id()
        self.name = name if name is not None else f"Agent {self.id}"

    def generate_random_web_agent_id(self, length=16):
        """Generates a random alphanumeric string for the web_agent ID."""
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
                json=task.model_dump()  # or task.dict() in Pydantic v1
            ) as response:
                response_json = await response.json()

                # 1) Extract top-level fields
                task_data = response_json.get("task", {})
                actions_data = response_json.get("actions", [])
                web_agent_id = response_json.get("web_agent_id", "unknown")

                # 2) Parse the Task
                # If you have a Pydantic model for Task, do something like:
                task_obj = Task.model_validate(task_data)  # Pydantic v2
                # or for Pydantic v1: task_obj = Task.parse_obj(task_data)

                # 3) Parse actions using BaseAction.from_response
                iwa_actions = BaseAction.from_response(actions_data, ACTION_CLASS_MAP)

                # 4) Build a TaskSolution
                solution = TaskSolution(
                    task=task_obj,
                    actions=iwa_actions,
                    web_agent_id=web_agent_id
                )
                return solution

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
