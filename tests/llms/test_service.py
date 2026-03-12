"""Unit tests for llms.service (_prepare_payload, LLMFactory, predict with mocks)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.llms.interfaces import LLMConfig
from autoppia_iwa.src.llms.service import (
    ChutesLLMService,
    LLMFactory,
    LocalLLMService,
    OpenAIService,
)


class TestOpenAIServicePreparePayload:
    """Tests for OpenAIService._prepare_payload (and predict with mocked client)."""

    def test_prepare_payload_default(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.7, max_tokens=1000)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            svc = OpenAIService(config, api_key="sk-test")
        messages = [{"role": "user", "content": "Hello"}]
        payload = svc._prepare_payload(messages)
        assert payload["model"] == "gpt-4o-mini"
        assert payload["temperature"] == 0.7
        assert payload["max_tokens"] == 1000
        assert payload["messages"] == messages

    def test_prepare_payload_with_temperature_override(self):
        config = LLMConfig(model="gpt-4o", temperature=0.5, max_tokens=500)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            svc = OpenAIService(config, api_key="sk-test")
        payload = svc._prepare_payload([{"role": "user", "content": "Hi"}], temperature=0.9)
        assert payload["temperature"] == 0.9

    def test_prepare_payload_json_format_and_schema(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as mock_openai:
            mock_openai.return_value = MagicMock()
            svc = OpenAIService(config, api_key="sk-test")
        messages = [{"role": "user", "content": "List items"}]
        schema = {"type": "array", "items": {"type": "string"}}
        payload = svc._prepare_payload(messages, json_format=True, schema=schema)
        assert payload.get("response_format") == {"type": "json_object"}
        assert any(m.get("role") == "system" for m in payload["messages"])

    def test_predict_returns_content_and_raises_on_api_error(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from API"
        with patch("autoppia_iwa.src.llms.service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            svc = OpenAIService(config, api_key="sk-test")
        result = svc.predict([{"role": "user", "content": "Hi"}])
        assert result == "Hello from API"

    def test_predict_wraps_exception_in_runtime_error(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = ValueError("API error")
            MockOpenAI.return_value = mock_client
            svc = OpenAIService(config, api_key="sk-test")
        with pytest.raises(RuntimeError) as exc_info:
            svc.predict([{"role": "user", "content": "Hi"}])
        assert "OpenAI Sync Error" in str(exc_info.value)

    def test_predict_return_raw_returns_response_object(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "text"
        with patch("autoppia_iwa.src.llms.service.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            MockOpenAI.return_value = mock_client
            svc = OpenAIService(config, api_key="sk-test")
        result = svc.predict([{"role": "user", "content": "Hi"}], return_raw=True)
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_async_predict_return_raw_returns_response_object(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0.0, max_tokens=100)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "async text"
        with patch("autoppia_iwa.src.llms.service.AsyncOpenAI") as MockAsyncOpenAI:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            MockAsyncOpenAI.return_value = mock_client
            svc = OpenAIService(config, api_key="sk-test")
        result = await svc.async_predict([{"role": "user", "content": "Hi"}], return_raw=True)
        assert result is mock_response


class TestLocalLLMServicePreparePayload:
    """Tests for LocalLLMService._prepare_payload."""

    def test_prepare_payload_includes_messages_and_temperature(self):
        config = LLMConfig(model="local", temperature=0.8, max_tokens=500)
        svc = LocalLLMService(config, endpoint_url="http://localhost:8000/generate")
        payload = svc._prepare_payload([{"role": "user", "content": "Hi"}])
        assert payload["messages"] == [{"role": "user", "content": "Hi"}]
        assert payload["temperature"] == 0.8
        assert payload["max_tokens"] == 500

    def test_prepare_payload_json_format_and_schema(self):
        config = LLMConfig(model="local", temperature=0.0, max_tokens=100)
        svc = LocalLLMService(config, endpoint_url="http://localhost/generate")
        payload = svc._prepare_payload([], json_format=True, schema={"key": "value"})
        assert payload["json_format"] is True
        assert payload["schema"] == {"key": "value"}


class TestChutesLLMService:
    """Tests for ChutesLLMService _prepare_payload and _headers."""

    def test_prepare_payload_basic(self):
        config = LLMConfig(model="meta-llama/Llama-3.1-8B", temperature=0.7, max_tokens=2048)
        svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="key", use_bearer=False)
        payload = svc._prepare_payload([{"role": "user", "content": "Hi"}])
        assert payload["model"] == config.model
        assert payload["messages"] == [{"role": "user", "content": "Hi"}]

    def test_headers_x_api_key_when_not_bearer(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="mykey", use_bearer=False)
        assert svc._headers()["X-API-Key"] == "mykey"
        assert "Authorization" not in svc._headers() or "Bearer" not in svc._headers().get("Authorization", "")

    def test_headers_bearer_when_use_bearer_true(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="mykey", use_bearer=True)
        assert svc._headers()["Authorization"] == "Bearer mykey"

    def test_prepare_payload_with_system_message_and_json_format(self):
        """Covers Chutes _prepare_payload when messages have system role and json_format/schema (lines 166-182)."""
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="key", use_bearer=False)
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "List items"},
        ]
        payload = svc._prepare_payload(messages, json_format=True, schema={"type": "array"})
        assert payload["messages"][0]["role"] == "system"
        assert "CRITICAL" in payload["messages"][0]["content"] or "JSON" in payload["messages"][0]["content"]
        assert len(payload["messages"]) == 2

    def test_predict_return_raw_returns_full_response(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        full_data = {"choices": [{"message": {"content": "hi"}}], "usage": {}}
        with patch("autoppia_iwa.src.llms.service.httpx") as mock_httpx:
            mock_httpx.Client.return_value.__enter__.return_value.post.return_value.json.return_value = full_data
            mock_httpx.Client.return_value.__enter__.return_value.post.return_value.raise_for_status = MagicMock()
            svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="key")
            result = svc.predict([{"role": "user", "content": "Hi"}], return_raw=True)
        assert result == full_data

    @pytest.mark.asyncio
    async def test_async_predict_return_raw_returns_full_response(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        full_data = {"choices": [{"message": {"content": "hi"}}], "usage": {}}
        mock_post = MagicMock()
        mock_post.raise_for_status = MagicMock()
        mock_post.json = MagicMock(return_value=full_data)
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_post)
        with patch("autoppia_iwa.src.llms.service.httpx") as mock_httpx:
            mock_httpx.AsyncClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_httpx.AsyncClient.return_value.__aexit__ = AsyncMock(return_value=None)
            svc = ChutesLLMService(config, base_url="https://x.chutes.ai/v1", api_key="key")
            result = await svc.async_predict([{"role": "user", "content": "Hi"}], return_raw=True)
        assert result == full_data


class TestLLMFactory:
    """Tests for LLMFactory.create_llm."""

    def test_create_openai(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0, max_tokens=10)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = MagicMock()
            llm = LLMFactory.create_llm("openai", config, api_key="sk-x")
        assert isinstance(llm, OpenAIService)

    def test_create_local(self):
        config = LLMConfig(model="local", temperature=0, max_tokens=10)
        llm = LLMFactory.create_llm("local", config, endpoint_url="http://localhost/generate")
        assert isinstance(llm, LocalLLMService)

    def test_create_chutes(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        llm = LLMFactory.create_llm(
            "chutes",
            config,
            base_url="https://x.chutes.ai/v1",
            api_key="key",
            use_bearer=True,
        )
        assert isinstance(llm, ChutesLLMService)

    def test_unsupported_type_raises(self):
        config = LLMConfig(model="m", temperature=0, max_tokens=10)
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("unknown", config)
        assert "Unsupported LLM type" in str(exc_info.value)

    def test_case_insensitive_openai(self):
        config = LLMConfig(model="gpt-4o-mini", temperature=0, max_tokens=10)
        with patch("autoppia_iwa.src.llms.service.OpenAI") as MockOpenAI:
            MockOpenAI.return_value = MagicMock()
            llm = LLMFactory.create_llm("OPENAI", config, api_key="sk-x")
        assert isinstance(llm, OpenAIService)
