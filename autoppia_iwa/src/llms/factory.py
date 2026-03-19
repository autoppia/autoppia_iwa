from autoppia_iwa.src.llms.interfaces import ILLM, LLMConfig
from autoppia_iwa.src.llms.providers.chutes import ChutesLLMService
from autoppia_iwa.src.llms.providers.local import LocalLLMService
from autoppia_iwa.src.llms.providers.openai import OpenAIService


class LLMFactory:
    """Factory to build the right LLM implementation based on llm_type."""

    @staticmethod
    def create_llm(llm_type: str, config: LLMConfig, **kwargs) -> ILLM:
        if llm_type.lower() == "openai":
            return OpenAIService(config, api_key=kwargs.get("api_key"))
        elif llm_type.lower() == "local":
            return LocalLLMService(config, endpoint_url=kwargs.get("endpoint_url"))
        elif llm_type.lower() == "chutes":
            return ChutesLLMService(config, base_url=kwargs.get("base_url"), api_key=kwargs.get("api_key"), use_bearer=kwargs.get("use_bearer", False))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
