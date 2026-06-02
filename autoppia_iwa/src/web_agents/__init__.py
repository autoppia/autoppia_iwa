from autoppia_iwa.src.web_agents.apified_harvester import ApifiedHarvester
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent
from autoppia_iwa.src.web_agents.apified_web_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.classes import IHarvester, TaskSolution, Trajectory, TrajectoryResult
from autoppia_iwa.src.web_agents.interfaces import (
    AsyncTaskExecutionSession,
    AsyncWebAgentSession,
    BrowserSnapshot,
    ScoreDetails,
    StepResult,
    TaskExecutionSessionProtocol,
    WebAgentSession,
)
from autoppia_iwa.src.web_agents.protocol import (
    STEP_PROTOCOL_VERSION,
    StepAllowedTool,
    StepExecutionMode,
    StepHistoryItem,
    StepRequest,
    StepResponse,
)

# Backward compat aliases
ApifiedIterativeWebAgent = ApifiedWebAgent
WebAgent = ApifiedWebAgent

__all__ = [
    "STEP_PROTOCOL_VERSION",
    "ApifiedHarvester",
    "ApifiedIterativeWebAgent",
    "ApifiedOneShotWebAgent",
    "ApifiedWebAgent",
    "AsyncTaskExecutionSession",
    "AsyncWebAgentSession",
    "BrowserSnapshot",
    "IHarvester",
    "ScoreDetails",
    "StepAllowedTool",
    "StepExecutionMode",
    "StepHistoryItem",
    "StepRequest",
    "StepResponse",
    "StepResult",
    "TaskExecutionSessionProtocol",
    "TaskSolution",
    "Trajectory",
    "TrajectoryResult",
    "WebAgent",
    "WebAgentSession",
]
