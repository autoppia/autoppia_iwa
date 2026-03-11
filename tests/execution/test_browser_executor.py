"""Tests for execution.browser_executor."""

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.execution import browser_executor


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


@pytest.mark.asyncio
async def test_executor_execute_single_action_raises_without_page():
    from autoppia_iwa.src.execution.actions.actions import NavigateAction

    config = BrowserSpecification()
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=None)
    action = NavigateAction(url="http://example.com")
    with pytest.raises(RuntimeError, match="Playwright page is not initialized"):
        await executor.execute_single_action(action, "agent1", 0, False, False)
