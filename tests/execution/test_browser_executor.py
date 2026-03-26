"""Tests for execution.browser_executor."""

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.execution import browser_executor
from autoppia_iwa.src.execution.actions.base import BaseAction


def test_parse_event_timestamp_not_dict():
    assert browser_executor._parse_event_timestamp(None) is None
    assert browser_executor._parse_event_timestamp("string") is None
    assert browser_executor._parse_event_timestamp([]) is None


def test_parse_event_timestamp_empty_dict():
    assert browser_executor._parse_event_timestamp({}) is None
    assert browser_executor._parse_event_timestamp({"other": 1}) is None


def test_parse_event_timestamp_top_level():
    dt = browser_executor._parse_event_timestamp({"timestamp": "2024-01-15T10:00:00Z"})
    assert dt is not None
    assert dt.tzinfo is not None


def test_parse_event_timestamp_without_timezone_assumes_utc():
    dt = browser_executor._parse_event_timestamp({"timestamp": "2024-01-15T10:00:00"})
    assert dt is not None
    assert dt.tzinfo is not None


def test_parse_event_timestamp_data_nested():
    dt = browser_executor._parse_event_timestamp({"data": {"timestamp": "2024-01-15T10:00:00Z"}})
    assert dt is not None


def test_parse_event_timestamp_invalid_returns_none():
    assert browser_executor._parse_event_timestamp({"timestamp": ""}) is None
    assert browser_executor._parse_event_timestamp({"timestamp": "not-a-date"}) is None


def test_minimal_snapshot():
    out = browser_executor._minimal_snapshot(html="<p>", url="http://x", error="err")
    assert out["html"] == "<p>"
    assert out["url"] == "http://x"
    assert out["error"] == "err"
    assert out["screenshot"] == ""


def test_action_execution_exception_types_contains_common_errors():
    exc_types = browser_executor._action_execution_exception_types()
    assert RuntimeError in exc_types
    assert ValueError in exc_types
    assert TypeError in exc_types


@pytest.mark.asyncio
async def test_executor_execute_single_action_raises_without_page():
    from autoppia_iwa.src.execution.actions.actions import NavigateAction

    config = BrowserSpecification()
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=None)
    action = NavigateAction(url="http://example.com")
    with pytest.raises(RuntimeError, match="Playwright page is not initialized"):
        await executor.execute_single_action(action, "agent1", 0, False, False)


class _FakePage:
    def __init__(self):
        self.url = "http://example.com"

    async def content(self):
        return "<html></html>"

    async def screenshot(self, **kwargs):
        return b"img"

    async def wait_for_load_state(self, *_args, **_kwargs):
        return None


class _FailingPage(_FakePage):
    async def content(self):
        raise RuntimeError("content failed")


class _ActionOk(BaseAction):
    type: str = "ActionOk"

    async def execute(self, page, backend_service, web_agent_id):
        return None


class _ActionFail(BaseAction):
    type: str = "ActionFail"

    async def execute(self, page, backend_service, web_agent_id):
        raise ValueError("boom")


class _Backend:
    async def get_backend_events(self, web_agent_id):
        return []


@pytest.mark.asyncio
async def test_capture_snapshot_error_returns_minimal():
    executor = browser_executor.PlaywrightBrowserExecutor(BrowserSpecification(), page=_FailingPage(), backend_demo_webs_service=_Backend())
    snap = await executor._capture_snapshot()
    assert snap["screenshot"] == ""
    assert "error" in snap


@pytest.mark.asyncio
async def test_execute_single_action_success_path():
    executor = browser_executor.PlaywrightBrowserExecutor(BrowserSpecification(), page=_FakePage(), backend_demo_webs_service=_Backend())
    result = await executor.execute_single_action(_ActionOk(type="ActionOk"), "agent1", 0, False, should_record=False)
    assert result.successfully_executed is True
    assert result.error is None


@pytest.mark.asyncio
async def test_execute_single_action_error_path():
    executor = browser_executor.PlaywrightBrowserExecutor(BrowserSpecification(), page=_FakePage(), backend_demo_webs_service=_Backend())
    result = await executor.execute_single_action(_ActionFail(type="ActionFail"), "agent1", 0, False, should_record=False)
    assert result.successfully_executed is False
    assert "boom" in (result.error or "")
