import random
import string
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from autoppia_iwa.src.data_generation.domain.classes import Task
from autoppia_iwa.src.web_agents.classes import TaskSolution


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
            async with session.post(f"{self.base_url}/solve_task", json=task.dict()) as response:
                response_json = await response.json()
                return TaskSolution.parse_obj(response_json)

    def solve_task_sync(self, task: Task) -> TaskSolution:
        return asyncio.run(self.solve_task(task))
