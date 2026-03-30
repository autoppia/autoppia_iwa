from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent


@pytest.mark.asyncio
async def test_apified_web_agent_solves_task_and_rebuilds_actions():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:9999", id="agent-1", name="StubAgent")
    task = Task(url="https://example.com", prompt="Click CTA", web_project_id="dummy")

    response_mock = AsyncMock()
    response_mock.raise_for_status = MagicMock()
    response_mock.json = AsyncMock(
        return_value={
            "web_agent_id": "stub-agent",
            "actions": [
                {
                    "type": "ClickAction",
                    "selector": {
                        "type": "attributeValueSelector",
                        "attribute": "id",
                        "value": "cta",
                    },
                }
            ],
        }
    )
    post_mock = MagicMock()
    post_mock.__aenter__ = AsyncMock(return_value=response_mock)
    post_mock.__aexit__ = AsyncMock(return_value=None)
    session_mock = MagicMock()
    session_mock.post = MagicMock(return_value=post_mock)
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=session_mock):
        solution = await agent.solve_task(task)

    assert solution.web_agent_id == "stub-agent"
    assert len(solution.actions) == 1
    assert solution.actions[0].type == "ClickAction"
    session_mock.post.assert_called_once()
    _, kwargs = session_mock.post.call_args
    assert kwargs["json"]["url"] == "https://localhost"


@pytest.mark.asyncio
async def test_apified_one_shot_agent_raises_when_endpoint_unavailable():
    agent = ApifiedOneShotWebAgent(base_url="http://127.0.0.1:65500", id="agent-err", name="ErrAgent", timeout=1)
    task = Task(url="https://example.com", prompt="Click CTA", web_project_id="dummy")
    with pytest.raises(RuntimeError):
        await agent.solve_task(task)


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
        html="<html/>",
        url="https://example.com",
        step_index=1,
    )
    assert actions == []


@pytest.mark.asyncio
async def test_act_step_index_zero_uses_cached_solution_after_first_call():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    task = Task(url="https://example.com", prompt="p", web_project_id="dummy")

    fake_action = {"type": "NavigateAction", "url": "http://localhost/page"}
    response_mock = AsyncMock()
    response_mock.raise_for_status = MagicMock()
    response_mock.json = AsyncMock(return_value={"web_agent_id": "agent-x", "actions": [fake_action]})
    post_mock = MagicMock()
    post_mock.__aenter__ = AsyncMock(return_value=response_mock)
    post_mock.__aexit__ = AsyncMock(return_value=None)
    session_mock = MagicMock()
    session_mock.post = MagicMock(return_value=post_mock)
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=session_mock):
        first_actions = await agent.act(task=task, html="<html/>", url="https://example.com", step_index=0)
        second_actions = await agent.act(task=task, html="<html/>", url="https://example.com", step_index=1)

    assert len(first_actions) == 1
    assert first_actions[0].type == "NavigateAction"
    assert second_actions == []
    assert agent._cached_solution is not None
