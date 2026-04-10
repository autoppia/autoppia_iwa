from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from autoppia_iwa.config.config import (
    CHUTES_API_KEY,
    CHUTES_BASE_URL,
    CHUTES_MAX_TOKENS,
    CHUTES_MODEL,
    CHUTES_TEMPERATURE,
    CHUTES_USE_BEARER,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from autoppia_iwa.src.llms.factory import LLMFactory
from autoppia_iwa.src.llms.interfaces import LLMConfig


class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container."""

    # Configuration
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(packages=["autoppia_iwa.src"])

    # LLM Service provider using Factory pattern
    llm_service = providers.Singleton(lambda: DIContainer._get_llm_service())

    @classmethod
    def register_service(cls, service_name: str, service_instance):
        """Register a new service in the dependency container."""
        if hasattr(cls, service_name):
            raise AttributeError(f"Service {service_name} is already registered.")
        setattr(cls, service_name, providers.Singleton(service_instance))

    @staticmethod
    def _get_llm_service():
        providers = {
            "openai": dict(
                config=LLMConfig(
                    model=OPENAI_MODEL,
                    temperature=OPENAI_TEMPERATURE,
                    max_tokens=OPENAI_MAX_TOKENS,
                ),
                kwargs=dict(
                    api_key=OPENAI_API_KEY,
                ),
            ),
            "chutes": dict(
                config=LLMConfig(
                    model=CHUTES_MODEL,
                    temperature=CHUTES_TEMPERATURE,
                    max_tokens=CHUTES_MAX_TOKENS,
                ),
                kwargs=dict(
                    base_url=CHUTES_BASE_URL,
                    api_key=CHUTES_API_KEY,
                    use_bearer=CHUTES_USE_BEARER,
                ),
            ),
        }

        try:
            provider = providers[LLM_PROVIDER]
        except KeyError:
            raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}") from None

        return LLMFactory.create_llm(
            llm_type=LLM_PROVIDER,
            config=provider["config"],
            **provider["kwargs"],
        )

    @classmethod
    def resolve_llm_service(cls, llm_service=None):
        """Resolve lazy/default DI values into a concrete LLM service."""
        if llm_service is None or isinstance(llm_service, Provide):
            return cls.llm_service()
        return llm_service
