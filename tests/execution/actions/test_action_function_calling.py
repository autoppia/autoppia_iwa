import asyncio

from autoppia_iwa.src.execution.actions.actions import RequestUserInputAction, TypeAction
from autoppia_iwa.src.execution.actions.base import BaseAction


def test_create_action_from_function_call_payload() -> None:
    created = BaseAction.create_action(
        {
            "function": {
                "name": "type",
                "arguments": '{"selector": {"type": "attributeValueSelector", "attribute": "id", "value": "email"}, "text": "hello"}',
            }
        }
    )

    assert isinstance(created, TypeAction)
    assert created.text == "hello"


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
