import asyncio
from unittest.mock import patch

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


def test_init_raises_when_host_and_base_url_missing():
    with pytest.raises(ValueError, match="host must be provided"):
        ApifiedOneShotWebAgent(host=None, base_url=None)


def test_init_with_port_includes_port_in_base_url():
    agent = ApifiedOneShotWebAgent(host="localhost", port=9000)
    assert agent.base_url == "http://localhost:9000"


def test_init_without_port_omits_port():
    agent = ApifiedOneShotWebAgent(host="localhost", port=None)
    assert agent.base_url == "http://localhost"


def test_force_localhost_returns_none_for_none():
    assert ApifiedOneShotWebAgent._force_localhost(None) is None


def test_force_localhost_rewrites_host_keeps_port():
    result = ApifiedOneShotWebAgent._force_localhost("https://example.com:8000/page")
    assert "localhost" in result
    assert "8000" in result
    assert "/page" in result


def test_rewrite_to_remote_returns_none_for_none():
    assert ApifiedOneShotWebAgent._rewrite_to_remote(None) is None


def test_rewrite_to_remote_relative_path():
    with patch("autoppia_iwa.src.web_agents.apified_one_shot_agent.DEMO_WEBS_ENDPOINT", "http://remote:8090"):
        result = ApifiedOneShotWebAgent._rewrite_to_remote("/path")
        assert result == "http://remote:8090/path" or ("remote" in result and "/path" in result)


def test_create_action_returns_none_for_invalid_raw():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    assert agent._create_action({"type": "UnknownType"}) is None
    assert agent._create_action("not a dict") is None


@pytest.mark.asyncio
async def test_act_step_index_non_zero_returns_empty():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    task = Task(url="https://example.com", prompt="p", web_project_id="dummy")
    actions = await agent.act(
        task=task,
        snapshot_html="<html/>",
        url="https://example.com",
        step_index=1,
    )
    assert actions == []
