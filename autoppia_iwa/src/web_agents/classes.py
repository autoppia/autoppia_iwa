"""Web Agent base classes and interfaces."""

import random
import string
import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.base import BaseAction


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
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[BaseAction]:
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
