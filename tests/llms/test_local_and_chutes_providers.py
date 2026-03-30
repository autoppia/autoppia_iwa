from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from autoppia_iwa.src.llms.interfaces import LLMConfig
from autoppia_iwa.src.llms.providers.chutes import ChutesLLMService
from autoppia_iwa.src.llms.providers.local import LocalLLMService


def test_local_prepare_payload_and_predict_return_raw(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"output": "hello", "meta": {"ok": True}}
    client = Mock()
    client.post.return_value = response
    httpx_client = Mock()
    httpx_client.__enter__ = Mock(return_value=client)
    httpx_client.__exit__ = Mock(return_value=None)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.local.httpx.Client", Mock(return_value=httpx_client))

    service = LocalLLMService(LLMConfig(model="local"), endpoint_url="http://localhost/generate")

    payload = service._prepare_payload([{"role": "user", "content": "hi"}], json_format=True, schema={"type": "object"})
    assert payload["json_format"] is True
    assert payload["schema"] == {"type": "object"}
    assert service.predict([{"role": "user", "content": "hi"}], return_raw=True) == {"output": "hello", "meta": {"ok": True}}


@pytest.mark.asyncio
async def test_local_async_predict_returns_output(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"output": "async hello"}
    client = Mock()
    client.post = AsyncMock(return_value=response)
    async_ctx = Mock()
    async_ctx.__aenter__ = AsyncMock(return_value=client)
    async_ctx.__aexit__ = AsyncMock(return_value=None)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.local.httpx.AsyncClient", Mock(return_value=async_ctx))

    service = LocalLLMService(LLMConfig(model="local"), endpoint_url="http://localhost/generate")

    assert await service.async_predict([{"role": "user", "content": "hi"}]) == "async hello"


def test_chutes_headers_and_system_prompt_behavior():
    service = ChutesLLMService(LLMConfig(model="m"), base_url="https://x.chutes.ai/v1/", api_key="key", use_bearer=True)
    assert service.base_url == "https://x.chutes.ai/v1"
    assert service._headers()["Authorization"] == "Bearer key"

    payload = service._prepare_payload(
        [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "List items"},
        ],
        json_format=True,
        schema={"type": "array"},
    )
    assert payload["messages"][0]["role"] == "system"
    assert "CRITICAL" in payload["messages"][0]["content"]
    assert payload["messages"][1]["role"] == "user"


def test_chutes_predict_uses_httpx_response(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"choices": [{"message": {"content": "hello"}}]}
    client = Mock()
    client.post.return_value = response
    httpx_client = Mock()
    httpx_client.__enter__ = Mock(return_value=client)
    httpx_client.__exit__ = Mock(return_value=None)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.chutes.httpx.Client", Mock(return_value=httpx_client))

    service = ChutesLLMService(LLMConfig(model="m"), base_url="https://x.chutes.ai/v1", api_key="key")

    assert service.predict([{"role": "user", "content": "hi"}]) == "hello"


@pytest.mark.asyncio
async def test_chutes_async_predict_return_raw(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"choices": [{"message": {"content": "hello"}}], "usage": {"prompt_tokens": 1}}
    client = Mock()
    client.post = AsyncMock(return_value=response)
    async_ctx = Mock()
    async_ctx.__aenter__ = AsyncMock(return_value=client)
    async_ctx.__aexit__ = AsyncMock(return_value=None)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.chutes.httpx.AsyncClient", Mock(return_value=async_ctx))

    service = ChutesLLMService(LLMConfig(model="m"), base_url="https://x.chutes.ai/v1", api_key="key")

    result = await service.async_predict([{"role": "user", "content": "hi"}], return_raw=True)
    assert result["usage"]["prompt_tokens"] == 1
