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
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import (
    ConcurrentEvaluator,
    _is_navigation_url_allowed as _orig_nav_allowed,
)
from autoppia_iwa.src.execution.actions.actions import ClickAction, NavigateAction, TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
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
    """Run evaluator with real browser, mock HTML (data URL), and mock backend returning passing events."""
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
            "autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator.BackendDemoWebService",
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

    assert result.final_score == 1.0
    assert result.stats is not None
    assert result.stats.tests_passed >= 1
    assert result.stats.total_tests >= 1
    assert result.execution_history is not None
    assert len(result.execution_history) >= 1


@pytest.mark.asyncio
async def test_concurrent_evaluator_wrong_solution():
    """Run evaluator with mock backend returning no matching events; score should be 0."""
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
            "autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator.BackendDemoWebService",
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

    assert result.final_score == 0.0
    assert result.stats is not None
    assert result.stats.tests_passed == 0
    assert result.stats.total_tests >= 1


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
    result = await evaluator.evaluate_single_task_solution(task, solution)

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
    result = await evaluator.evaluate_single_task_solution(task, solution)

    assert result.stats is not None
    assert result.stats.total_tests >= 1
    assert result.stats.tests_passed == 0
    assert result.final_score == 0.0
    assert result.execution_history is not None
