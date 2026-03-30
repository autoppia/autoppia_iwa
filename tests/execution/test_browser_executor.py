"""Tests for the Playwright browser executor."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification
from autoppia_iwa.src.execution import playwright_browser_executor as browser_executor


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


@pytest.mark.asyncio
async def test_executor_returns_failed_result_for_assertion_error():
    from autoppia_iwa.src.execution.actions.actions import AssertAction

    page = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>missing</body></html>")
    page.url = "http://example.com"
    config = BrowserSpecification()
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=page)

    result = await executor.execute_single_action(
        AssertAction(text_to_assert="expected"),
        "agent1",
        0,
        is_web_real=True,
        should_record=False,
    )

    assert result.successfully_executed is False
    assert "expected" in (result.error or "")


@pytest.mark.asyncio
async def test_executor_before_action_failure_does_not_crash_on_unbound_start_time():
    from autoppia_iwa.src.execution.actions.actions import NavigateAction

    class FailingExecutor(browser_executor.PlaywrightBrowserExecutor):
        async def _before_action(self, action, iteration):
            raise ValueError("before hook failed")

    page = AsyncMock()
    page.content = AsyncMock(return_value="<html></html>")
    page.url = "http://example.com"
    config = BrowserSpecification()
    executor = FailingExecutor(config, page=page)

    result = await executor.execute_single_action(
        NavigateAction(url="http://example.com"),
        "agent1",
        0,
        is_web_real=True,
        should_record=False,
    )

    assert result.successfully_executed is False
    assert result.error == "before hook failed"


@pytest.mark.asyncio
async def test_fetch_backend_events_filtered_discards_stale_events():
    config = BrowserSpecification()
    backend = Mock()
    page = AsyncMock()
    page.content = AsyncMock(return_value="<html></html>")
    page.url = "http://example.com"
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=page, backend_demo_webs_service=backend)

    start = datetime.now(UTC)
    backend.get_backend_events = AsyncMock(
        return_value=[
            {"event_name": "OLD", "timestamp": (start - timedelta(seconds=5)).isoformat()},
            {"event_name": "NEW", "timestamp": (start + timedelta(seconds=1)).isoformat()},
            {"event_name": "NO_TS"},
        ]
    )

    filtered = await executor._fetch_backend_events_filtered("agent1", start)

    assert [event["event_name"] for event in filtered] == ["NEW", "NO_TS"]


@pytest.mark.asyncio
async def test_get_backend_events_for_action_returns_empty_for_real_web():
    config = BrowserSpecification()
    backend = Mock()
    page = AsyncMock()
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=page, backend_demo_webs_service=backend)

    result = await executor._get_backend_events_for_action("agent1", datetime.now(UTC), is_web_real=True)

    assert result == []
    backend.get_backend_events.assert_not_called()


@pytest.mark.asyncio
async def test_executor_does_not_wait_for_load_state_after_type_action():
    from autoppia_iwa.src.execution.actions.actions import Selector, SelectorType, TypeAction

    page = AsyncMock()
    page.content = AsyncMock(return_value="<html></html>")
    page.url = "http://example.com/login"
    page.fill = AsyncMock(return_value=None)
    page.wait_for_load_state = AsyncMock(return_value=None)
    config = BrowserSpecification()
    executor = browser_executor.PlaywrightBrowserExecutor(config, page=page)

    result = await executor.execute_single_action(
        TypeAction(
            selector=Selector(
                type=SelectorType.ATTRIBUTE_VALUE_SELECTOR,
                attribute="id",
                value="login-username",
            ),
            text="user1",
        ),
        "agent1",
        0,
        is_web_real=True,
        should_record=False,
    )

    assert result.successfully_executed is True
    page.fill.assert_awaited_once()
    page.wait_for_load_state.assert_not_awaited()
