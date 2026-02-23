from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent as ApifiedOneShotWebAgent

__all__ = [
    "ApifiedOneShotWebAgent",
    "ApifiedWebAgent",
    "WebAgent",
]

# New public name for the HTTP iterative web-agent interface.
WebAgent = ApifiedWebAgent
