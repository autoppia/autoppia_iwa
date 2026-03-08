import asyncio

from autoppia_iwa.src.execution.actions.actions import (
    ExtractAction,
    GetDropDownOptionsAction,
    GoBackAction,
    RequestUserInputAction,
    SearchAction,
    SelectDropDownOptionAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction


def test_create_action_from_function_call_payload() -> None:
    created = BaseAction.create_action(
        {
            "function": {
                "name": "input",
                "arguments": '{"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "email"}, "text": "hello"}',
            }
        }
    )

    assert isinstance(created, TypeAction)
    assert created.text == "hello"


def test_create_action_accepts_browser_use_tool_names() -> None:
    assert isinstance(BaseAction.create_action({"type": "input", "text": "x"}), TypeAction)
    assert isinstance(BaseAction.create_action({"type": "go_back"}), GoBackAction)
    assert isinstance(
        BaseAction.create_action(
            {
                "type": "select_dropdown",
                "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "genre"},
                "text": "Comedy",
            }
        ),
        SelectDropDownOptionAction,
    )
    assert isinstance(
        BaseAction.create_action(
            {
                "type": "dropdown_options",
                "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "genre"},
            }
        ),
        GetDropDownOptionsAction,
    )


def test_browser_use_tool_names_are_exposed_in_function_definitions() -> None:
    defs = BaseAction.all_function_definitions()
    names = {item["function"]["name"] for item in defs if isinstance(item, dict) and isinstance(item.get("function"), dict)}

    assert "input" in names
    assert "go_back" in names
    assert "select_dropdown" in names
    assert "dropdown_options" in names
    assert "search" in names
    assert "extract" in names


def test_request_user_input_action_metadata_and_execution() -> None:
    action = BaseAction.create_action(
        {
            "type": "RequestUserInputAction",
            "prompt": "Choose 2FA method",
            "options": ["sms", "email"],
        }
    )

    assert isinstance(action, RequestUserInputAction)
    function_def = RequestUserInputAction.to_function_definition()
    assert function_def["type"] == "function"
    assert function_def["function"]["name"] == "request_user_input"

    call_payload = action.to_tool_call()
    assert call_payload["name"] == "request_user_input"
    assert call_payload["arguments"]["prompt"] == "Choose 2FA method"

    async def run() -> None:
        result = await action.execute(page=None, backend_service=None, web_agent_id="agent-1")
        assert result is None

    asyncio.run(run())


def test_new_actions_use_browser_use_names() -> None:
    assert SearchAction.tool_name() == "search"
    assert ExtractAction.tool_name() == "extract"


def test_search_action_builds_search_url() -> None:
    class FakePage:
        def __init__(self) -> None:
            self.visited: list[str] = []

        async def goto(self, url: str) -> None:
            self.visited.append(url)

    async def run() -> None:
        page = FakePage()
        await SearchAction(query="browser use", engine="duckduckgo").execute(page, backend_service=None, web_agent_id="agent-1")
        assert page.visited == ["https://duckduckgo.com/?q=browser+use"]

    asyncio.run(run())
