import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import pytest
from playwright.async_api import Error as PlaywrightError

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.evaluation.stateful_evaluator import AsyncStatefulEvaluator
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction
from autoppia_iwa.src.web_agents.apified_iterative_agent import ApifiedWebAgent

from .test_stateful_evaluator import WEB_AGENT_ID, _is_real_demo_server_available, _skip_if_real_server_unavailable

ROOT_FIXTURE_PATH = Path(__file__).resolve().parents[3] / "all_projects_use_case_trajectories_prod_pxx_step_tests.json"
TRACKING_QUERY_PARAMS = {"X-WebAgent-Id", "web_agent_id", "X-Validator-Id", "validator_id"}
KNOWN_PROD_MISMATCHES: dict[tuple[str, str], str] = {}


def load_project_fixture(project_id: str) -> dict[str, Any]:
    data = json.loads(ROOT_FIXTURE_PATH.read_text())
    for project in data:
        if project["project_id"] == project_id:
            return project
    raise AssertionError(f"Project fixture not found for {project_id}")


def successful_trajectories(project_fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return [trajectory for trajectory in project_fixture["trajectories"] if trajectory.get("has_success")]


def fixture_test_id(project_fixture: dict[str, Any]) -> str:
    return project_fixture["project_id"].replace("p", "trajectories_p", 1)


def assert_project_fixture(project_fixture: dict[str, Any], expected_project_id: str, expected_legacy_name: str) -> None:
    assert project_fixture["project_id"] == expected_project_id
    assert project_fixture["project_name_legacy"] == expected_legacy_name


def project_params(project_fixture: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    return [(index, trajectory) for index, trajectory in enumerate(successful_trajectories(project_fixture))]


def project_ids(project_fixture: dict[str, Any]) -> list[str]:
    return [trajectory["use_case"] for trajectory in successful_trajectories(project_fixture)]


def _build_task(project_fixture: dict[str, Any], index: int, trajectory: dict[str, Any]) -> Task:
    tests = []
    serialized_tests = json.loads(json.dumps(trajectory.get("tests", [])))
    for test_data in serialized_tests:
        criteria = test_data.get("event_criteria")
        if isinstance(criteria, dict):
            for key, value in list(criteria.items()):
                if value == "user<web_agent_id>":
                    criteria[key] = f"user{WEB_AGENT_ID}"
        tests.append(BaseTaskTest.deserialize(test_data))
    return Task(
        id=f"{fixture_test_id(project_fixture)}_{index}_{trajectory['use_case'].lower()}",
        url=trajectory["url"],
        prompt=trajectory["prompt"],
        web_project_id=project_fixture["project_name_legacy"],
        is_web_real=False,
        specifications=BrowserSpecification(),
        tests=tests,
    )


def _normalize_url(action_url: str, task_url: str) -> str:
    task_parts = urlsplit(task_url)
    action_parts = urlsplit(action_url)
    filtered_query = [(key, value) for key, value in parse_qsl(action_parts.query, keep_blank_values=True) if key not in TRACKING_QUERY_PARAMS]
    path = action_parts.path or task_parts.path or "/"
    query = urlencode(filtered_query, doseq=True)
    return urlunsplit((task_parts.scheme, task_parts.netloc, path, query, ""))


def _normalize_action(action: dict[str, Any], task_url: str) -> dict[str, Any]:
    normalized = json.loads(json.dumps(action))
    arguments = normalized.get("arguments", {})
    arguments.pop("attributes", None)

    selector = arguments.get("selector")
    if isinstance(selector, dict):
        selector.pop("attributes", None)

    if normalized.get("name") == "browser.navigate" and isinstance(arguments.get("url"), str):
        arguments["url"] = _normalize_url(arguments["url"], task_url)

    if isinstance(arguments.get("text"), str):
        arguments["text"] = arguments["text"].replace("<web_agent_id>", WEB_AGENT_ID)

    return normalized


def _build_actions(trajectory: dict[str, Any]) -> list[BaseAction]:
    normalized_actions = [_normalize_action(action, trajectory["url"]) for action in trajectory.get("actions", [])]
    parser = ApifiedWebAgent(base_url="http://127.0.0.1:9999")
    built_actions: list[BaseAction] = []
    for action in normalized_actions:
        payload = parser._tool_call_to_action_payload(parser._parse_canonical_response({"tool_calls": [action], "done": False}).tool_calls[0])
        built_action = BaseAction.create_action(payload)
        if built_action is None:
            continue
        if isinstance(built_action, NavigateAction):
            built_action.url = action["arguments"]["url"]
        built_actions.append(built_action)
    return built_actions


def _is_task_frontend_available(task_url: str | None) -> tuple[bool, str]:
    if not task_url:
        return False, "Task URL missing"
    try:
        req = urllib.request.Request(task_url, method="GET")
        req.add_header("User-Agent", "IWA-Trajectories-Test/1.0")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if 200 <= resp.status < 400:
                return True, ""
            return False, f"Frontend returned status {resp.status} for {task_url}"
    except urllib.error.URLError as exc:
        return False, f"Task frontend not reachable for {task_url}: {exc.reason}"
    except OSError as exc:
        return False, f"Task frontend not reachable for {task_url}: {exc}"


async def replay_project_trajectory(project_fixture: dict[str, Any], index: int, trajectory: dict[str, Any]) -> None:
    known_mismatch = KNOWN_PROD_MISMATCHES.get((project_fixture["project_id"], trajectory["use_case"]))
    if known_mismatch:
        pytest.xfail(known_mismatch)

    available, reason = _is_real_demo_server_available()
    if not available:
        _skip_if_real_server_unavailable(reason)

    frontend_available, frontend_reason = _is_task_frontend_available(trajectory.get("url"))
    if not frontend_available:
        pytest.skip(frontend_reason)

    task = _build_task(project_fixture, index, trajectory)
    actions = _build_actions(trajectory)
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

        for action in actions:
            await evaluator.step(action)

        details = await evaluator.get_score_details()
        assert details.total_tests >= 1
        assert details.tests_passed >= 1
        assert details.raw_score > 0
        assert details.success is True
    finally:
        await evaluator.close()
