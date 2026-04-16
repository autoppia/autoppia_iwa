import pytest
from pydantic import ValidationError

from autoppia_iwa.src.web_agents.act_protocol import (
    ActAllowedTool,
    ActHistoryItem,
    ActRequest,
    ActResponse,
    StepAllowedTool,
    StepHistoryItem,
)


def test_act_response_accepts_canonical_tool_calls() -> None:
    parsed = ActResponse.from_raw(
        {
            "protocol_version": "1.0",
            "tool_calls": [{"name": "browser.navigate", "arguments": {"url": "https://example.com"}}],
            "content": "navigating now",
            "done": False,
        }
    )

    assert parsed.protocol_version == "1.0"
    assert parsed.tool_calls[0].name == "browser.navigate"
    assert parsed.tool_calls[0].arguments == {"url": "https://example.com"}
    assert parsed.content == "navigating now"
    assert parsed.done is False


def test_act_response_requires_tool_calls() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw({"done": False})


def test_act_response_accepts_actions_alias_for_tool_calls() -> None:
    parsed = ActResponse.from_raw(
        {
            "actions": [{"name": "browser.click", "arguments": {"x": 10, "y": 20}}],
            "done": False,
        }
    )
    assert len(parsed.tool_calls) == 1
    assert parsed.tool_calls[0].name == "browser.click"


def test_act_response_prefers_tool_calls_when_both_fields_are_present() -> None:
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [{"name": "browser.navigate", "arguments": {"url": "https://autoppia.com"}}],
            "actions": [{"name": "browser.click", "arguments": {"x": 10, "y": 20}}],
            "done": False,
        }
    )
    assert len(parsed.tool_calls) == 1
    assert parsed.tool_calls[0].name == "browser.navigate"


def test_act_request_normalizes_legacy_fields() -> None:
    request = ActRequest(
        task_id="task_1",
        snapshot_html="<html/>",
        allowed_tools=[{"name": "browser.click"}],
        history=[{"index": 0, "success": True}],
        step_index=0,
    )
    assert request.html == "<html/>"
    assert len(request.tools) == 1
    assert request.tools[0].name == "browser.click"
    assert len(request.history or []) == 1
    assert request.history[0].success is True


def test_act_request_ignores_legacy_state_in() -> None:
    request = ActRequest(task_id="task_1", state_in={"phase": "login"})
    assert not hasattr(request, "state_in")


def test_step_request_typed_history_and_tools_are_serialized_cleanly() -> None:
    request = ActRequest(
        task_id="task_1",
        html="<html/>",
        history=[ActHistoryItem(index=1, action={"type": "ClickAction"}, success=False, error="timeout")],
        tools=[ActAllowedTool(name="browser.click", description="Click", parameters={"type": "object"})],
        screenshot=b"abc",
    )

    dumped = request.model_dump(mode="json", exclude_none=True)

    assert dumped["history"] == [{"index": 1, "action": {"type": "ClickAction"}, "success": False, "error": "timeout"}]
    assert dumped["tools"] == [{"name": "browser.click", "description": "Click", "parameters": {"type": "object"}}]
    assert dumped["screenshot"] == "abc"


def test_step_request_accepts_string_history_action_for_backward_compatibility() -> None:
    request = ActRequest(history=[{"index": 0, "action": "click", "success": True}])
    assert request.history is not None
    assert request.history[0].action == "click"


def test_step_alias_types_match_act_aliases() -> None:
    assert StepHistoryItem is ActHistoryItem
    assert StepAllowedTool is ActAllowedTool


def test_act_response_ignores_legacy_state_out() -> None:
    parsed = ActResponse.from_raw({"tool_calls": [], "done": True, "state_out": None})
    assert parsed.done is True


def test_act_response_rejects_legacy_actions_shape_with_type_payload() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw(
            {
                "actions": [{"type": "ClickAction", "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "go"}}],
                "done": False,
            }
        )
