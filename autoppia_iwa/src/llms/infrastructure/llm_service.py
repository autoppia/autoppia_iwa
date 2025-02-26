
# llms.py

from typing import Dict, List, Optional

import httpx
from openai import OpenAI, AsyncOpenAI

from autoppia_iwa.src.llms.domain.interfaces import ILLM, LLMConfig
import time
import httpx


# In llms.py

class OpenAIService(ILLM):
    """
    Simple OpenAI-based LLM.
    Uses OpenAI (sync) and AsyncOpenAI (async) clients.
    """

    def __init__(self, config: LLMConfig, api_key: str):
        self.config = config
        self.sync_client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

    def _prepare_json_schema(self, schema: Dict) -> Dict:
        """
        Prepares the JSON schema for OpenAI's format requirements.
        """
        return {
            "type": "object",
            "properties": {
                "schema": {
                    "type": "string",
                    "enum": ["JSON_SCHEMA"]
                },
                "response": schema
            },
            "required": ["schema", "response"]
        }

    def predict(
        self,
        messages: List[Dict[str, str]],
        json_format: bool = False,
        schema: Optional[Dict] = None
    ) -> str:
        try:
            params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            if json_format and schema:
                params["response_format"] = {
                    "type": "json_object"
                }
                # Add system message for JSON structure
                messages.insert(0, {
                    "role": "system",
                    "content": f"You must respond with JSON that matches this schema: {schema}"
                })
                params["messages"] = messages

            response = self.sync_client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI Sync Error: {e}")

    async def async_predict(
        self,
        messages: List[Dict[str, str]],
        json_format: bool = False,
        schema: Optional[Dict] = None
    ) -> str:
        try:
            params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            if json_format and schema:
                params["response_format"] = {
                    "type": "json_object"
                }
                # Add system message for JSON structure
                messages.insert(0, {
                    "role": "system",
                    "content": f"You must respond with JSON that matches this schema: {schema}"
                })
                params["messages"] = messages

            response = await self.async_client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI Async Error: {e}")


class LocalLLMService(ILLM):
    """
    Simple local (self-hosted) LLM that communicates via HTTP.
    Uses HTTPX for sync and async calls.
    """

    def __init__(self, config: LLMConfig, endpoint_url: str):
        self.config = config
        self.endpoint_url = endpoint_url

    def predict(
        self,
        messages: List[Dict[str, str]],
        json_format: bool = False,
        schema: Optional[Dict] = None
    ) -> str:
        start_time = time.time()
        try:
            with httpx.Client(timeout=120.0) as client:
                payload = {
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                }
                if json_format:
                    payload["json_format"] = True
                if schema:
                    payload["schema"] = schema

                response = client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                output = response.json().get("output", "")
                return output
        except httpx.HTTPError as e:
            raise RuntimeError(f"Local LLM Sync Error: {e}")
        finally:
            elapsed_time = time.time() - start_time
            # print(f"Sync request took {elapsed_time:.2f} seconds.")

    async def async_predict(
        self,
        messages: List[Dict[str, str]],
        json_format: bool = False,
        schema: Optional[Dict] = None
    ) -> str:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                payload = {
                    "messages": messages,
                    "temperature": self.config.temperature,
                    "max_tokens": self.config.max_tokens,
                }
                if json_format:
                    payload["json_format"] = "json"
                if schema:
                    payload["schema"] = schema

                response = await client.post(self.endpoint_url, json=payload)
                response.raise_for_status()
                output = response.json().get("output", "")
                return output
            except httpx.HTTPError as e:
                raise RuntimeError(f"Local LLM Async Error: {e}")
            finally:
                elapsed_time = time.time() - start_time


class LLMFactory:
    """
    Simple factory to build the right LLM implementation
    based on the llm_type.
    """

    @staticmethod
    def create_llm(
        llm_type: str,
        config: LLMConfig,
        **kwargs
    ) -> ILLM:
        if llm_type.lower() == "openai":
            return OpenAIService(config, api_key=kwargs.get("api_key"))
        elif llm_type.lower() == "local":
            return LocalLLMService(config, endpoint_url=kwargs.get("endpoint_url"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
