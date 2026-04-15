import pytest
from pydantic import ValidationError

from autoppia_iwa.src.web_agents.act_protocol import ActRequest, ActResponse, ActToolCall


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


def test_act_response_rejects_legacy_actions_shape_with_type_payload() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw(
            {
                "actions": [{"type": "ClickAction", "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "go"}}],
                "done": False,
                "state_out": {},
            }
        )


def test_act_tool_call_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        ActToolCall(name="", arguments={})


def test_act_tool_call_normalizes_arguments_none() -> None:
    tc = ActToolCall(name="browser.click", arguments=None)  # type: ignore[arg-type]
    assert tc.arguments == {}


def test_act_tool_call_rejects_non_object_arguments() -> None:
    with pytest.raises(ValidationError):
        ActToolCall(name="browser.click", arguments="not-a-dict")  # type: ignore[arg-type]


def test_act_response_normalize_root_non_dict_passes_through_validator() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw([])  # type: ignore[arg-type]


def test_act_response_rejects_non_object_state_out() -> None:
    with pytest.raises(ValidationError):
        ActResponse.from_raw({"tool_calls": [], "done": True, "state_out": "bad"})


def test_act_protocol_ignores_extra_fields_in_response_and_tool_call() -> None:
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [{"name": "browser.click", "arguments": {"x": 1, "y": 2}, "extra_tool_field": "ignored"}],
            "done": False,
            "state_out": {},
            "extra_response_field": "ignored",
        }
    )
    assert len(parsed.tool_calls) == 1
    assert parsed.tool_calls[0].name == "browser.click"
    assert parsed.tool_calls[0].arguments == {"x": 1, "y": 2}
