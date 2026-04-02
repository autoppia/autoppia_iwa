"""Tests for ApifiedWebAgent (iterative /act endpoint agent)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent


class TestApifiedWebAgentInit:
    def test_init_with_base_url(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000", id="agent-1")
        assert agent.base_url == "http://localhost:5000"
        assert agent.id == "agent-1"
        assert agent.name == "Agent agent-1"

    def test_init_with_base_url_strips_trailing_slash(self):
        agent = ApifiedWebAgent(base_url="http://host:5000/")
        assert agent.base_url == "http://host:5000"

    def test_init_with_host_and_port(self):
        agent = ApifiedWebAgent(host="127.0.0.1", port=5000)
        assert agent.base_url == "http://127.0.0.1:5000"

    def test_init_with_host_only(self):
        agent = ApifiedWebAgent(host="example.com")
        assert agent.base_url == "http://example.com"

    def test_init_without_host_nor_base_url_raises(self):
        with pytest.raises(ValueError, match="host must be provided"):
            ApifiedWebAgent(port=5000)


class TestForceLocalhost:
    def test_force_localhost_preserves_port_and_path(self):
        result = ApifiedWebAgent._force_localhost("https://example.com:8080/path?q=1")
        assert result == "https://localhost:8080/path?q=1"

    def test_force_localhost_none_returns_none(self):
        assert ApifiedWebAgent._force_localhost(None) is None

    def test_force_localhost_no_port(self):
        result = ApifiedWebAgent._force_localhost("http://foo.com/page")
        assert result == "http://localhost/page"


class TestRewriteToRemote:
    def test_rewrite_relative_path_anchors_to_remote(self):
        with patch("autoppia_iwa.src.web_agents.apified_iterative_agent.DEMO_WEBS_ENDPOINT", "https://demo.example.com"):
            result = ApifiedWebAgent._rewrite_to_remote("/path/to/page")
            assert result == "https://demo.example.com/path/to/page"

    def test_rewrite_none_returns_none(self):
        assert ApifiedWebAgent._rewrite_to_remote(None) is None

    def test_rewrite_no_scheme_prepends_remote_scheme_and_netloc(self):
        with patch("autoppia_iwa.src.web_agents.apified_iterative_agent.DEMO_WEBS_ENDPOINT", "https://remote.test"):
            result = ApifiedWebAgent._rewrite_to_remote("page")
            assert result == "https://remote.test/page"

    def test_rewrite_full_url_replaces_netloc(self):
        with patch("autoppia_iwa.src.web_agents.apified_iterative_agent.DEMO_WEBS_ENDPOINT", "https://demo.example.com"):
            result = ApifiedWebAgent._rewrite_to_remote("http://other.com/page")
            assert result == "https://demo.example.com/page"


class TestParseActionsResponse:
    def test_actions_list_format(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        data = {
            "actions": [
                {"type": "ClickAction", "x": 10, "y": 20},
            ]
        }
        with patch.object(agent, "_rewrite_to_remote", side_effect=lambda x: x):
            result = agent._parse_actions_response(data)
        assert len(result) == 1
        assert result[0].type == "ClickAction"

    def test_single_action_format(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        data = {"action": {"type": "NavigateAction", "url": "http://localhost/page"}}
        with patch.object(agent, "_rewrite_to_remote", side_effect=lambda x: x):
            result = agent._parse_actions_response(data)
        assert len(result) == 1
        assert isinstance(result[0], NavigateAction)

    def test_navigate_url_format(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        data = {"navigate_url": "http://localhost/landing"}
        with patch.object(agent, "_rewrite_to_remote", side_effect=lambda x: x):
            result = agent._parse_actions_response(data)
        assert len(result) == 1
        assert result[0].type == "NavigateAction"
        assert result[0].url == "http://localhost/landing"

    def test_empty_or_invalid_returns_empty_list(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        assert agent._parse_actions_response({}) == []
        assert agent._parse_actions_response({"actions": []}) == []
        assert agent._parse_actions_response({"actions": [None, "not-dict"]}) == []


class TestSolveTask:
    @pytest.mark.asyncio
    async def test_solve_task_raises_not_implemented(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        task = Task(url="https://example.com", prompt="Do something", web_project_id="dummy")
        with pytest.raises(NotImplementedError, match="ApifiedWebAgent only supports act"):
            await agent.solve_task(task)


class TestAct:
    @pytest.mark.asyncio
    async def test_act_returns_actions_on_success(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", id="a1")
        task = Task(url="https://example.com", prompt="Click it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.json = AsyncMock(return_value={"actions": [{"type": "ClickAction", "x": 100, "y": 200}]})
        post_mock = MagicMock()
        post_mock.__aenter__ = AsyncMock(return_value=response_mock)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        session_mock = MagicMock()
        session_mock.post = MagicMock(return_value=post_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=session_mock):
            result = await agent.act(
                task=task,
                snapshot_html="<html></html>",
                url="http://localhost:8000/",
                step_index=0,
            )
        assert len(result) == 1
        assert result[0].type == "ClickAction"

    @pytest.mark.asyncio
    async def test_act_returns_dict_when_extracted_data_in_response(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", id="a1")
        task = Task(url="https://example.com", prompt="Read it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.json = AsyncMock(
            return_value={
                "actions": [{"type": "ClickAction", "x": 1, "y": 2}],
                "extracted_data": "subnet-42",
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
            result = await agent.act(
                task=task,
                snapshot_html="<html></html>",
                url="http://localhost:8000/",
                step_index=0,
            )
        assert isinstance(result, dict)
        assert result["extracted_data"] == "subnet-42"
        assert len(result["actions"]) == 1
        assert result["actions"][0].type == "ClickAction"

    @pytest.mark.asyncio
    async def test_act_returns_empty_when_both_endpoints_fail(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", timeout=0.5)
        task = Task(url="https://example.com", prompt="P", web_project_id="dummy")
        session_mock = MagicMock()
        session_mock.post = MagicMock(side_effect=Exception("connection refused"))
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)
        with patch("aiohttp.ClientSession", return_value=session_mock):
            result = await agent.act(
                task=task,
                snapshot_html="",
                url="http://localhost:8000/",
                step_index=0,
            )
        assert result == []
