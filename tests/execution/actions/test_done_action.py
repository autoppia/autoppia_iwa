import asyncio

from autoppia_iwa.src.execution.actions.actions import DoneAction
from autoppia_iwa.src.execution.actions.base import BaseAction


def test_done_action_noop_and_factory_creation() -> None:
    action = DoneAction(reason="task complete")

    async def run() -> None:
        result = await action.execute(page=None, backend_service=None, web_agent_id="agent-1")
        assert result is None

    asyncio.run(run())

    created = BaseAction.create_action({"type": "DoneAction", "reason": "done"})
    assert created is not None
    assert created.type == "DoneAction"
    assert getattr(created, "reason", None) == "done"
