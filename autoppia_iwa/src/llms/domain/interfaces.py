# interfaces.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class LLMConfig:
    """Basic configuration for LLMs."""

    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048


class ILLM(ABC):
    """Minimal interface for LLM models with two methods."""

    @abstractmethod
    def predict(self, messages: List[Dict[str, str]], json_format: bool = False, schema: Optional[Dict] = None) -> str:
        """
        Synchronous inference call.
        """

    @abstractmethod
    async def async_predict(self, messages: List[Dict[str, str]], json_format: bool = False, schema: Optional[Dict] = None) -> str:
        """
        Asynchronous inference call.
        """
