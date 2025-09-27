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


class ChutesLLMService(ILLM):
    """
    Chutes LLM using OpenAI-compatible API via HTTPX.
    """

    def __init__(self, config: LLMConfig, base_url: str, api_key: str, use_bearer: bool = False):
        """
        :param config: LLMConfig object
        :param base_url: e.g. https://myuser-my-llm.chutes.ai/v1
        :param api_key: Chutes API key
        :param use_bearer: If True, use Authorization: Bearer header; else X-API-Key
        """
        self.config = config
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.use_bearer = use_bearer

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None) -> dict:
        payload = {
            "model": self.config.model,
            "messages": list(messages),  # no mutar original
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        if json_format:
            sys_prompt = {
                "role": "system",
                "content": (
                    "Your ONLY output must be a valid JSON array of strings, e.g.: "
                    '["prompt1", "prompt2"]. '
                    "Do not wrap it in an object, do not include keys, do not output <think>, explanations, or Markdown."
                ),
            }
            payload["messages"].insert(0, sys_prompt)

            if schema:
                payload["messages"].insert(1, {"role": "system", "content": f"You must respond with JSON that matches this schema: {schema}"})

        return payload

    def _headers(self):
        if self.use_bearer:
            return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        else:
            return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Synchronous prediction using Chutes API.
        """
        url = f"{self.base_url}/chat/completions"
        try:
            with httpx.Client(timeout=180.0) as client:
                payload = self._prepare_payload(messages, json_format, schema)
                response = client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Chutes LLM Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False) -> str:
        """
        Asynchronous prediction using Chutes API.
        """
        url = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = self._prepare_payload(messages, json_format, schema)
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Chutes LLM Async Error: {e}") from e


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
        elif llm_type.lower() == "chutes":
            return ChutesLLMService(config, base_url=kwargs.get("base_url"), api_key=kwargs.get("api_key"), use_bearer=kwargs.get("use_bearer", False))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
