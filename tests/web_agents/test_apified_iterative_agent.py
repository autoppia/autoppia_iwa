"""Tests for ApifiedWebAgent (iterative /step endpoint agent)."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.execution.actions.actions import GoBackAction, NavigateAction, RequestUserInputAction, TypeAction
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent
from autoppia_iwa.src.web_agents.protocol import StepResponse


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

    def test_max_actions_per_step_rejects_invalid_values(self):
        with pytest.raises(ValueError, match="max_actions_per_step must be greater than 0"):
            ApifiedWebAgent(base_url="http://127.0.0.1:5060", max_actions_per_step=0)


class TestForceLocalhost:
    def test_force_localhost_preserves_port_and_path(self):
        result = ApifiedWebAgent._force_localhost("https://example.com:8080/path?q=1")
        assert result == "https://localhost:8080/path?q=1"

    def test_force_localhost_none_returns_none(self):
        assert ApifiedWebAgent._force_localhost(None) is None

    def test_force_localhost_no_port(self):
        result = ApifiedWebAgent._force_localhost("http://foo.com/page")
        assert result == "http://localhost/page"


class TestScreenshotForJson:
    def test_none_and_empty(self):
        assert ApifiedWebAgent._screenshot_for_json(None) is None
        assert ApifiedWebAgent._screenshot_for_json(b"") is None
        assert ApifiedWebAgent._screenshot_for_json("   ") is None

    def test_bytes_becomes_data_url(self):
        png_magic = b"\x89PNG\r\n\x1a\n"
        out = ApifiedWebAgent._screenshot_for_json(png_magic)
        assert out.startswith("data:image/png;base64,")

    def test_string_preserved(self):
        s = "data:image/png;base64,QQ=="
        assert ApifiedWebAgent._screenshot_for_json(s) == s


class TestRewriteToRemote:
    @staticmethod
    def _agent() -> ApifiedWebAgent:
        return ApifiedWebAgent(base_url="http://127.0.0.1:1")

    def test_rewrite_relative_path_anchors_to_remote(self):
        agent = self._agent()
        with patch("autoppia_iwa.src.web_agents.apified_web_agent.DEMO_WEBS_ENDPOINT", "https://demo.example.com"):
            result = agent._rewrite_to_remote("/path/to/page")
            assert result == "https://demo.example.com/path/to/page"

    def test_rewrite_none_returns_none(self):
        assert self._agent()._rewrite_to_remote(None) is None

    def test_rewrite_no_scheme_prepends_remote_scheme_and_netloc(self):
        agent = self._agent()
        with patch("autoppia_iwa.src.web_agents.apified_web_agent.DEMO_WEBS_ENDPOINT", "https://remote.test"):
            result = agent._rewrite_to_remote("page")
            assert result == "https://remote.test/page"

    def test_rewrite_full_url_replaces_netloc(self):
        agent = self._agent()
        with patch("autoppia_iwa.src.web_agents.apified_web_agent.DEMO_WEBS_ENDPOINT", "https://demo.example.com"):
            result = agent._rewrite_to_remote("http://other.com/page")
            assert result == "https://demo.example.com/page"

    def test_rewrite_bare_localhost_gets_scheme(self):
        agent = self._agent()
        agent._step_rewrite_page_url = "http://localhost:8013/?seed=1"
        with patch("autoppia_iwa.src.web_agents.apified_web_agent.DEMO_WEBS_ENDPOINT", "http://localhost"):
            result = agent._rewrite_to_remote("localhost")
            assert result == "http://localhost:8013/"

    def test_rewrite_http_localhost_without_port_keeps_demo_page_port(self):
        agent = self._agent()
        agent._step_rewrite_page_url = "http://localhost:8013/?seed=1"
        with patch("autoppia_iwa.src.web_agents.apified_web_agent.DEMO_WEBS_ENDPOINT", "http://localhost"):
            result = agent._rewrite_to_remote("http://localhost/appointments")
            assert result == "http://localhost:8013/appointments"


class TestParseActionsResponse:
    def test_actions_list_format(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        data = {"actions": [{"type": "ClickAction", "x": 10, "y": 20}]}
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

    def test_parse_actions_response_rewrites_navigate_from_browser_tool_call(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [
                    {"name": "browser.navigate", "arguments": {"url": "/dashboard"}},
                    {"name": "browser.click", "arguments": {"x": 10, "y": 20}},
                ],
                "done": False,
            }
        )

        parsed_actions = agent._parse_actions_response(parsed)

        assert len(parsed_actions) == 2
        assert isinstance(parsed_actions[0], NavigateAction)
        assert parsed_actions[0].url == agent._rewrite_to_remote("/dashboard")

    def test_parse_actions_response_returns_empty_when_done_true_and_no_tool_calls(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        parsed = StepResponse.from_raw({"tool_calls": [], "done": True, "reasoning": "finished"})
        parsed_actions = agent._parse_actions_response(parsed)
        assert parsed_actions == []

    def test_parse_actions_response_returns_batch_by_default(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [
                    {"name": "browser.navigate", "arguments": {"url": "/a"}},
                    {"name": "browser.navigate", "arguments": {"url": "/b"}},
                ],
                "done": False,
            }
        )

        parsed_actions = agent._parse_actions_response(parsed)

        assert len(parsed_actions) == 2
        assert isinstance(parsed_actions[0], NavigateAction)
        assert isinstance(parsed_actions[1], NavigateAction)

    def test_parse_actions_response_honors_max_actions_per_step(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060", max_actions_per_step=1)
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [
                    {"name": "browser.navigate", "arguments": {"url": "/a"}},
                    {"name": "browser.navigate", "arguments": {"url": "/b"}},
                ],
                "done": False,
            }
        )

        parsed_actions = agent._parse_actions_response(parsed)

        assert len(parsed_actions) == 1
        assert isinstance(parsed_actions[0], NavigateAction)
        assert parsed_actions[0].url == agent._rewrite_to_remote("/a")

    def test_parse_actions_response_maps_user_request_input_tool(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [{"name": "user.request_input", "arguments": {"prompt": "Need OTP"}}],
                "done": False,
            }
        )

        parsed_actions = agent._parse_actions_response(parsed)
        assert len(parsed_actions) == 1
        assert isinstance(parsed_actions[0], RequestUserInputAction)

    def test_parse_actions_response_supports_new_browser_use_tool_names(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [
                    {"name": "browser.input", "arguments": {"text": "hello"}},
                    {"name": "browser.go_back", "arguments": {}},
                ],
                "done": False,
            }
        )

        parsed_actions = agent._parse_actions_response(parsed)
        assert len(parsed_actions) == 2
        assert isinstance(parsed_actions[0], TypeAction)
        assert isinstance(parsed_actions[1], GoBackAction)

    def test_step_response_ignores_operator_telemetry_fields(self) -> None:
        """Subnet operator may add metrics/usage/model; IWA must still parse tool_calls."""
        parsed = StepResponse.from_raw(
            {
                "tool_calls": [{"name": "browser.click", "arguments": {"x": 1, "y": 2}}],
                "done": False,
                "metrics": {"llm": {"llm_calls": 1}},
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "total_tokens": 0,
                "model": "gpt-4o-mini",
                "estimated_cost_usd": 0.0,
            }
        )
        assert len(parsed.tool_calls) == 1
        assert parsed.tool_calls[0].name == "browser.click"
        assert parsed.done is False

    def test_parse_actions_response_accepts_canonical_actions_alias(self) -> None:
        agent = ApifiedWebAgent(base_url="http://127.0.0.1:5060")
        payload = {
            "actions": [
                {"name": "browser.navigate", "arguments": {"url": "/dashboard"}},
                {"name": "browser.click", "arguments": {"x": 10, "y": 20}},
            ],
            "done": False,
        }

        parsed_actions = agent._parse_actions_response(payload)

        assert len(parsed_actions) == 2
        assert isinstance(parsed_actions[0], NavigateAction)
        assert parsed_actions[0].url == agent._rewrite_to_remote("/dashboard")


class TestSolveTask:
    @pytest.mark.asyncio
    async def test_solve_task_raises_not_implemented(self):
        agent = ApifiedWebAgent(base_url="http://localhost:5000")
        task = Task(url="https://example.com", prompt="Do something", web_project_id="dummy")
        with pytest.raises(NotImplementedError, match="only supports step"):
            await agent.solve_task(task)


class TestStep:
    @pytest.mark.asyncio
    async def test_step_returns_legacy_actions_on_success(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", id="a1")
        task = Task(url="https://example.com", prompt="Click it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.text = AsyncMock(return_value=json.dumps({"actions": [{"type": "ClickAction", "x": 100, "y": 200}]}))
        post_mock = MagicMock()
        post_mock.__aenter__ = AsyncMock(return_value=response_mock)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        session_mock = MagicMock()
        session_mock.post = MagicMock(return_value=post_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=session_mock):
            result = await agent.step(
                task=task,
                html="<html></html>",
                url="http://localhost:8000/",
                step_index=0,
            )
        assert len(result) == 1
        assert result[0].type == "ClickAction"
        assert session_mock.post.call_args.args[0] == "http://localhost:9999/step"

    @pytest.mark.asyncio
    async def test_step_returns_canonical_actions_on_success(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", id="a1")
        task = Task(url="https://example.com", prompt="Click it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.text = AsyncMock(
            return_value=json.dumps(
                {
                    "tool_calls": [{"name": "browser.navigate", "arguments": {"url": "/landing"}}],
                    "done": False,
                    "reasoning": "go to landing",
                }
            )
        )
        post_mock = MagicMock()
        post_mock.__aenter__ = AsyncMock(return_value=response_mock)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        session_mock = MagicMock()
        session_mock.post = MagicMock(return_value=post_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=session_mock):
            result = await agent.step(
                task=task,
                html="<html></html>",
                url="http://localhost:8000/",
                step_index=0,
            )

        assert len(result) == 1
        assert isinstance(result[0], NavigateAction)
        assert result[0].url == agent._rewrite_to_remote("/landing")
        assert agent.last_reasoning == "go to landing"
        assert session_mock.post.call_args.args[0] == "http://localhost:9999/step"

    @pytest.mark.asyncio
    async def test_step_posts_canonical_payload_with_tools_and_html(self):
        agent = ApifiedWebAgent(
            base_url="http://localhost:9999",
            id="a1",
            request_reasoning=True,
            send_allowed_tools=True,
        )
        task = Task(url="https://example.com", prompt="Click it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.text = AsyncMock(return_value=json.dumps({"tool_calls": [], "done": False}))
        post_mock = MagicMock()
        post_mock.__aenter__ = AsyncMock(return_value=response_mock)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        session_mock = MagicMock()
        session_mock.post = MagicMock(return_value=post_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=session_mock):
            await agent.step(
                task=task,
                html="<main>hello</main>",
                screenshot=b"raw-shot",
                url="http://example.com:8000/page",
                step_index=3,
                history=[{"action": "click"}],
            )

        _, kwargs = session_mock.post.call_args
        payload = kwargs["json"]
        assert payload["task_id"] == task.id
        assert payload["prompt"] == task.prompt
        assert payload["url"] == "http://localhost:8000/page"
        assert payload["html"] == "<main>hello</main>"
        assert str(payload["screenshot"]).startswith("data:image/png;base64,")
        assert payload["step_index"] == 3
        assert payload["history"] == [{"action": "click"}]
        assert payload["include_reasoning"] is True
        assert "tools" in payload
        assert isinstance(payload["tools"], list)
        assert all(isinstance(item, dict) for item in payload["tools"])

    @pytest.mark.asyncio
    async def test_step_uses_snapshot_html_alias_when_provided(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", id="a1")
        task = Task(url="https://example.com", prompt="Click it", web_project_id="dummy")
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.raise_for_status = MagicMock()
        response_mock.text = AsyncMock(return_value=json.dumps({"tool_calls": [], "done": False}))
        post_mock = MagicMock()
        post_mock.__aenter__ = AsyncMock(return_value=response_mock)
        post_mock.__aexit__ = AsyncMock(return_value=None)
        session_mock = MagicMock()
        session_mock.post = MagicMock(return_value=post_mock)
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=session_mock):
            await agent.step(
                task=task,
                html="<html>ignored</html>",
                snapshot_html="<html>legacy</html>",
                url="http://example.com",
                step_index=0,
            )

        _, kwargs = session_mock.post.call_args
        assert kwargs["json"]["html"] == "<html>legacy</html>"
        assert agent.last_done is False
        assert agent.tools == []

    @pytest.mark.asyncio
    async def test_step_returns_empty_when_step_fails(self):
        agent = ApifiedWebAgent(base_url="http://localhost:9999", timeout=0.5)
        task = Task(url="https://example.com", prompt="P", web_project_id="dummy")
        session_mock = MagicMock()
        session_mock.post = MagicMock(side_effect=Exception("connection refused"))
        session_mock.__aenter__ = AsyncMock(return_value=session_mock)
        session_mock.__aexit__ = AsyncMock(return_value=None)
        with patch("aiohttp.ClientSession", return_value=session_mock):
            result = await agent.step(
                task=task,
                html="",
                url="http://localhost:8000/",
                step_index=0,
            )
        assert result == []
