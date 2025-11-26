"""Web Agent base classes and interfaces."""

import random
import string
import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.base import BaseAction


class IWebAgent(ABC):
    """
    Interface for all web agents in IWA.

    The design ensures standardized inputs and behaviors across different agents.
    Every web agent must implement this interface for compatibility with the evaluation system.

    Example implementations:
    - ApifiedWebAgent: HTTP API-based agent (recommended)
    - RandomAgent: Random clicker for baseline
    - BrowserUseAgent: External browser-use library wrapper
    - RLAgent: Reinforcement Learning agent
    """

    id: str
    name: str

    @abstractmethod
    async def solve_task(self, task: Task) -> "TaskSolution":
        """
        Solve a task and return the solution.

        Args:
            task: The task to solve

        Returns:
            TaskSolution with list of actions to execute
        """
        pass


class BaseAgent(IWebAgent):
    """Helper base class with common agent functionality."""

    def __init__(self, id: str | None = None, name: str | None = None):
        self.id = id or self.generate_random_web_agent_id()
        self.name = name if name is not None else f"Agent {self.id}"

    def generate_random_web_agent_id(self, length=16):
        """Generates a random alphanumeric string for the web_agent ID."""
        letters_and_digits = string.ascii_letters + string.digits
        return "".join(random.choice(letters_and_digits) for _ in range(length))


class TaskSolution(BaseModel):
    """
    Solution to a task consisting of a sequence of actions.

    This is the standard output format that all web agents must return.
    """

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the task, auto-generated using UUID4")
    actions: list[BaseAction] = Field(default_factory=list, description="List of actions to execute")
    web_agent_id: str | None = None
    recording: Any | None = Field(default=None, description="Optional recording data associated with the task solution")

    def nested_model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Serialize with nested action dumps."""
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["actions"] = [action.model_dump() for action in self.actions]
        return base_dump

    def replace_web_agent_id(self) -> list[BaseAction]:
        """Replace <web_agent_id> placeholders in action fields with actual agent ID."""
        if self.web_agent_id is None:
            return self.actions

        for action in self.actions:
            for field in ("text", "url", "value"):
                if hasattr(action, field):
                    value = getattr(action, field)
                    if isinstance(value, str) and ("<web_agent_id>" in value or "your_book_id" in value):
                        new_val = value.replace("<web_agent_id>", str(self.web_agent_id)).replace("<your_book_id>", str(self.web_agent_id))
                        setattr(action, field, new_val)
        return self.actions
