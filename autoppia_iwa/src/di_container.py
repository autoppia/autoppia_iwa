from dependency_injector import containers, providers

from autoppia_iwa.config.config import (
    GENERATE_MILESTONES,
    LLM_PROVIDER,
    LOCAL_MODEL_ENDPOINT,
    LOCAL_PARALLEL_MODEL_ENDPOINT,
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from autoppia_iwa.src.llms.infrastructure.llm_service import LLMConfig, LLMFactory


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
        config = LLMConfig(
            model=OPENAI_MODEL if LLM_PROVIDER == "openai" else "local",
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
        )

        return LLMFactory.create_llm(
            llm_type=LLM_PROVIDER,
            config=config,
            api_key=OPENAI_API_KEY,
            endpoint_url=LOCAL_MODEL_ENDPOINT,
            parallel_endpoint_url=LOCAL_PARALLEL_MODEL_ENDPOINT,
        )
