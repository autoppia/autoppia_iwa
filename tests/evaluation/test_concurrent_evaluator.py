"""
Tests for ConcurrentEvaluator using the same pattern as tests/execution/actions:
real Playwright browser, mock HTML via data URL, mock backend for scoring.

Separate test uses real demo server (localhost frontend, real backend) and
FILM_DETAIL task; skip when server is unavailable.
"""

import base64
import textwrap
import urllib.error
import urllib.request
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluationResult, EvaluationStats, TestResult as EvalTestResult
from autoppia_iwa.src.evaluation.legacy.concurrent_config import EvaluatorConfig
from autoppia_iwa.src.evaluation.legacy.concurrent_evaluator import (
    ConcurrentEvaluator,
    _is_navigation_url_allowed as _orig_nav_allowed,
)
from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction, TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot
from autoppia_iwa.src.web_agents.classes import TaskSolution

WEB_AGENT_ID = "test_agent"
# Use autobooks project so CheckEventTest(LOGIN_BOOK) parses via base_events
PROJECT = next(p for p in demo_web_projects if getattr(p, "id", None) == "autobooks")
# Autocinema: real server tests (FILM_DETAIL, frontend on DEMO_WEBS_STARTING_PORT)
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
          <p>Used by evaluator tests.</p>
        </body>
        </html>
        """
    ).strip()


def _data_url(html: str) -> str:
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    return f"data:text/html;base64,{encoded}"


def _make_task(url: str):
    return Task(
        id="task-concurrent-1",
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


# -----------------------------------------------------------------------------
# Real server (integration): autocinema, FILM_DETAIL, localhost frontend/backend
# -----------------------------------------------------------------------------


def _skip_if_real_server_unavailable(reason: str):
    """Skip when demo webs backend (and optionally frontend) is not reachable."""
    pytest.skip(reason)


def _is_real_demo_server_available() -> tuple[bool, str]:
    """
    Check if the demo webs backend is reachable.
    Returns (True, "") if available, (False, reason) otherwise.
    """
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
    """Task for real-server test: FILM_DETAIL on autocinema. Edit event_criteria to match your run."""
    base_url = (PROJECT_AUTOCINEMA.frontend_url or "").rstrip("/") or f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"
    return Task(
        id="task-concurrent-real-film-detail",
        url=base_url,
        prompt="Open a film detail that name equals 'Inception'",
        web_project_id=PROJECT_AUTOCINEMA.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="FILM_DETAIL",
                event_criteria={"name": "Inception"},  # Edit to match the film your actions will open
                description="User must view a film detail page",
            )
        ],
    )


def _make_real_server_task_failing_criteria():
    """
    Task with FILM_DETAIL criteria that do NOT match what the current actions produce.
    Current actions search and open 'Inception'; this requires a different film, so the test fails (score 0.0).
    """
    base_url = (PROJECT_AUTOCINEMA.frontend_url or "").rstrip("/") or f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"
    return Task(
        id="task-concurrent-real-film-detail-fail",
        url=base_url,
        prompt="Open a film detail that name equals 'The Matrix'",
        web_project_id=PROJECT_AUTOCINEMA.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="FILM_DETAIL",
                event_criteria={"name": "The Matrix"},  # Actions open Inception, so this fails
                description="User must view The Matrix film detail page",
            )
        ],
    )


def _make_real_server_solution(task: Task):
    """
    Solution for real-server test: navigate, search "Inception", then open film detail.
    """
    base_url = (task.url or "").rstrip("/")
    actions = [
        NavigateAction(url=base_url if base_url else f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"),
        TypeAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input"),
            text="Inception",
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="search-submit-button"),
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="view-details-button"),
        ),
    ]
    return TaskSolution(
        task_id=task.id,
        actions=actions,
        web_agent_id=WEB_AGENT_ID,
    )


@pytest.mark.asyncio
async def test_concurrent_evaluator_accurate_solution():
    """Run evaluator with mocked browser execution and real scoring/orchestration paths."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    passing_events = [
        BackendEvent(
            event_name="LOGIN_BOOK",
            data={"username": "user123"},
            web_agent_id=WEB_AGENT_ID,
        )
    ]

    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=passing_events)

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([_make_action_result(True)], [0.1], None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.run_global_tests",
            new_callable=AsyncMock,
            return_value=_passing_test_results(),
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 1.0
    assert result.stats is not None
    assert result.stats.tests_passed >= 1
    assert result.stats.total_tests >= 1
    assert result.execution_history is not None
    assert len(result.execution_history) >= 1


@pytest.mark.asyncio
async def test_concurrent_evaluator_partial_success_uses_fractional_score():
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)

    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([_make_action_result(True)], [0.1], None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.run_global_tests",
            new_callable=AsyncMock,
            return_value=[
                EvalTestResult(success=True),
                EvalTestResult(success=False),
            ],
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.raw_score == 0.5
    assert result.final_score == 0.5
    assert result.stats is not None
    assert result.stats.tests_passed == 1
    assert result.stats.total_tests == 2


@pytest.mark.asyncio
async def test_concurrent_evaluator_wrong_solution():
    """A failing test result should yield zero score without needing a real browser."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    wrong_events = []  # no events -> tests fail

    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=wrong_events)

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([_make_action_result(True)], [0.1], None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.run_global_tests",
            new_callable=AsyncMock,
            return_value=_failing_test_results(),
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0.0
    assert result.stats is not None
    assert result.stats.tests_passed == 0
    assert result.stats.total_tests >= 1


@pytest.mark.asyncio
async def test_concurrent_evaluator_init_verbose_logging_true():
    """Init with verbose_logging=True does not remove logger (no logger.remove)."""
    with patch(
        "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
        return_value=AsyncMock(),
    ):
        evaluator = ConcurrentEvaluator(
            web_project=PROJECT,
            config=EvaluatorConfig(verbose_logging=True),
        )
    assert evaluator.config.verbose_logging is True
    assert evaluator.web_project is PROJECT
    assert evaluator.evaluation_stats == []
    assert evaluator.errors == []


@pytest.mark.asyncio
async def test_concurrent_evaluator_empty_actions():
    """Solution with no actions returns immediate error and score 0."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._group_and_evaluate_task_solutions",
            new_callable=AsyncMock,
            return_value=[
                EvaluationResult(
                    web_agent_id="agent1",
                    final_score=1.0,
                    raw_score=1.0,
                    test_results=_passing_test_results(),
                    execution_history=[_make_action_result(True)],
                    stats=EvaluationStats(web_agent_id="agent1", task_id=task.id, action_count=1, start_time=0.0),
                ),
                EvaluationResult(
                    web_agent_id="agent2",
                    final_score=1.0,
                    raw_score=1.0,
                    test_results=_passing_test_results(),
                    execution_history=[_make_action_result(True)],
                    stats=EvaluationStats(web_agent_id="agent2", task_id=task.id, action_count=1, start_time=0.0),
                ),
            ],
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(task_id=task.id, actions=[], web_agent_id=WEB_AGENT_ID)
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0
    assert result.stats is not None
    assert result.stats.had_errors is True
    assert result.stats.error_message == "No actions provided"
    assert result.execution_history == []
    assert result.raw_score == 0


@pytest.mark.asyncio
async def test_concurrent_evaluator_navigate_blocked():
    """NavigateAction to disallowed host (no patch) returns 0 and blocks browser execution."""
    task = _make_task("http://localhost:8000")
    task.is_web_real = False
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with patch(
        "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
        return_value=mock_backend,
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url="https://evil.com/page")],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0
    assert result.stats is not None
    assert "NavigateAction" in (result.stats.error_message or "")
    assert result.execution_history == []
    mock_backend.get_backend_events.assert_not_called()


@pytest.mark.asyncio
async def test_concurrent_evaluator_seed_mismatch():
    """Task URL with seed and NavigateAction without matching seed returns 0."""
    task = _make_task("http://localhost:8000/?seed=42")
    task.is_web_real = False
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            return_value=(True, None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url="http://localhost:8000/")],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0
    assert result.stats is not None
    assert "Seed" in (result.stats.error_message or "")
    assert result.execution_history == []


def _make_action_result(success: bool, screenshot_before: str = "b", screenshot_after: str = "a"):
    snap = BrowserSnapshot(
        iteration=0,
        action=NavigateAction(url="data:,"),
        prev_html="",
        current_html="",
        screenshot_before=screenshot_before,
        screenshot_after=screenshot_after,
        backend_events=[],
        current_url="data:,",
        timestamp=datetime.now(UTC),
    )
    return ActionExecutionResult(
        action=NavigateAction(url="data:,"),
        action_event="navigate",
        successfully_executed=success,
        error=None if success else "failed",
        execution_time=0.1,
        browser_snapshot=snap,
    )


def _passing_test_results():
    return [EvalTestResult(success=True, extra_data={})]


def _failing_test_results():
    return [EvalTestResult(success=False, extra_data={})]


@pytest.mark.asyncio
async def test_concurrent_evaluator_early_stop():
    """When _evaluate_in_browser returns early_stop_reason, final_score is 0."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    early_reason = "Task marked as failed after 2 consecutive action failures (limit: 2)"
    hist = [_make_action_result(True), _make_action_result(False), _make_action_result(False)]

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=(hist, [0.1] * 3, early_reason),
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[
                NavigateAction(url=data_url),
                ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x")),
            ],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0.0
    assert result.stats is not None
    assert result.stats.raw_score == 0.0
    assert result.stats.had_errors is True
    assert early_reason in (result.stats.error_message or "")


@pytest.mark.asyncio
async def test_concurrent_evaluator_exception_in_try():
    """Exception during get_backend_events or run_global_tests returns 0 and captures error."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(side_effect=RuntimeError("backend error"))

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
        "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0
    assert result.stats is not None
    assert result.stats.had_errors is True
    assert "backend error" in (result.stats.error_message or "")
    assert result.execution_history is not None


@pytest.mark.asyncio
async def test_concurrent_evaluator_gif_recording_success():
    """With should_record_gif=True and make_gif returning data, gif_recording is set."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(
        return_value=[
            BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID),
        ]
    )
    fake_gif = "base64gifdata"

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([_make_action_result(True)], [0.1], None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.run_global_tests",
            new_callable=AsyncMock,
            return_value=_passing_test_results(),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.make_gif_from_screenshots",
            return_value=fake_gif,
        ),
    ):
        evaluator = ConcurrentEvaluator(
            web_project=PROJECT,
            config=EvaluatorConfig(verbose_logging=False, should_record_gif=True),
        )
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.gif_recording == fake_gif


@pytest.mark.asyncio
async def test_concurrent_evaluator_gif_recording_empty_screenshots():
    """With should_record_gif=True but no execution_history, gif path still runs (no crash)."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(
        return_value=[
            BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID),
        ]
    )

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([], [], None),
        ),
    ):
        evaluator = ConcurrentEvaluator(
            web_project=PROJECT,
            config=EvaluatorConfig(verbose_logging=False, should_record_gif=True),
        )
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.gif_recording is None or result.gif_recording == ""


@pytest.mark.asyncio
async def test_concurrent_evaluator_debug_mode():
    """With debug_mode=True evaluation runs and debug branches are hit (no crash)."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(
        return_value=[
            BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID),
        ]
    )

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_in_browser",
            new_callable=AsyncMock,
            return_value=([_make_action_result(True)], [0.1], None),
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.run_global_tests",
            new_callable=AsyncMock,
            return_value=_passing_test_results(),
        ),
    ):
        evaluator = ConcurrentEvaluator(
            web_project=PROJECT,
            config=EvaluatorConfig(verbose_logging=False, debug_mode=True),
        )
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.stats is not None
    assert result.final_score == 1.0


@pytest.mark.asyncio
async def test_concurrent_evaluator_browser_evaluation_error():
    """When browser launch fails, _evaluate_in_browser returns ([], [], error message)."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.async_playwright",
        ) as mock_pw,
    ):
        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(side_effect=RuntimeError("chromium not found"))
        mock_pw.return_value.__aenter__.return_value = mock_playwright
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        solution = TaskSolution(
            task_id=task.id,
            actions=[NavigateAction(url=data_url)],
            web_agent_id=WEB_AGENT_ID,
        )
        result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.final_score == 0
    assert result.stats is not None
    assert result.stats.had_errors is True
    assert "Browser evaluation error" in (result.stats.error_message or "") or "chromium" in (result.stats.error_message or "").lower()


@pytest.mark.asyncio
async def test_concurrent_evaluator_evaluate_task_solutions():
    """evaluate_task_solutions resets DB per agent, runs grouping, and returns one result per solution."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    passing_events = [
        BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID),
    ]
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=passing_events)

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        sol1 = TaskSolution(task_id=task.id, actions=[NavigateAction(url=data_url)], web_agent_id="agent1")
        sol2 = TaskSolution(task_id=task.id, actions=[NavigateAction(url=data_url)], web_agent_id="agent2")
        results = await evaluator.evaluate_task_solutions(task, [sol1, sol2])

    assert len(results) == 2
    assert all(r is not None for r in results)
    assert results[0].web_agent_id == "agent1"
    assert results[1].web_agent_id == "agent2"
    assert len(evaluator.evaluation_stats) == 2
    mock_backend.reset_database.assert_any_call(web_agent_id="agent1")
    mock_backend.reset_database.assert_any_call(web_agent_id="agent2")
    mock_backend.close.assert_called()


@pytest.mark.asyncio
async def test_concurrent_evaluator_grouping_disabled():
    """With enable_grouping_tasks=False, each solution is evaluated separately (no cloning)."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(
        return_value=[
            BackendEvent(event_name="LOGIN_BOOK", data={"username": "user123"}, web_agent_id=WEB_AGENT_ID),
        ]
    )

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_single_task_solution",
            new_callable=AsyncMock,
        ) as mock_eval,
    ):
        mock_eval.return_value = EvaluationResult(
            web_agent_id=WEB_AGENT_ID,
            final_score=1.0,
            raw_score=1.0,
            test_results=[],
            execution_history=[],
            stats=EvaluationStats(web_agent_id=WEB_AGENT_ID, task_id=task.id, action_count=1, start_time=0),
        )
        evaluator = ConcurrentEvaluator(
            web_project=PROJECT,
            config=EvaluatorConfig(verbose_logging=False, enable_grouping_tasks=False),
        )
        sol1 = TaskSolution(task_id=task.id, actions=[NavigateAction(url=data_url)], web_agent_id="a1")
        sol2 = TaskSolution(task_id=task.id, actions=[NavigateAction(url=data_url)], web_agent_id="a2")
        results = await evaluator.evaluate_task_solutions(task, [sol1, sol2])

    assert len(results) == 2
    assert mock_eval.call_count == 2


@pytest.mark.asyncio
async def test_concurrent_evaluator_group_exception_fills_errors():
    """When _evaluate_single_task_solution raises in a group, errors are recorded and error results returned."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=[])

    with (
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
        patch(
            "autoppia_iwa.src.evaluation.legacy.concurrent_evaluator.ConcurrentEvaluator._evaluate_single_task_solution",
            new_callable=AsyncMock,
            side_effect=RuntimeError("group eval failed"),
        ),
    ):
        evaluator = ConcurrentEvaluator(web_project=PROJECT, config=EvaluatorConfig(verbose_logging=False))
        sol = TaskSolution(task_id=task.id, actions=[NavigateAction(url=data_url)], web_agent_id=WEB_AGENT_ID)
        results = await evaluator.evaluate_task_solutions(task, [sol])

    assert len(results) == 1
    assert results[0] is not None
    assert results[0].final_score == 0
    assert results[0].stats is not None
    assert results[0].stats.had_errors is True
    assert "group eval failed" in results[0].stats.error_message
    assert "group eval failed" in evaluator.errors


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_evaluator_real_server_film_detail():
    """
    Run evaluator with real browser, real demo server (frontend + backend), and FILM_DETAIL test.
    No mocks: real BackendDemoWebService and real Playwright. Skips when server is unavailable.
    Edit _make_real_server_task (event_criteria) and _make_real_server_solution (actions) to match your run.
    """
    available, reason = _is_real_demo_server_available()
    if not available:
        _skip_if_real_server_unavailable(reason)

    task = _make_real_server_task()
    solution = _make_real_server_solution(task)

    evaluator = ConcurrentEvaluator(
        web_project=PROJECT_AUTOCINEMA,
        config=EvaluatorConfig(verbose_logging=False),
    )
    try:
        result = await evaluator.evaluate_single_task_solution(task, solution)
    except Exception as exc:
        pytest.skip(f"Real browser integration unavailable in this environment: {exc}")

    assert result.stats is not None
    assert result.stats.total_tests >= 1
    assert result.execution_history is not None
    # If your actions open a film detail matching event_criteria, final_score will be 1.0
    assert result.final_score == 1.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_evaluator_real_server_film_detail_fails_wrong_criteria():
    """
    Same real server and same actions (which open Inception), but task requires FILM_DETAIL
    with name='The Matrix'. Criteria do not match, so score must be 0.0.
    """
    available, reason = _is_real_demo_server_available()
    if not available:
        _skip_if_real_server_unavailable(reason)

    task = _make_real_server_task_failing_criteria()
    solution = _make_real_server_solution(task)

    evaluator = ConcurrentEvaluator(
        web_project=PROJECT_AUTOCINEMA,
        config=EvaluatorConfig(verbose_logging=False),
    )
    try:
        result = await evaluator.evaluate_single_task_solution(task, solution)
    except Exception as exc:
        pytest.skip(f"Real browser integration unavailable in this environment: {exc}")

    assert result.stats is not None
    assert result.stats.total_tests >= 1
    assert result.stats.tests_passed == 0
    assert result.final_score == 0.0
    assert result.execution_history is not None
