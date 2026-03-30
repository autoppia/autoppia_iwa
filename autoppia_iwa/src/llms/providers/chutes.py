import httpx

from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig


class ChutesLLMService(ILLM):
    """Chutes LLM using OpenAI-compatible API via HTTPX."""

    def __init__(self, config: LLMConfig, base_url: str, api_key: str, use_bearer: bool = False):
        self.config = config
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.use_bearer = use_bearer

    def _prepare_payload(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, temperature: float | None = None) -> dict:
        payload = {
            "model": self.config.model,
            "messages": list(messages),
            "max_tokens": self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
        }
        system_prompt = None
        for msg in payload["messages"]:
            if msg["role"] == "system":
                system_prompt = msg["content"]
                payload["messages"].remove(msg)
                break
        if json_format:
            sys_prompt_content = (
                "CRITICAL: Your ONLY output must be a valid JSON array of strings. "
                'Example: ["item1", "item2", "item3"]. '
                "DO NOT include:\n"
                "- Markdown formatting (```json, ```)\n"
                "- <think> tags or any XML-like tags\n"
                "- Explanations or additional text\n"
                "- Object wrappers with keys\n"
                "- Any text before or after the array\n"
                "Return ONLY the JSON array, nothing else."
            )
            if schema:
                sys_prompt_content += f"\n\nSchema requirements: {schema}"
            system_prompt = f"{sys_prompt_content}\n\n{system_prompt}" if system_prompt else sys_prompt_content
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})
        return payload

    def _headers(self):
        if self.use_bearer:
            return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        else:
            return {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    def predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        url = f"{self.base_url}/chat/completions"
        try:
            with httpx.Client(timeout=180.0) as client:
                payload = self._prepare_payload(messages, json_format, schema, temperature)
                response = client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Chutes LLM Sync Error: {e}") from e

    async def async_predict(self, messages: list[dict[str, str]], json_format: bool = False, schema: dict | None = None, return_raw: bool = False, temperature: float | None = None) -> str:
        url = f"{self.base_url}/chat/completions"
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = self._prepare_payload(messages, json_format, schema, temperature)
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                if return_raw:
                    return data
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Chutes LLM Async Error: {e}") from e
