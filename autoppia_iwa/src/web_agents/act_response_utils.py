"""
Convert list[BaseAction] to ActResponse (IWA /act response format).

Used by agents that return BaseAction instances so they can serve HTTP /act
responses in the format expected by ApifiedWebAgent: tool_calls with
namespaced names (browser.<action_type> or user.request_input).
"""

from typing import TYPE_CHECKING

from autoppia_iwa.src.web_agents.act_protocol import ActResponse, ActToolCall

if TYPE_CHECKING:
    from autoppia_iwa.src.execution.actions.base import BaseAction


def actions_to_act_response(
    actions: list["BaseAction"],
    done: bool = False,
    content: str | None = None,
    reasoning: str | None = None,
    state_out: dict | None = None,
    error: str | None = None,
) -> ActResponse:
    """
    Build an ActResponse from a list of BaseAction instances.

    Each action's to_tool_call() gives {name, arguments}; the name is
    namespaced to match what ApifiedWebAgent expects: "browser.<name>"
    or "user.request_input" for request_user_input.
    """
    from autoppia_iwa.src.execution.actions.base import BaseAction

    tool_calls: list[ActToolCall] = []
    for action in actions:
        if not isinstance(action, BaseAction):
            continue
        raw = action.to_tool_call()
        name = str(raw.get("name") or "").strip()
        if not name:
            continue
        arguments = raw.get("arguments")
        if not isinstance(arguments, dict):
            arguments = {}
        namespaced_name = "user.request_input" if name == "request_user_input" else f"browser.{name}"
        tool_calls.append(ActToolCall(name=namespaced_name, arguments=arguments))

    return ActResponse(
        tool_calls=tool_calls,
        done=done,
        content=content,
        reasoning=reasoning,
        state_out=state_out or {},
        error=error,
    )
