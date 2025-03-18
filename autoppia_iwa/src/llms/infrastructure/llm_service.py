# llm_service.py


import httpx
from openai import AsyncOpenAI, OpenAI

from autoppia_iwa.src.llms.domain.interfaces import ILLM, LLMConfig


class OpenAIService(ILLM):
    """
    Simple OpenAI-based LLM.
    Uses OpenAI (sync) and AsyncOpenAI (async) clients.
    """

    def __init__(self, config: LLMConfig, api_key: str):
        self.config = config
        self.sync_client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None) -> dict:
        """
        Prepares the payload for OpenAI API requests.
        """
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }
        if json_format and schema:
            payload["response_format"] = {"type": "json_object"}
            # Add system message for JSON structure
            messages.insert(0, {"role": "system", "content": f"You must respond with JSON that matches this schema: {schema}"})
            payload["messages"] = messages
        return payload

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Synchronous prediction using OpenAI's API.
        """
        try:
            payload = self._prepare_payload(messages, json_format, schema)
            response = self.sync_client.chat.completions.create(**payload)
            if return_raw:
                return response
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Asynchronous prediction using OpenAI's API.
        """
        try:
            payload = self._prepare_payload(messages, json_format, schema)
            response = await self.async_client.chat.completions.create(**payload)
            if return_raw:
                return response
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI Async Error: {e}") from e


class LocalLLMService(ILLM):
    """
    Simple local (self-hosted) LLM that communicates via HTTP.
    Uses HTTPX for sync and async calls.
    """

    def __init__(self, config: LLMConfig, endpoint_url: str):
        """
        :param config: LLMConfig object with model details, max_tokens, temperature, etc.
        :param endpoint_url: The HTTP endpoint for single-request generation (e.g. /generate).
        """
        self.config = config
        self.endpoint_url = endpoint_url

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None) -> dict:
        """
        Prepares the payload for local LLM API requests.
        """
        payload = {
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if json_format:
            payload["json_format"] = True
        if schema:
            payload["schema"] = schema
        return payload

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Synchronous prediction using the local LLM endpoint.
        """
        try:
            with httpx.Client(timeout=180.0) as client:
                payload = self._prepare_payload(messages, json_format, schema)
                response = client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                return response.json().get("output", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Local LLM Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Asynchronous prediction using the local LLM endpoint.
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = self._prepare_payload(messages, json_format, schema)
                response = await client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                return response.json().get("output", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Local LLM Async Error: {e}") from e


class LLMFactory:
    """
    Simple factory to build the right LLM implementation
    based on the llm_type.
    """

    @staticmethod
    def create_llm(llm_type: str, config: LLMConfig, **kwargs) -> ILLM:
        if llm_type.lower() == "openai":
            return OpenAIService(config, api_key=kwargs.get("api_key"))
        elif llm_type.lower() == "local":
            return LocalLLMService(config, endpoint_url=kwargs.get("endpoint_url"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
