import httpx

from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig


class LocalLLMService(ILLM):
    """Local (self-hosted) LLM that communicates via HTTP using HTTPX."""

    def __init__(self, config: LLMConfig, endpoint_url: str):
        self.config = config
        self.endpoint_url = endpoint_url

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, temperature: float | None = None) -> dict:
        payload = {
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if json_format:
            payload["json_format"] = True
        if schema:
            payload["schema"] = schema
        return payload

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        try:
            with httpx.Client(timeout=180.0) as client:
                payload = self._prepare_payload(messages, json_format, schema, temperature)
                response = client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data.get("output", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Local LLM Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = self._prepare_payload(messages, json_format, schema, temperature)
                response = await client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data.get("output", "")
        except httpx.HTTPError as e:
            raise RuntimeError(f"Local LLM Async Error: {e}") from e
