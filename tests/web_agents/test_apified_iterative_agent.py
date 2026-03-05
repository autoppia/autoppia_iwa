from types import SimpleNamespace

from autoppia_iwa.src.execution.actions.actions import NavigateAction, RequestUserInputAction
from autoppia_iwa.src.web_agents.act_protocol import ActResponse
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent


def test_parse_actions_response_rewrites_navigate_from_browser_tool_call() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [
                {"name": "browser.navigate", "arguments": {"url": "/dashboard"}},
                {"name": "browser.click", "arguments": {"x": 10, "y": 20}},
            ],
            "done": False,
            "state_out": {},
        }
    )

    parsed_actions = agent._parse_actions_response(parsed)

    assert len(parsed_actions) == 2
    assert isinstance(parsed_actions[0], NavigateAction)
    assert parsed_actions[0].url == agent._rewrite_to_remote("/dashboard")


def test_parse_actions_response_returns_empty_when_done_true_and_no_tool_calls() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    parsed = ActResponse.from_raw({"tool_calls": [], "done": True, "state_out": {}, "reasoning": "finished"})
    parsed_actions = agent._parse_actions_response(parsed)
    assert parsed_actions == []


def test_parse_actions_response_returns_batch_by_default() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [
                {"name": "browser.navigate", "arguments": {"url": "/a"}},
                {"name": "browser.navigate", "arguments": {"url": "/b"}},
            ],
            "done": False,
            "state_out": {},
        }
    )

    parsed_actions = agent._parse_actions_response(parsed)

    assert len(parsed_actions) == 2
    assert isinstance(parsed_actions[0], NavigateAction)
    assert isinstance(parsed_actions[1], NavigateAction)


def test_parse_actions_response_honors_max_actions_per_step() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060", max_actions_per_step=1)
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [
                {"name": "browser.navigate", "arguments": {"url": "/a"}},
                {"name": "browser.navigate", "arguments": {"url": "/b"}},
            ],
            "done": False,
            "state_out": {},
        }
    )

    parsed_actions = agent._parse_actions_response(parsed)

    assert len(parsed_actions) == 1
    assert isinstance(parsed_actions[0], NavigateAction)
    assert parsed_actions[0].url == agent._rewrite_to_remote("/a")


def test_max_actions_per_step_rejects_invalid_values() -> None:
    try:
        ApifiedWebAgent(base_url="http://127.0.0.1:5060", max_actions_per_step=0)
    except ValueError as exc:
        assert "max_actions_per_step must be greater than 0" in str(exc)
        return
    raise AssertionError("Expected ValueError for max_actions_per_step=0")


def test_resolve_state_starts_empty_and_keeps_latest_state_per_task() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    task = SimpleNamespace(id="task_1")

    first = agent._resolve_state_for_step(task=task, step_index=0, state=None)
    assert first == {}

    second = agent._resolve_state_for_step(task=task, step_index=1, state={"phase": "browse"})
    assert second == {"phase": "browse"}

    third = agent._resolve_state_for_step(task=task, step_index=2, state=None)
    assert third == {"phase": "browse"}


def test_resolve_state_resets_when_task_changes() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    task_1 = SimpleNamespace(id="task_1")
    task_2 = SimpleNamespace(id="task_2")

    _ = agent._resolve_state_for_step(task=task_1, step_index=0, state={"phase": "extract"})
    reset = agent._resolve_state_for_step(task=task_2, step_index=1, state=None)

    assert reset == {}


def test_parse_actions_response_maps_user_request_input_tool() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
    parsed = ActResponse.from_raw(
        {
            "tool_calls": [{"name": "user.request_input", "arguments": {"prompt": "Need OTP"}}],
            "done": False,
            "state_out": {},
        }
    )

    parsed_actions = agent._parse_actions_response(parsed)
    assert len(parsed_actions) == 1
    assert isinstance(parsed_actions[0], RequestUserInputAction)
