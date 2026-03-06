"""
Tests for ConcurrentEvaluator using the same pattern as tests/execution/actions:
real Playwright browser, mock HTML via data URL, mock backend for scoring.
"""

import base64
import textwrap
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.classes import EvaluatorConfig
from autoppia_iwa.src.evaluation.concurrent_evaluator.evaluator import (
    ConcurrentEvaluator,
    _is_navigation_url_allowed as _orig_nav_allowed,
)
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.web_agents.classes import TaskSolution

WEB_AGENT_ID = "test_agent"
# Use autobooks project so CheckEventTest(LOGIN_BOOK) parses via base_events
PROJECT = next(p for p in demo_web_projects if getattr(p, "id", None) == "autobooks")


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
