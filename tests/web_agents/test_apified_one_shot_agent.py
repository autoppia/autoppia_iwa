import asyncio

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent


def test_apified_web_agent_uses_stub_endpoint(stub_agent):
    stub_agent.actions = [
        {
            "type": "ClickAction",
            "selector": {
                "type": "attributeValueSelector",
                "attribute": "id",
                "value": "cta",
            },
        }
    ]

    agent = ApifiedOneShotWebAgent(base_url=stub_agent.base_url, id="agent-1", name="StubAgent")
    task = Task(url="https://example.com", prompt="Click CTA", web_project_id="dummy")

    async def run():
        solution = await agent.solve_task(task)
        assert solution.web_agent_id == "stub-agent"
        assert solution.actions, "Action list should be rebuilt"
        assert solution.actions[0].type == "ClickAction"

    asyncio.run(run())


def test_apified_one_shot_agent_raises_when_endpoint_unavailable():
    agent = ApifiedOneShotWebAgent(base_url="http://127.0.0.1:65500", id="agent-err", name="ErrAgent", timeout=1)
    task = Task(url="https://example.com", prompt="Click CTA", web_project_id="dummy")

    async def run():
        with pytest.raises(RuntimeError):
            await agent.solve_task(task)

    asyncio.run(run())
