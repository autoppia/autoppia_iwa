from autoppia_iwa.src.web_agents.act_protocol import ACT_PROTOCOL_VERSION, ActExecutionMode, ActRequest, ActResponse
from autoppia_iwa.src.web_agents.act_response_utils import actions_to_act_response
from autoppia_iwa.src.web_agents.apified_iterative_agent import (
    ApifiedIterativeWebAgent,
    ApifiedWebAgent,
)
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent as ApifiedOneShotWebAgent

__all__ = [
    "ACT_PROTOCOL_VERSION",
    "ActExecutionMode",
    "ActRequest",
    "ActResponse",
    "ApifiedIterativeWebAgent",
    "ApifiedOneShotWebAgent",
    "ApifiedWebAgent",
    "WebAgent",
    "actions_to_act_response",
]

# New public name for the HTTP iterative web-agent interface.
WebAgent = ApifiedWebAgent
