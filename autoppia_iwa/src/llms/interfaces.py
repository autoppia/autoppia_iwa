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
    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        """
        Synchronous inference call.

        Args:
            temperature: Optional temperature override. If None, uses config temperature.
        """

    @abstractmethod
    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        """
        Asynchronous inference call.

        Args:
            temperature: Optional temperature override. If None, uses config temperature.
        """
