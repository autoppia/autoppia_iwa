"""
Tests for AsyncStatefulEvaluator using the same pattern as tests/execution/actions:
real Playwright browser, mock HTML via data URL, mock backend for scoring.
Screenshot is disabled (capture_screenshot=False).

Separate tests use real demo server (localhost frontend, real backend) and FILM_DETAIL
task; skip when server is unavailable.
"""

import base64
import textwrap
import urllib.error
import urllib.request
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright.async_api import Error as PlaywrightError

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.scoring import ScoreDetails
from autoppia_iwa.src.evaluation.stateful_evaluator import (
    AsyncStatefulEvaluator,
    _is_navigation_url_allowed as _orig_nav_allowed,
)
from autoppia_iwa.src.execution.actions.actions import ClickAction, TypeAction, WaitAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot as ExecutionBrowserSnapshot

WEB_AGENT_ID = "test_agent"
PROJECT = next(p for p in demo_web_projects if getattr(p, "id", None) == "autobooks")
PROJECT_AUTOCINEMA = next(p for p in demo_web_projects if getattr(p, "id", None) == "autocinema")


def _allow_data_url(*, is_web_real: bool, task_url: str | None, candidate_url: str | None):
    """Allow data: URLs in tests so we can use mock HTML without a real server."""
    if candidate_url and candidate_url.strip().lower().startswith("data:"):
        return True, None
    return _orig_nav_allowed(is_web_real=is_web_real, task_url=task_url, candidate_url=candidate_url)


def _make_mock_html():
    return textwrap.dedent(
        """
        <!doctype html>
        <html>
        <body>
          <h1>Mock page</h1>
          <input id="input" type="text" />
        </body>
        </html>
        """
    ).strip()


def _data_url(html: str) -> str:
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return f"data:text/html;base64,{encoded}"


def _make_task(url: str):
    return Task(
        id="task-stateful-1",
        url=url,
        prompt="Log in to the app",
        web_project_id=PROJECT.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="LOGIN_BOOK",
                event_criteria={"username": "user123"},
                description="User must log in",
            )
        ],
    )


def _make_action_result(action, *, url: str, html: str, success: bool = True) -> ActionExecutionResult:
    return ActionExecutionResult(
        action=action,
        action_event=action.type,
        successfully_executed=success,
        error=None if success else "failed",
        execution_time=0.1,
        browser_snapshot=ExecutionBrowserSnapshot(
            iteration=0,
            action=action,
            prev_html="",
            current_html=html,
            screenshot_before="",
            screenshot_after="",
            backend_events=[],
            current_url=url,
        ),
    )


class _DummyPage:
    def __init__(self, *, html: str, url: str):
        self._html = html
        self.url = url

    async def content(self):
        return self._html

    async def screenshot(self, full_page=True):
        return b"fake-screenshot"


class _DummyContext:
    def __init__(self, page):
        self._page = page
        self.headers = None

    async def new_page(self):
        return self._page

    async def add_init_script(self, script):
        return None

    def set_default_timeout(self, value):
        return None

    async def close(self):
        return None


class _DummyBrowser:
    def __init__(self, context):
        self._context = context

    async def new_context(self, **kwargs):
        self._context.headers = kwargs.get("extra_http_headers")
        return self._context

    async def close(self):
        return None


class _DummyPlaywright:
    def __init__(self, browser):
        self.chromium = SimpleNamespace(launch=AsyncMock(return_value=browser))

    async def stop(self):
        return None


def _build_runtime_patches(*, html: str, url: str, action_result: ActionExecutionResult, scores: list[ScoreDetails]):
    page = _DummyPage(html=html, url=url)
    context = _DummyContext(page)
    browser = _DummyBrowser(context)
    playwright = _DummyPlaywright(browser)
    async_playwright_factory = MagicMock(return_value=SimpleNamespace(start=AsyncMock(return_value=playwright)))
    executor_mock = MagicMock()
    executor_mock.execute_single_action = AsyncMock(return_value=action_result)
    score_mock = AsyncMock(side_effect=scores)
    return (
        patch("autoppia_iwa.src.evaluation.stateful_evaluator.async_playwright", async_playwright_factory),
        patch("autoppia_iwa.src.evaluation.stateful_evaluator.PlaywrightBrowserExecutor", return_value=executor_mock),
        patch("autoppia_iwa.src.evaluation.stateful_evaluator.TaskExecutionScorer.score", new=score_mock),
        executor_mock,
        context,
    )


# -----------------------------------------------------------------------------
# Real server (integration): autocinema, FILM_DETAIL, localhost frontend/backend
# -----------------------------------------------------------------------------


def _skip_if_real_server_unavailable(reason: str):
    """Skip when demo webs backend is not reachable."""
    pytest.skip(reason)


def _is_real_demo_server_available() -> tuple[bool, str]:
    """Check if the demo webs backend is reachable. Returns (True, "") or (False, reason)."""
    base = DEMO_WEBS_ENDPOINT.rstrip("/")
    if "://" in base:
        rest = base.split("://", 1)[1]
        host = rest.split("/")[0].split(":")[0]
    else:
        host = base.split("/")[0].split(":")[0]
    port = DEMO_WEB_SERVICE_PORT
    url = f"http://{host}:{port}/health"
    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("User-Agent", "IWA-Test/1.0")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status in (200, 204):
                return True, ""
            return False, f"Backend returned status {resp.status}"
    except urllib.error.URLError as e:
        return False, f"Demo webs backend not reachable: {e.reason}"
    except OSError as e:
        return False, f"Demo webs backend not reachable: {e}"


def _make_real_server_task():
    """Task for real-server test: FILM_DETAIL on autocinema, criteria Inception."""
    base_url = (PROJECT_AUTOCINEMA.frontend_url or "").rstrip("/") or f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"
    return Task(
        id="task-stateful-real-film-detail",
        url=base_url,
        prompt="Open a film detail that name equals 'Inception'",
        web_project_id=PROJECT_AUTOCINEMA.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="FILM_DETAIL",
                event_criteria={"name": "Inception"},
                description="User must view a film detail page",
            )
        ],
    )


def _make_real_server_task_failing_criteria():
    """Task with FILM_DETAIL criteria that do not match current actions (Inception -> The Matrix)."""
    base_url = (PROJECT_AUTOCINEMA.frontend_url or "").rstrip("/") or f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"
    return Task(
        id="task-stateful-real-film-detail-fail",
        url=base_url,
        prompt="Open a film detail that name equals 'The Matrix'",
        web_project_id=PROJECT_AUTOCINEMA.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="FILM_DETAIL",
                event_criteria={"name": "The Matrix"},
                description="User must view The Matrix film detail page",
            )
        ],
    )


def _real_server_step1_actions():
    """Step 1: two actions — search for Inception and submit search."""
    return [
        TypeAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input"),
            text="Inception",
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="search-submit-button"),
        ),
    ]


def _real_server_step2_actions():
    """Step 2: one action — open film detail."""
    return [
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="view-details-button"),
        ),
        WaitAction(time_seconds=1),
    ]


@pytest.mark.asyncio
async def test_stateful_evaluator_correct_solution():
    """Reset and step should work with a mocked runtime and real session logic."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID)])
    step_action = TypeAction(
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input"),
        text="hello",
    )
    action_result = _make_action_result(step_action, url=data_url, html=html)
    async_playwright_patch, executor_patch, scorer_patch, executor_mock, context = _build_runtime_patches(
        html=html,
        url=data_url,
        action_result=action_result,
        scores=[
            ScoreDetails(raw_score=0.0, tests_passed=0, total_tests=1, success=False),
            ScoreDetails(raw_score=1.0, tests_passed=1, total_tests=1, success=True),
            ScoreDetails(raw_score=1.0, tests_passed=1, total_tests=1, success=True),
        ],
    )

    with (
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        async_playwright_patch,
        executor_patch,
        scorer_patch,
    ):
        evaluator = AsyncStatefulEvaluator(
            task=task,
            web_agent_id=WEB_AGENT_ID,
            should_record_gif=False,
            capture_screenshot=False,
        )
        try:
            step_result = await evaluator.reset()
            assert step_result.score.total_tests >= 1
            step_result = await evaluator.step(step_action)
            details = await evaluator.get_score_details()
            assert details.total_tests >= 1
            assert details.tests_passed >= 1
            assert details.raw_score > 0
            assert details.success is True
            assert step_result.action_result is action_result
            assert step_result.snapshot.html == html
            assert executor_mock.execute_single_action.await_count == 2
            assert context.headers == {"X-WebAgent-Id": WEB_AGENT_ID, "X-Validator-Id": evaluator.validator_id}
        finally:
            await evaluator.close()


@pytest.mark.asyncio
async def test_stateful_evaluator_wrong_solution():
    """A noop step should still rescore and preserve existing execution history."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])
    first_action = TypeAction(
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input"),
        text="hello",
    )
    action_result = _make_action_result(first_action, url=data_url, html=html)
    async_playwright_patch, executor_patch, scorer_patch, executor_mock, _context = _build_runtime_patches(
        html=html,
        url=data_url,
        action_result=action_result,
        scores=[
            ScoreDetails(raw_score=0.0, tests_passed=0, total_tests=1, success=False),
            ScoreDetails(raw_score=0.0, tests_passed=0, total_tests=1, success=False),
            ScoreDetails(raw_score=0.0, tests_passed=0, total_tests=1, success=False),
        ],
    )

    with (
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        async_playwright_patch,
        executor_patch,
        scorer_patch,
    ):
        evaluator = AsyncStatefulEvaluator(
            task=task,
            web_agent_id=WEB_AGENT_ID,
            should_record_gif=False,
            capture_screenshot=False,
        )
        try:
            await evaluator.reset()
            await evaluator.step(None)  # noop step still triggers score with empty events
            details = await evaluator.get_score_details()
            assert details.total_tests >= 1
            assert details.tests_passed == 0
            assert details.raw_score == 0.0
            assert details.success is False
            assert len(evaluator.history) == 1
            executor_mock.execute_single_action.assert_awaited_once()
        finally:
            await evaluator.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stateful_evaluator_real_server_film_detail():
    """
    Real browser, real demo server (frontend + backend), FILM_DETAIL task with criteria Inception.
    No mocks. reset() navigates to task URL; steps search and open Inception -> score should pass.
    """
    available, reason = _is_real_demo_server_available()
    if not available:
        _skip_if_real_server_unavailable(reason)

    task = _make_real_server_task()
    evaluator = AsyncStatefulEvaluator(
        task=task,
        web_agent_id=WEB_AGENT_ID,
        should_record_gif=False,
        capture_screenshot=False,
    )
    try:
        try:
            await evaluator.reset()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browser unavailable in this environment: {exc}")
        # Step 1: two actions — type search query and submit
        for action in _real_server_step1_actions():
            await evaluator.step(action)
        # Step 2: one action — open film detail
        for action in _real_server_step2_actions():
            await evaluator.step(action)
        details = await evaluator.get_score_details()
        assert details.total_tests >= 1
        assert details.tests_passed >= 1
        assert details.raw_score > 0
        assert details.success is True
    finally:
        await evaluator.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stateful_evaluator_real_server_film_detail_fails_wrong_criteria():
    """
    Same real server and same steps (open Inception), but task requires FILM_DETAIL name='The Matrix'.
    Criteria do not match -> score 0.0, success False.
    """
    available, reason = _is_real_demo_server_available()
    if not available:
        _skip_if_real_server_unavailable(reason)

    task = _make_real_server_task_failing_criteria()
    evaluator = AsyncStatefulEvaluator(
        task=task,
        web_agent_id=WEB_AGENT_ID,
        should_record_gif=False,
        capture_screenshot=False,
    )
    try:
        try:
            await evaluator.reset()
        except PlaywrightError as exc:
            pytest.skip(f"Playwright browser unavailable in this environment: {exc}")
        # Step 1: two actions — type search query and submit
        for action in _real_server_step1_actions():
            await evaluator.step(action)
        # Step 2: one action — open film detail
        for action in _real_server_step2_actions():
            await evaluator.step(action)
        details = await evaluator.get_score_details()
        assert details.total_tests >= 1
        assert details.tests_passed == 0
        assert details.raw_score == 0.0
        assert details.success is False
    finally:
        await evaluator.close()
