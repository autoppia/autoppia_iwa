from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

STEP_PROTOCOL_VERSION = "1.0"


class StepExecutionMode(str, Enum):
    """Execution strategy hint for consumers of /step responses."""

    SINGLE_STEP = "single_step"
    BATCH = "batch"


class StepHistoryItem(BaseModel):
    """Compact execution-history item sent back to the agent on later /step calls."""

    model_config = ConfigDict(extra="allow")

    index: int | None = Field(default=None, ge=0)
    action: dict[str, Any] | str | None = None
    success: bool | None = None
    error: str | None = None

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, value: Any) -> dict[str, Any] | str | None:
        if value is None:
            return None
        if isinstance(value, dict):
            return dict(value)
        if isinstance(value, str):
            return value
        raise ValueError("history item `action` must be a JSON object or string when provided.")


class StepAllowedTool(BaseModel):
    """Tool definition advertised to the agent in the /step request."""

    model_config = ConfigDict(extra="allow")

    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = str(value or "").strip()
        if not name:
            raise ValueError("allowed tool `name` must be a non-empty string.")
        return name

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    @field_validator("parameters", mode="before")
    @classmethod
    def normalize_parameters(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        raise ValueError("allowed tool `parameters` must be a JSON object.")


class StepRequest(BaseModel):
    """Canonical request payload sent to /step endpoints."""

    model_config = ConfigDict(extra="allow")

    protocol_version: str = Field(default=STEP_PROTOCOL_VERSION)
    task_id: str | None = None
    prompt: str | None = None
    url: str | None = None
    html: str = ""
    screenshot: str | bytes | None = None
    step_index: int = Field(default=0, ge=0)
    history: list[StepHistoryItem] | None = None
    tools: list[StepAllowedTool] = Field(default_factory=list)
    include_reasoning: bool = False

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_request_fields(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        if "html" not in payload and "snapshot_html" in payload:
            payload["html"] = payload.pop("snapshot_html")
        if "tools" not in payload and "allowed_tools" in payload:
            payload["tools"] = payload.pop("allowed_tools")
        payload.pop("state_in", None)
        payload.pop("web_project_id", None)
        return payload


class StepToolCall(BaseModel):
    """Canonical tool call payload used by /step response."""

    model_config = ConfigDict(extra="ignore")

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = str(value or "").strip()
        if not name:
            raise ValueError("tool call `name` must be a non-empty string.")
        return name

    @field_validator("arguments", mode="before")
    @classmethod
    def normalize_arguments(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        raise ValueError("tool call `arguments` must be a JSON object.")


class StepResponse(BaseModel):
    """Canonical response payload returned by /step endpoints."""

    model_config = ConfigDict(extra="ignore")

    protocol_version: str = Field(default=STEP_PROTOCOL_VERSION)
    tool_calls: list[StepToolCall]
    content: str | None = None
    reasoning: str | None = None
    done: bool
    error: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_tool_calls_alias(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        if "actions" in payload:
            alias_payload = payload.pop("actions")
            if "tool_calls" not in payload:
                payload["tool_calls"] = alias_payload
        payload.pop("state_out", None)
        return payload

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "StepResponse":
        return cls.model_validate(payload)


# Backward compat aliases
ACT_PROTOCOL_VERSION = STEP_PROTOCOL_VERSION
ActExecutionMode = StepExecutionMode
ActHistoryItem = StepHistoryItem
ActAllowedTool = StepAllowedTool
ActRequest = StepRequest
ActToolCall = StepToolCall
ActResponse = StepResponse
