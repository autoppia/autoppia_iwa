import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import BaseAction, NavigateAction
from autoppia_iwa.src.web_agents.apified_one_shot_agent import ApifiedOneShotWebAgent
from autoppia_iwa.src.web_agents.classes import TaskSolution


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


@pytest.mark.asyncio
async def test_act_step_zero_caches_solution_and_returns_actions():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    task = Task(url="https://example.com", prompt="p", web_project_id="dummy")
    nav = NavigateAction(type="NavigateAction", url="/home")
    solution = TaskSolution(task_id=str(task.id), actions=[nav], web_agent_id="ag")
    with patch.object(agent, "solve_task", new_callable=AsyncMock, return_value=solution):
        out = await agent.act(
            task=task,
            snapshot_html="<html/>",
            url="https://example.com",
            step_index=0,
        )
    assert out == solution.actions
    assert agent._cached_solution is solution


def test_create_action_swallows_create_exception():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    with patch.object(BaseAction, "create_action", side_effect=RuntimeError("fail")):
        assert agent._create_action({"type": "NavigateAction", "url": "/x"}) is None


@pytest.mark.asyncio
async def test_solve_task_skips_non_dict_actions_and_none_factory_results():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:9999", id="a1")
    task = Task(url="https://example.com", prompt="p", web_project_id="dummy")
    response_mock = AsyncMock()
    response_mock.raise_for_status = MagicMock()
    response_mock.json = AsyncMock(
        return_value={
            "actions": [None, "skip", {"type": "__unregistered__"}, {"type": "NavigateAction", "url": "/ok"}],
            "web_agent_id": "remote-agent",
            "recording": "rec",
        }
    )
    post_mock = MagicMock()
    post_mock.__aenter__ = AsyncMock(return_value=response_mock)
    post_mock.__aexit__ = AsyncMock(return_value=None)
    session_mock = MagicMock()
    session_mock.post = MagicMock(return_value=post_mock)
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=session_mock), patch.object(agent, "_rewrite_to_remote", side_effect=lambda u: u):
        sol = await agent.solve_task(task)

    assert sol.web_agent_id == "remote-agent"
    assert sol.recording == "rec"
    assert len(sol.actions) == 1
    assert isinstance(sol.actions[0], NavigateAction)


def test_solve_task_sync_wraps_async():
    agent = ApifiedOneShotWebAgent(base_url="http://localhost:5000")
    task = Task(url="https://example.com", prompt="p", web_project_id="dummy")
    expected = TaskSolution(task_id=str(task.id), actions=[], web_agent_id="x")
    with patch.object(agent, "solve_task", new_callable=AsyncMock, return_value=expected):
        assert agent.solve_task_sync(task) is expected


def test_rewrite_to_remote_path_without_scheme_or_netloc_is_anchored():
    # urlparse leaves netloc empty for "8001/foo" (path-only shape), exercising the
    # branch that anchors the string to the remote demo host.
    with patch("autoppia_iwa.src.web_agents.apified_one_shot_agent.DEMO_WEBS_ENDPOINT", "https://demo.example.com"):
        result = ApifiedOneShotWebAgent._rewrite_to_remote("8001/foo")
        assert result == "https://demo.example.com/8001/foo"


def test_rewrite_to_remote_loopback_preserves_agent_port():
    with patch("autoppia_iwa.src.web_agents.apified_one_shot_agent.DEMO_WEBS_ENDPOINT", "https://remote.app"):
        result = ApifiedOneShotWebAgent._rewrite_to_remote("http://127.0.0.1:7777/page")
        assert result.startswith("https://remote.app:7777") or ":7777" in result


def test_rewrite_to_remote_non_loopback_uses_remote_netloc():
    with patch("autoppia_iwa.src.web_agents.apified_one_shot_agent.DEMO_WEBS_ENDPOINT", "https://remote.app"):
        result = ApifiedOneShotWebAgent._rewrite_to_remote("https://other.example.com:9999/z")
        assert "remote.app" in result
        assert "9999" not in result or "other" not in result.split("://", 1)[1].split("/")[0]


def test_rewrite_to_remote_ip_remote_carries_port_when_no_remote_port():
    with patch("autoppia_iwa.src.web_agents.apified_one_shot_agent.DEMO_WEBS_ENDPOINT", "http://10.0.0.1"):
        result = ApifiedOneShotWebAgent._rewrite_to_remote("http://example.com:8888/path")
        assert "10.0.0.1:8888" in result
