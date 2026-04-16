from __future__ import annotations

import pytest

from autoppia_iwa.src.llms.factory import LLMFactory
from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig
from autoppia_iwa.src.llms.providers.chutes import ChutesLLMService
from autoppia_iwa.src.llms.providers.local import LocalLLMService
from autoppia_iwa.src.llms.providers.openai import OpenAIService


def test_llm_config_defaults_are_sane():
    config = LLMConfig()
    assert config.model
    assert config.max_tokens > 0


def test_factory_builds_openai(monkeypatch):
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: object())
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())

    llm = LLMFactory.create_llm("openai", LLMConfig(), api_key="sk-test")

    assert isinstance(llm, OpenAIService)
    assert isinstance(llm, ILLM)


def test_factory_builds_local():
    llm = LLMFactory.create_llm("local", LLMConfig(model="local"), endpoint_url="http://localhost/generate")
    assert isinstance(llm, LocalLLMService)
    assert isinstance(llm, ILLM)


def test_factory_builds_chutes():
    llm = LLMFactory.create_llm("chutes", LLMConfig(model="m"), base_url="https://x.chutes.ai/v1", api_key="key", use_bearer=True)
    assert isinstance(llm, ChutesLLMService)
    assert isinstance(llm, ILLM)


def test_factory_is_case_insensitive(monkeypatch):
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.OpenAI", lambda api_key: object())
    monkeypatch.setattr("autoppia_iwa.src.llms.providers.openai.AsyncOpenAI", lambda api_key: object())

    llm = LLMFactory.create_llm("OPENAI", LLMConfig(), api_key="sk-test")

    assert isinstance(llm, OpenAIService)


def test_factory_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported LLM type"):
        LLMFactory.create_llm("missing", LLMConfig())
