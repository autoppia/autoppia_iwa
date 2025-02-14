from dependency_injector import containers, providers

from autoppia_iwa.config.config import AGENT_HOST, AGENT_NAME, AGENT_PORT
from autoppia_iwa.src.web_agents.apified_agent import ApifiedWebAgent


class TestDIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container."""

    # Configuration
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(packages=["tests"])
    web_agent = providers.Singleton(lambda: TestDIContainer._assign_agent())

    @staticmethod
    def _assign_agent() -> ApifiedWebAgent:
        if AGENT_NAME == "browser_use":
            return ApifiedWebAgent(name="browser_use_agent", host=AGENT_HOST, port=AGENT_PORT)
        if AGENT_NAME == "autoppia_agent":
            return ApifiedWebAgent(name="autoppia_agent", host=AGENT_HOST, port=AGENT_PORT)
        if AGENT_NAME == "random_agent":
            return ApifiedWebAgent(name="random_agent", host=AGENT_HOST, port=AGENT_PORT)
        raise ValueError(f"Unknown agent {AGENT_NAME}")
