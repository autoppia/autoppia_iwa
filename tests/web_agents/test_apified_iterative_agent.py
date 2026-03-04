from autoppia_iwa.src.execution.actions.actions import DoneAction, NavigateAction
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent


def test_parse_actions_response_rewrites_navigate_and_honors_single_step() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")

    parsed_actions = agent._parse_actions_response(
        {
            "execution_mode": "single_step",
            "actions": [
                {"type": "NavigateAction", "url": "/dashboard"},
                {"type": "DoneAction", "reason": "unused"},
            ],
        }
    )

    assert len(parsed_actions) == 1
    assert isinstance(parsed_actions[0], NavigateAction)
    assert parsed_actions[0].url == agent._rewrite_to_remote("/dashboard")


def test_parse_actions_response_emits_done_action_when_done_true() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")

    parsed_actions = agent._parse_actions_response({"done": True, "reasoning": "finished"})

    assert len(parsed_actions) == 1
    assert isinstance(parsed_actions[0], DoneAction)
    assert parsed_actions[0].reason == "finished"


def test_parse_actions_response_returns_batch_by_default() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")

    parsed_actions = agent._parse_actions_response(
        {
            "execution_mode": "batch",
            "actions": [
                {"type": "NavigateAction", "url": "/a"},
                {"type": "NavigateAction", "url": "/b"},
            ],
        }
    )

    assert len(parsed_actions) == 2
    assert isinstance(parsed_actions[0], NavigateAction)
    assert isinstance(parsed_actions[1], NavigateAction)


def test_parse_actions_response_honors_max_actions_per_step() -> None:
    agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060", max_actions_per_step=1)

    parsed_actions = agent._parse_actions_response(
        {
            "execution_mode": "batch",
            "actions": [
                {"type": "NavigateAction", "url": "/a"},
                {"type": "NavigateAction", "url": "/b"},
            ],
        }
    )

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
