# interfaces.py

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Basic configuration for LLMs."""

    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048


class ILLM(ABC):
    """Minimal interface for LLM models with two methods."""

    @abstractmethod
    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Synchronous inference call.
        """

    @abstractmethod
    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Asynchronous inference call.
        """
