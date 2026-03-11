from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ACT_PROTOCOL_VERSION = "1.0"


class ActExecutionMode(str, Enum):
    """Execution strategy hint for consumers of `/act` responses."""

    SINGLE_STEP = "single_step"
    BATCH = "batch"


class ActRequest(BaseModel):
    """Canonical request payload sent to `/act` endpoints."""

    model_config = ConfigDict(extra="allow")

    protocol_version: str = Field(default=ACT_PROTOCOL_VERSION)
    task_id: str | None = None
    prompt: str | None = None
    url: str | None = None
    snapshot_html: str = ""
    screenshot: str | bytes | None = None
    step_index: int = Field(default=0, ge=0)
    web_project_id: str | int | None = None
    history: list[dict[str, Any]] | None = None
    state_in: dict[str, Any] = Field(default_factory=dict)
    allowed_tools: list[dict[str, Any]] | None = None
    include_reasoning: bool = False


class ActToolCall(BaseModel):
    """Canonical tool call payload used by `/act` response."""

    model_config = ConfigDict(extra="forbid")

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


class ActResponse(BaseModel):
    """Canonical response payload returned by `/act` endpoints."""

    model_config = ConfigDict(extra="forbid")

    protocol_version: str = Field(default=ACT_PROTOCOL_VERSION)
    tool_calls: list[ActToolCall]
    content: str | None = None
    reasoning: str | None = None
    state_out: dict[str, Any] = Field(default_factory=dict)
    done: bool
    error: str | None = None

    # Optional usage tracking (included in response by agent; benchmark accumulates per task)
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_tool_calls_alias(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        # `actions` is accepted as an alias for `tool_calls`, using the same
        # schema: [{"name": "...", "arguments": {...}}].
        if "actions" in payload:
            alias_payload = payload.pop("actions")
            if "tool_calls" not in payload:
                payload["tool_calls"] = alias_payload
        return payload

    @field_validator("state_out", mode="before")
    @classmethod
    def normalize_state_out(cls, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return dict(value)
        raise ValueError("`state_out` must be a JSON object.")

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "ActResponse":
        return cls.model_validate(payload)
