"""Web Agent base classes and interfaces."""

import random
import string
import uuid
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.base import BaseAction


def replace_credentials_in_action(action: BaseAction, web_agent_id: str) -> None:
    """
    Replace credential placeholders in a single action with actual values.
    This should be called AFTER receiving actions from the agent but BEFORE evaluating them.

    Replaces:
    - <username> → user{web_agent_id}
    - <password> → Passw0rd!
    - <signup_username> → newuser{web_agent_id}
    - <signup_email> → newuser{web_agent_id}@gmail.com
    - <signup_password> → Passw0rd!
    """
    # Common fields in actions that may contain credential placeholders
    credential_fields = ["text", "value", "url", "email", "username", "password"]

    # Check common fields first (more efficient)
    for field_name in credential_fields:
        if hasattr(action, field_name):
            value = getattr(action, field_name)
            if isinstance(value, str):
                # Replace credential placeholders
                new_value = value.replace("<username>", f"user{web_agent_id}")
                new_value = new_value.replace("<password>", "Passw0rd!")
                new_value = new_value.replace("<signup_username>", f"newuser{web_agent_id}")
                new_value = new_value.replace("<signup_email>", f"newuser{web_agent_id}@gmail.com")
                new_value = new_value.replace("<signup_password>", "Passw0rd!")
                # Also replace <web_agent_id> for backward compatibility
                new_value = new_value.replace("<web_agent_id>", web_agent_id)

                if new_value != value:
                    setattr(action, field_name, new_value)

    # Also check selector.value if it exists (for actions with selectors)
    if hasattr(action, "selector") and action.selector and hasattr(action.selector, "value"):
        selector_value = action.selector.value
        if isinstance(selector_value, str):
            new_selector_value = selector_value.replace("<username>", f"user{web_agent_id}")
            new_selector_value = new_selector_value.replace("<password>", "Passw0rd!")
            new_selector_value = new_selector_value.replace("<signup_username>", f"newuser{web_agent_id}")
            new_selector_value = new_selector_value.replace("<signup_email>", f"newuser{web_agent_id}@gmail.com")
            new_selector_value = new_selector_value.replace("<signup_password>", "Passw0rd!")
            new_selector_value = new_selector_value.replace("<web_agent_id>", web_agent_id)

            if new_selector_value != selector_value:
                action.selector.value = new_selector_value


def sanitize_snapshot_html(snapshot_html: str, web_agent_id: str) -> str:
    """
    Mask concrete credentials inside snapshot HTML so the agent sees placeholders.

    Replaces:
    - user{web_agent_id} -> <username>
    - newuser{web_agent_id} -> <signup_username>
    - newuser{web_agent_id}@gmail.com -> <signup_email>
    - Passw0rd! -> <password>
    """
    if not snapshot_html:
        return snapshot_html

    sanitized = snapshot_html
    sanitized = sanitized.replace(f"newuser{web_agent_id}@gmail.com", "<signup_email>")
    sanitized = sanitized.replace(f"newuser{web_agent_id}", "<signup_username>")
    sanitized = sanitized.replace(f"user{web_agent_id}", "<username>")
    sanitized = sanitized.replace("Passw0rd!", "<password>")
    return sanitized


class IWebAgent(ABC):
    """
    Interface for all web agents in IWA.

    ✅ IMPORTANTE: Todos los agentes usan el mismo endpoint /act

    Los agentes son servicios HTTP que exponen el endpoint /act.
    Reciben el estado del browser y devuelven acciones a ejecutar.

    Esta interfaz se usa tanto en:
    - Modo concurrent: Se llama una vez y el agente devuelve todas las acciones
    - Modo stateful: Se llama iterativamente, el agente ve el estado en cada paso

    Example implementations:
    - ApifiedWebCUA: HTTP API-based agent (para benchmark y subnet)
    - Miners: Repositorios GitHub deployados como contenedores HTTP
    """

    id: str
    name: str

    @abstractmethod
    async def act(
        self,
        *,
        task: Task,
        snapshot_html: str,
        url: str,
        step_index: int,
        history: list[dict[str, Any]] | None = None,
    ) -> list[BaseAction]:
        """
        Decide acciones basándose en el estado actual del browser.

        Este método se usa tanto en modo concurrent como stateful:
        - Concurrent: Se llama UNA vez con snapshot inicial, devuelve TODAS las acciones
        - Stateful: Se llama ITERATIVAMENTE, devuelve acciones para el siguiente paso

        Args:
            task: La tarea a resolver
            snapshot_html: HTML actual de la página
            url: URL actual
            step_index: Número de iteración (0 en concurrent, incrementa en stateful)
            history: Historial opcional de acciones previas

        Returns:
            Lista de acciones a ejecutar (puede ser múltiples para batch execution)
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

    def replace_credentials(self, web_agent_id: str) -> list[BaseAction]:
        """
        Replace credential placeholders in ALL actions with actual values.

        ✅ THIS IS THE CORRECT METHOD TO USE.
        This should be called AFTER receiving actions from the agent but BEFORE evaluating them.

        The agent receives the task WITH placeholders and returns actions WITH placeholders.
        This method replaces placeholders in all actions before evaluation.

        Replaces in all action fields (text, value, url, email, username, password, selector.value):
        - <username> → user{web_agent_id}
        - <password> → Passw0rd!
        - <signup_username> → newuser{web_agent_id}
        - <signup_email> → newuser{web_agent_id}@gmail.com
        - <signup_password> → Passw0rd!
        - <web_agent_id> → web_agent_id (for backward compatibility)

        Args:
            web_agent_id: The web agent ID to use for credential replacement

        Returns:
            The list of actions with credentials replaced (modifies actions in place)
        """
        for action in self.actions:
            replace_credentials_in_action(action, web_agent_id)
        return self.actions
