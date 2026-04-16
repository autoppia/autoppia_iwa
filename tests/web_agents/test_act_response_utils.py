from typing import Literal

from autoppia_iwa.src.execution.actions.actions import NavigateAction, RequestUserInputAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.act_response_utils import actions_to_act_response


class BlankToolNameAction(BaseAction):
    type: Literal["BlankToolNameAction"] = "BlankToolNameAction"

    @classmethod
    def tool_name(cls) -> str:
        return ""

    async def execute(self, page, backend_service, web_agent_id: str):
        return None


def test_actions_to_act_response_namespaces_browser_and_user_tools() -> None:
    response = actions_to_act_response(
        [
            NavigateAction(url="https://example.com"),
            RequestUserInputAction(prompt="Need confirmation", options=["yes", "no"]),
        ],
        done=True,
        content="ok",
        reasoning="picked two actions",
        state_out={"phase": "done"},
        error=None,
    )

    assert response.done is True
    assert response.content == "ok"
    assert response.reasoning == "picked two actions"
    assert [tool.name for tool in response.tool_calls] == [
        "browser.navigate",
        "user.request_input",
    ]
    assert response.tool_calls[0].arguments["url"] == "https://example.com"
    assert response.tool_calls[1].arguments["prompt"] == "Need confirmation"
    assert "state_out" not in response.model_dump(mode="json")


def test_actions_to_act_response_skips_non_actions_and_blank_tool_names() -> None:
    response = actions_to_act_response(
        [
            NavigateAction(url="https://example.com"),
            "not-an-action",
            BlankToolNameAction(),
        ]
    )

    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "browser.navigate"


def test_actions_to_act_response_defaults_state_out_to_empty_dict() -> None:
    response = actions_to_act_response([], error="boom")

    assert response.tool_calls == []
    assert response.error == "boom"
    assert "state_out" not in response.model_dump(mode="json")
