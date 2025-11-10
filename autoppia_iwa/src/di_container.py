import os

from dependency_injector import containers, providers

from autoppia_iwa.config.config import (
    CHUTES_API_KEY,
    CHUTES_BASE_URL,
    CHUTES_MAX_TOKENS,
    CHUTES_MODEL,
    CHUTES_TEMPERATURE,
    CHUTES_USE_BEARER,
    GENERATE_MILESTONES,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from autoppia_iwa.src.llms.service import LLMConfig, LLMFactory


class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container."""

    # Configuration
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(packages=["autoppia_iwa.src"])

    # LLM Service provider using Factory pattern
    llm_service = providers.Singleton(lambda: DIContainer._get_llm_service())

    # Milestone Configuration
    generate_milestones = GENERATE_MILESTONES

    @classmethod
    def register_service(cls, service_name: str, service_instance):
        """Register a new service in the dependency container."""
        if hasattr(cls, service_name):
            raise AttributeError(f"Service {service_name} is already registered.")
        setattr(cls, service_name, providers.Singleton(service_instance))

    @staticmethod
    def _get_llm_service():
        if LLM_PROVIDER == "openai":
            config = LLMConfig(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
            )
            return LLMFactory.create_llm(
                llm_type="openai",
                config=config,
                api_key=OPENAI_API_KEY,
            )
        elif LLM_PROVIDER == "local":
            config = LLMConfig(
                model="local",
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
            )
            endpoint_url = os.getenv("LOCAL_MODEL_ENDPOINT")
            parallel_endpoint_url = os.getenv("LOCAL_PARALLEL_MODEL_ENDPOINT")
            if not endpoint_url:
                raise ValueError("LOCAL_MODEL_ENDPOINT must be set when LLM_PROVIDER='local'")
            return LLMFactory.create_llm(
                llm_type="local",
                config=config,
                endpoint_url=endpoint_url,
                parallel_endpoint_url=parallel_endpoint_url,
            )
        elif LLM_PROVIDER == "chutes":
            config = LLMConfig(
                model=CHUTES_MODEL,
                temperature=CHUTES_TEMPERATURE,
                max_tokens=CHUTES_MAX_TOKENS,
            )
            return LLMFactory.create_llm(
                llm_type="chutes",
                config=config,
                base_url=CHUTES_BASE_URL,
                api_key=CHUTES_API_KEY,
                use_bearer=CHUTES_USE_BEARER,
            )
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
