"""
Tests for AsyncStatefulEvaluator using the same pattern as tests/execution/actions:
real Playwright browser, mock HTML via data URL, mock backend for scoring.
Screenshot is disabled (capture_screenshot=False).
"""

import base64
import textwrap
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.evaluation.stateful_evaluator.evaluator import (
    _is_navigation_url_allowed as _orig_nav_allowed,
)
from autoppia_iwa.src.execution.actions.actions import TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType

WEB_AGENT_ID = "test_agent"
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


@pytest.mark.asyncio
async def test_stateful_evaluator_correct_solution():
    """Reset loads mock HTML; step runs real action; mock backend returns passing events."""
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
            "autoppia_iwa.src.evaluation.stateful_evaluator.evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator.evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
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
            # After one step (e.g. type), backend events from mock -> score can pass
            sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input")
            step_result = await evaluator.step(TypeAction(selector=sel, text="hello"))
            details = await evaluator.get_score_details()
            assert details.total_tests >= 1
            assert details.tests_passed >= 1
            assert details.raw_score > 0
            assert details.success is True
        finally:
            await evaluator.close()


@pytest.mark.asyncio
async def test_stateful_evaluator_wrong_solution():
    """Mock backend returns no events; score should be 0."""
    html = _make_mock_html()
    data_url = _data_url(html)
    task = _make_task(data_url)
    wrong_events = []

    mock_backend = AsyncMock()
    mock_backend.reset_database = AsyncMock()
    mock_backend.close = AsyncMock()
    mock_backend.get_backend_events = AsyncMock(return_value=wrong_events)

    with (
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator.evaluator._is_navigation_url_allowed",
            side_effect=_allow_data_url,
        ),
        patch(
            "autoppia_iwa.src.evaluation.stateful_evaluator.evaluator.BackendDemoWebService",
            return_value=mock_backend,
        ),
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
        finally:
            await evaluator.close()
