import urllib.error
import urllib.request

import pytest

from autoppia_iwa.config.config import DEMO_WEB_SERVICE_PORT, DEMO_WEBS_ENDPOINT
from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.demo_webs.config import demo_web_projects
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.execution.actions.base import BaseAction

WEB_AGENT_ID = "trajectory_replay_agent"
PROJECT_AUTOCINEMA = next(p for p in demo_web_projects if getattr(p, "id", None) == "autocinema")


def _is_real_demo_server_available() -> tuple[bool, str]:
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
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status in (200, 204):
                return True, ""
            return False, f"backend status {resp.status}"
    except urllib.error.URLError as e:
        return False, f"demo webs backend not reachable: {e.reason}"
    except OSError as e:
        return False, f"demo webs backend not reachable: {e}"


def _make_task(*, event_criteria: dict) -> Task:
    base_url = (PROJECT_AUTOCINEMA.frontend_url or "").rstrip("/") or f"{DEMO_WEBS_ENDPOINT.rstrip('/')}:8000"
    return Task(
        id="trajectory-replay-film-detail",
        url=base_url,
        prompt="Open a film detail that name equals 'Inception'",
        web_project_id=PROJECT_AUTOCINEMA.id,
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="FILM_DETAIL",
                event_criteria=event_criteria,
                description="Replay trajectory should trigger FILM_DETAIL event criteria",
            )
        ],
    )


def _trajectory_actions() -> list[BaseAction]:
    raw_actions = [
        {
            "type": "TypeAction",
            "selector": {
                "type": "attributeValueSelector",
                "attribute": "id",
                "value": "input",
                "case_sensitive": False,
            },
            "text": "Inception",
        },
        {
            "type": "ClickAction",
            "selector": {
                "type": "attributeValueSelector",
                "attribute": "id",
                "value": "search-submit-button",
                "case_sensitive": False,
            },
        },
        {
            "type": "ClickAction",
            "selector": {
                "type": "attributeValueSelector",
                "attribute": "id",
                "value": "view-details-button",
                "case_sensitive": False,
            },
        },
        {"type": "WaitAction", "time_seconds": 1.0},
    ]
    return [BaseAction.create_action(a) for a in raw_actions]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trajectory_replay_non_zero_score():
    available, reason = _is_real_demo_server_available()
    if not available:
        pytest.skip(reason)

    evaluator = AsyncStatefulEvaluator(
        task=_make_task(event_criteria={"name": "Inception"}),
        web_agent_id=WEB_AGENT_ID,
        should_record_gif=False,
        capture_screenshot=False,
    )
    try:
        await evaluator.reset()
        for action in _trajectory_actions():
            await evaluator.step(action)
        details = await evaluator.get_score_details()
        assert details.total_tests >= 1
        assert details.raw_score > 0.0
        assert details.success is True
    finally:
        await evaluator.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trajectory_replay_zero_score_with_wrong_criteria():
    available, reason = _is_real_demo_server_available()
    if not available:
        pytest.skip(reason)

    evaluator = AsyncStatefulEvaluator(
        task=_make_task(event_criteria={"name": "The Matrix"}),
        web_agent_id=WEB_AGENT_ID,
        should_record_gif=False,
        capture_screenshot=False,
    )
    try:
        await evaluator.reset()
        for action in _trajectory_actions():
            await evaluator.step(action)
        details = await evaluator.get_score_details()
        assert details.total_tests >= 1
        assert details.raw_score == 0.0
        assert details.success is False
    finally:
        await evaluator.close()
