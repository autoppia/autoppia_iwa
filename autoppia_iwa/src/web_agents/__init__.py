from autoppia_iwa.src.web_agents.apified_iterative_agent import (
    ApifiedIterativeWebAgent,
    ApifiedWebAgent,
)
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent as ApifiedOneShotWebAgent

__all__ = [
    "WebAgent",
    "ApifiedWebAgent",
    "ApifiedOneShotWebAgent",
]

# New public name for the HTTP iterative web-agent interface.
WebAgent = ApifiedWebAgent
