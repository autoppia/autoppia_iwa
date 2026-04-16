"""Web Agent base classes and interfaces."""

import random
import string
import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field, computed_field

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.base import BaseAction

# ============================================================================
# Credential utilities
# ============================================================================

DEFAULT_PASSWORD = "Passw0rd!"  # NOSONAR - test password for placeholder replacement, not a real credential


def replace_credential_placeholders_in_string(s: str, web_agent_id: str) -> str:
    s = s.replace("<username>", f"user{web_agent_id}")
    s = s.replace("<password>", DEFAULT_PASSWORD)
    s = s.replace("<signup_username>", f"newuser{web_agent_id}")
    s = s.replace("<signup_email>", f"newuser{web_agent_id}@gmail.com")
    s = s.replace("<signup_password>", DEFAULT_PASSWORD)
    s = s.replace("<web_agent_id>", web_agent_id)  # NOSONAR
    return s


def replace_credentials_in_action(action: BaseAction, web_agent_id: str) -> None:
    credential_fields = ["text", "value", "url", "email", "username", "password"]
    for field_name in credential_fields:
        if hasattr(action, field_name):
            value = getattr(action, field_name)
            if isinstance(value, str):
                new_value = replace_credential_placeholders_in_string(value, web_agent_id)
                if new_value != value:
                    setattr(action, field_name, new_value)

    if hasattr(action, "selector") and action.selector and hasattr(action.selector, "value"):
        selector_value = action.selector.value
        if isinstance(selector_value, str):
            new_selector_value = replace_credential_placeholders_in_string(selector_value, web_agent_id)
            if new_selector_value != selector_value:
                action.selector.value = new_selector_value


def sanitize_html(html: str, web_agent_id: str) -> str:
    if not html:
        return html
    sanitized = html
    sanitized = sanitized.replace(f"newuser{web_agent_id}@gmail.com", "<signup_email>")
    sanitized = sanitized.replace(f"newuser{web_agent_id}", "<signup_username>")
    sanitized = sanitized.replace(f"user{web_agent_id}", "<username>")
    sanitized = sanitized.replace(DEFAULT_PASSWORD, "<password>")
    return sanitized


def sanitize_snapshot_html(snapshot_html: str, web_agent_id: str) -> str:
    """Backward-compatible alias for sanitize_html()."""
    return sanitize_html(snapshot_html, web_agent_id)


# ============================================================================
# Agent interface
# ============================================================================


class IWebAgent(ABC):
    """
    Interface for all web agents in IWA.

    All agents expose a single async step() method.
    They receive the browser state and return actions to execute.
    """

    id: str
    name: str

    @abstractmethod
    async def step(
        self,
        *,
        task: Task,
        html: str,
        screenshot: str | bytes | None = None,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        """
        Decide actions based on the current browser state.

        Args:
            task: The task to solve
            html: Current page HTML
            screenshot: Visual snapshot (bytes or base64 str). Optional.
            url: Current URL
            step_index: Iteration number
            history: Optional history of previous actions

        Returns:
            List of actions to execute
        """
        pass


class BaseAgent(IWebAgent):
    """Helper base class with common agent functionality."""

    def __init__(self, id: str | None = None, name: str | None = None):
        self.id = id or self.generate_random_web_agent_id()
        self.name = name if name is not None else f"Agent {self.id}"

    def generate_random_web_agent_id(self, length=16):
        letters_and_digits = string.ascii_letters + string.digits
        return "".join(random.choice(letters_and_digits) for _ in range(length))


# ============================================================================
# TaskSolution (kept for backward compatibility with concurrent evaluator)
# ============================================================================


class TaskSolution(BaseModel):
    """Solution to a task consisting of a sequence of actions."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actions: list[BaseAction] = Field(default_factory=list)
    web_agent_id: str | None = None
    recording: Any | None = Field(default=None)
    cost_usd: float = Field(default=0.0)
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    model_used: str | None = Field(default=None)

    @computed_field
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def nested_model_dump(self, *args, **kwargs) -> dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump["actions"] = [action.model_dump() for action in self.actions]
        return base_dump

    def replace_web_agent_id(self) -> list[BaseAction]:
        if self.web_agent_id is None:
            return self.actions
        for action in self.actions:
            for field in ("text", "url", "value"):
                if hasattr(action, field):
                    value = getattr(action, field)
                    if isinstance(value, str) and ("<web_agent_id>" in value or "your_book_id" in value):  # NOSONAR
                        new_val = value.replace("<web_agent_id>", str(self.web_agent_id)).replace("<your_book_id>", str(self.web_agent_id))
                        setattr(action, field, new_val)
        return self.actions

    def replace_credentials(self, web_agent_id: str) -> list[BaseAction]:
        for action in self.actions:
            replace_credentials_in_action(action, web_agent_id)
        return self.actions
