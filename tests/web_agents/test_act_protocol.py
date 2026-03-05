import pytest
from pydantic import ValidationError

from autoppia_iwa.src.web_agents.act_protocol import ActRequest, ActResponse


def test_act_response_accepts_canonical_tool_calls() -> None:
    parsed = ActResponse.from_raw(
        {
            "protocol_version": "1.0",
            "tool_calls": [{"name": "browser.navigate", "arguments": {"url": "https://example.com"}}],
            "content": "navigating now",
            "done": False,
            "state_out": {"phase": "browse"},
        }
    )

    assert parsed.protocol_version == "1.0"
    assert parsed.tool_calls[0].name == "browser.navigate"
    assert parsed.tool_calls[0].arguments == {"url": "https://example.com"}
    assert parsed.content == "navigating now"
    assert parsed.done is False
    assert parsed.state_out == {"phase": "browse"}


def test_act_response_requires_tool_calls() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw({"done": False, "state_out": {}})


def test_act_response_accepts_actions_alias_for_tool_calls() -> None:
    parsed = ActResponse.from_raw(
        {
            "actions": [{"name": "browser.click", "arguments": {"x": 10, "y": 20}}],
            "done": False,
            "state_out": {},
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
            "state_out": {},
        }
    )
    assert len(parsed.tool_calls) == 1
    assert parsed.tool_calls[0].name == "browser.navigate"


def test_act_request_default_state_is_empty_dict() -> None:
    request = ActRequest(task_id="task_1", snapshot_html="<html/>", step_index=0)
    assert request.state_in == {}
    assert request.allowed_tools == []


def test_act_response_normalizes_state_out_none_to_empty_dict() -> None:
    parsed = ActResponse.from_raw({"tool_calls": [], "done": True, "state_out": None})
    assert parsed.state_out == {}
