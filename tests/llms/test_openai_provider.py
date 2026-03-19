from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from autoppia_iwa.src.llms.interfaces import LLMConfig
from autoppia_iwa.src.llms.providers.openai import OpenAIService


def _make_openai_response(content: str):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_prepare_payload_does_not_mutate_input_messages(monkeypatch):
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: object())
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())
    service = OpenAIService(LLMConfig(model="gpt-4o-mini", temperature=0.2, max_tokens=128), api_key="sk-test")

    messages = [{"role": "user", "content": "hi"}]
    payload = service._prepare_payload(messages, json_format=True, schema={"type": "object"})

    assert messages == [{"role": "user", "content": "hi"}]
    assert payload["messages"][0]["role"] == "system"
    assert payload["response_format"] == {"type": "json_object"}


def test_predict_returns_message_content(monkeypatch):
    sync_client = Mock()
    sync_client.chat.completions.create.return_value = _make_openai_response("hello")
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: sync_client)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())

    service = OpenAIService(LLMConfig(), api_key="sk-test")

    assert service.predict([{"role": "user", "content": "hi"}]) == "hello"


def test_predict_return_raw_returns_response(monkeypatch):
    response = _make_openai_response("hello")
    sync_client = Mock()
    sync_client.chat.completions.create.return_value = response
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: sync_client)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())

    service = OpenAIService(LLMConfig(), api_key="sk-test")

    assert service.predict([{"role": "user", "content": "hi"}], return_raw=True) is response


@pytest.mark.asyncio
async def test_async_predict_returns_message_content(monkeypatch):
    async_client = Mock()
    async_client.chat.completions.create = AsyncMock(return_value=_make_openai_response("async hello"))
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: object())
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: async_client)

    service = OpenAIService(LLMConfig(), api_key="sk-test")

    assert await service.async_predict([{"role": "user", "content": "hi"}]) == "async hello"


def test_predict_wraps_errors(monkeypatch):
    sync_client = Mock()
    sync_client.chat.completions.create.side_effect = ValueError("boom")
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: sync_client)
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())

    service = OpenAIService(LLMConfig(), api_key="sk-test")

    with pytest.raises(RuntimeError, match="OpenAI Sync Error"):
        service.predict([{"role": "user", "content": "hi"}])
