import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    include_reasoning: bool = False


class ActResponse(BaseModel):
    """Canonical response payload returned by `/act` endpoints."""

    model_config = ConfigDict(extra="allow")

    protocol_version: str = Field(default=ACT_PROTOCOL_VERSION)
    execution_mode: ActExecutionMode = Field(default=ActExecutionMode.BATCH)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    reasoning: str | None = None
    done: bool = False
    error: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, payload: Any) -> Any:
        if not isinstance(payload, dict):
            raise ValueError("ActResponse payload must be a JSON object.")

        normalized = dict(payload)
        normalized.setdefault("protocol_version", ACT_PROTOCOL_VERSION)
        normalized["actions"] = _extract_actions(normalized)
        return normalized

    @classmethod
    def from_raw(cls, payload: dict[str, Any]) -> "ActResponse":
        return cls.model_validate(payload)


def _extract_actions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("actions"), list):
        return [action for action in payload["actions"] if isinstance(action, dict)]

    if isinstance(payload.get("action"), dict):
        return [payload["action"]]

    if isinstance(payload.get("navigate_url"), str):
        return [{"type": "NavigateAction", "url": payload["navigate_url"]}]

    function_call = payload.get("function_call")
    if function_call:
        normalized = _normalize_tool_call(function_call)
        return [normalized] if normalized else []

    tool_calls = payload.get("tool_calls")
    if isinstance(tool_calls, list):
        actions: list[dict[str, Any]] = []
        for tool_call in tool_calls:
            normalized = _normalize_tool_call(tool_call)
            if normalized:
                actions.append(normalized)
        return actions

    return []


def _normalize_tool_call(tool_call: Any) -> dict[str, Any] | None:
    if not isinstance(tool_call, dict):
        return None

    function_payload = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else tool_call
    name = function_payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return None

    arguments = _parse_tool_arguments(function_payload.get("arguments"))
    normalized = dict(arguments)
    normalized["type"] = normalized.get("type", name.strip())
    return normalized


def _parse_tool_arguments(raw_arguments: Any) -> dict[str, Any]:
    if isinstance(raw_arguments, dict):
        return dict(raw_arguments)

    if isinstance(raw_arguments, str):
        serialized = raw_arguments.strip()
        if not serialized:
            return {}
        try:
            parsed = json.loads(serialized)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}

    return {}
