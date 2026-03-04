from autoppia_iwa.src.web_agents.apified_iterative_agent import (
    ApifiedIterativeWebAgent,
    ApifiedWebAgent,
)
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent as ApifiedOneShotWebAgent
from autoppia_iwa.src.web_agents.act_protocol import ACT_PROTOCOL_VERSION, ActExecutionMode, ActRequest, ActResponse

__all__ = [
    "WebAgent",
    "ApifiedWebAgent",
    "ApifiedIterativeWebAgent",
    "ApifiedOneShotWebAgent",
    "ACT_PROTOCOL_VERSION",
    "ActExecutionMode",
    "ActRequest",
    "ActResponse",
]

# New public name for the HTTP iterative web-agent interface.
WebAgent = ApifiedWebAgent
