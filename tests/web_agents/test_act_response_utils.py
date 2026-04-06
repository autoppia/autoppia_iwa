"""Tests for act_response_utils.actions_to_act_response."""

from unittest.mock import patch

from autoppia_iwa.src.execution.actions.actions import NavigateAction, RequestUserInputAction
from autoppia_iwa.src.web_agents.act_response_utils import actions_to_act_response


def test_actions_to_act_response_namespaces_browser_tool() -> None:
    nav = NavigateAction(type="NavigateAction", url="https://example.com/p")
    resp = actions_to_act_response(
        [nav],
        done=True,
        content="ok",
        reasoning="because",
        state_out={"k": 1},
        error=None,
    )
    assert resp.done is True
    assert resp.content == "ok"
    assert resp.reasoning == "because"
    assert resp.state_out == {"k": 1}
    assert resp.error is None
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "browser.navigate"
    assert "url" in resp.tool_calls[0].arguments


def test_actions_to_act_response_maps_request_user_input() -> None:
    req = RequestUserInputAction(type="RequestUserInputAction", prompt="OTP?")
    resp = actions_to_act_response([req])
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "user.request_input"


def test_actions_to_act_response_skips_non_base_action() -> None:
    class NotAnAction:
        def to_tool_call(self) -> dict:
            return {"name": "navigate", "arguments": {}}

    nav = NavigateAction(type="NavigateAction", url="/x")
    resp = actions_to_act_response([NotAnAction(), nav])  # type: ignore[list-item]
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "browser.navigate"


def test_actions_to_act_response_skips_empty_tool_name() -> None:
    nav = NavigateAction(type="NavigateAction", url="/x")
    with patch.object(nav, "to_tool_call", return_value={"name": "", "arguments": {}}):
        resp = actions_to_act_response([nav])
    assert resp.tool_calls == []


def test_actions_to_act_response_normalizes_non_dict_arguments() -> None:
    nav = NavigateAction(type="NavigateAction", url="/x")
    with patch.object(nav, "to_tool_call", return_value={"name": "navigate", "arguments": None}):
        resp = actions_to_act_response([nav])
    assert resp.tool_calls[0].arguments == {}


def test_actions_to_act_response_default_state_out() -> None:
    nav = NavigateAction(type="NavigateAction", url="/x")
    resp = actions_to_act_response([nav], state_out=None)
    assert resp.state_out == {}
