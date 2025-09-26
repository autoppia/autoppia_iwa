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

    # Initialize MongoDB client as Singleton
    # mongo_client = providers.Singleton(lambda: MongoClient(MONGODB_URL))

    # Repository of analysis results as Factory
    # analysis_repository = providers.Factory(
    #     BaseMongoRepository,
    #     mongo_client=mongo_client,
    #     db_name=MONGODB_NAME,
    #     collection_name=ANALYSIS_COLLECTION,
    # )

    # # Synthetic Task Repository
    # synthetic_task_repository = providers.Factory(
    #     BaseMongoRepository,
    #     mongo_client=mongo_client,
    #     db_name=MONGODB_NAME,
    #     collection_name=TASKS_COLLECTION,
    # )

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
            return LLMFactory.create_llm(
                llm_type="local",
                config=config,
                endpoint_url=LOCAL_MODEL_ENDPOINT,
                parallel_endpoint_url=LOCAL_PARALLEL_MODEL_ENDPOINT,
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
