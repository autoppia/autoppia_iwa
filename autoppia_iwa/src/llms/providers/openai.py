from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, OpenAI, RateLimitError

from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig


class OpenAIService(ILLM):
    """OpenAI-based LLM using sync and async clients."""

    def __init__(self, config: LLMConfig, api_key: str):
        self.config = config
        self.sync_client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, temperature: float | None = None) -> dict:
        payload_messages = list(messages)
        payload = {
            "model": self.config.model,
            "messages": payload_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }
        if json_format and schema:
            payload["response_format"] = {"type": "json_object"}
            payload_messages.insert(0, {"role": "system", "content": f"You must respond with JSON that matches this schema: {schema}"})
        return payload

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        try:
            payload = self._prepare_payload(messages, json_format, schema, temperature)
            response = self.sync_client.chat.completions.create(**payload)
            if return_raw:
                return response
            return response.choices[0].message.content
        except (APIError, APIConnectionError, APITimeoutError, RateLimitError, ValueError, TypeError) as e:
            raise RuntimeError(f"OpenAI Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        try:
            payload = self._prepare_payload(messages, json_format, schema, temperature)
            response = await self.async_client.chat.completions.create(**payload)
            if return_raw:
                return response
            return response.choices[0].message.content
        except (APIError, APIConnectionError, APITimeoutError, RateLimitError, ValueError, TypeError) as e:
            raise RuntimeError(f"OpenAI Async Error: {e}") from e
