from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.evaluation.stateful_evaluator import (
    BrowserSnapshot,
    TaskExecutionSession,
    _is_navigation_url_allowed,
    _url_hostname,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult


def test_url_hostname_handles_missing_and_normalizes_case():
    assert _url_hostname(None) is None
    assert _url_hostname("https://EXAMPLE.com/path") == "example.com"


def test_navigation_url_allowed_blocks_non_http_scheme():
    allowed, reason = _is_navigation_url_allowed(
        is_web_real=False,
        task_url="http://localhost:8000",
        candidate_url="javascript:alert(1)",
    )
    assert allowed is False
    assert "scheme" in reason


def test_navigation_url_allowed_allows_relative_and_matching_demo_host():
    assert _is_navigation_url_allowed(
        is_web_real=False,
        task_url="http://localhost:8000",
        candidate_url="/search",
    ) == (True, None)
    assert _is_navigation_url_allowed(
        is_web_real=False,
        task_url="http://demo.local:8000",
        candidate_url="http://demo.local/films",
    ) == (True, None)


def test_navigation_url_allowed_blocks_foreign_real_host():
    allowed, reason = _is_navigation_url_allowed(
        is_web_real=True,
        task_url="https://autoppia.com/start",
        candidate_url="https://evil.com/other",
    )
    assert allowed is False
    assert "does not match" in reason


@pytest.mark.asyncio
async def test_snapshot_async_handles_missing_page_and_screenshot_failure():
    session = TaskExecutionSession(task=Task(url="http://localhost", prompt="p", web_project_id="autocinema"))
    empty = await session._snapshot_async()
    assert empty == BrowserSnapshot(html="", url="", screenshot=None)

    session._page = SimpleNamespace(
        content=AsyncMock(return_value="<html/>"),
        url="http://localhost/page",
        screenshot=AsyncMock(side_effect=RuntimeError("boom")),
    )
    session.capture_screenshot = True

    snap = await session._snapshot_async()
    assert snap.html == "<html/>"
    assert snap.url == "http://localhost/page"
    assert snap.screenshot is None


@pytest.mark.asyncio
async def test_close_async_resets_runtime_handles():
    session = TaskExecutionSession(task=Task(url="http://localhost", prompt="p", web_project_id="autocinema"))
    context = SimpleNamespace(close=AsyncMock())
    browser = SimpleNamespace(close=AsyncMock())
    playwright = SimpleNamespace(stop=AsyncMock())
    backend = SimpleNamespace(close=AsyncMock())
    session._context = context
    session._browser = browser
    session._playwright = playwright
    session._backend = backend

    await session._close_async()

    context.close.assert_awaited_once()
    browser.close.assert_awaited_once()
    playwright.stop.assert_awaited_once()
    backend.close.assert_awaited_once()
    assert session._context is None
    assert session._browser is None
    assert session._playwright is None
    assert session._backend is None


@pytest.mark.asyncio
async def test_step_async_blocks_seed_mismatch_before_executor():
    task = Task(url="http://localhost:8000/?seed=5", prompt="p", web_project_id="autocinema")
    session = TaskExecutionSession(task=task)
    session._page = SimpleNamespace(url="http://localhost:8000")
    session._executor = SimpleNamespace(execute_single_action=AsyncMock())
    session._scorer = SimpleNamespace(score=AsyncMock(return_value=SimpleNamespace(raw_score=0.0, success=False, tests_passed=0, total_tests=1)))
    session._snapshot_async = AsyncMock(return_value=BrowserSnapshot(html="", url="", screenshot=None))

    result = await session._step_async(NavigateAction(url="http://localhost:8000/?seed=7"))

    assert isinstance(result.action_result, ActionExecutionResult)
    assert result.action_result.successfully_executed is False
    assert "Seed mismatch" in (result.action_result.error or "")
    session._executor.execute_single_action.assert_not_awaited()
