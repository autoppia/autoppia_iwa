from unittest.mock import patch

import pytest
from dependency_injector import containers, providers

from autoppia_iwa.config.config import AGENT_HOST, AGENT_NAME, AGENT_PORT
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent


class AppDIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container."""

    # Configuration
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(packages=["tests"])
    web_agent = providers.Singleton(lambda: AppDIContainer._assign_agent())

    @staticmethod
    def _assign_agent() -> ApifiedOneShotWebAgent:
        return ApifiedOneShotWebAgent(name=AGENT_NAME, host=AGENT_HOST, port=AGENT_PORT)


def test_di_container_register_service_raises_when_already_exists():
    """register_service raises AttributeError if service name already exists."""
    from autoppia_iwa.src.di_container import DIContainer

    with pytest.raises(AttributeError, match="already registered"):
        DIContainer.register_service("llm_service", object())


def test_di_container_get_llm_service_chutes_branch():
    """_get_llm_service returns chutes LLM when LLM_PROVIDER is chutes."""
    from autoppia_iwa.src.di_container import DIContainer

    with (
        patch("autoppia_iwa.src.di_container.LLM_PROVIDER", "chutes"),
        patch("autoppia_iwa.src.di_container.CHUTES_API_KEY", "test-key"),
        patch("autoppia_iwa.src.di_container.CHUTES_BASE_URL", "https://chutes.test/v1"),
        patch("autoppia_iwa.src.di_container.CHUTES_MODEL", "test-model"),
        patch("autoppia_iwa.src.di_container.CHUTES_MAX_TOKENS", 2048),
        patch("autoppia_iwa.src.di_container.CHUTES_TEMPERATURE", 0.7),
        patch("autoppia_iwa.src.di_container.CHUTES_USE_BEARER", False),
        patch("autoppia_iwa.src.di_container.LLMFactory") as mock_factory,
    ):
        DIContainer._get_llm_service()
        mock_factory.create_llm.assert_called_once()
        call_kw = mock_factory.create_llm.call_args[1]
        assert call_kw["llm_type"] == "chutes"
        assert call_kw["api_key"] == "test-key"
        assert call_kw.get("use_bearer") is False


def test_di_container_get_llm_service_unsupported_provider_raises():
    """_get_llm_service raises ValueError for unsupported LLM_PROVIDER."""
    from autoppia_iwa.src.di_container import DIContainer

    with patch("autoppia_iwa.src.di_container.LLM_PROVIDER", "unsupported"), pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        DIContainer._get_llm_service()
