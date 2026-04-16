from __future__ import annotations

import pytest

from autoppia_iwa.entrypoints.web_verification import event_trajectory_verifier as verifier_module
from autoppia_iwa.entrypoints.web_verification.event_trajectory_verifier import EventTrajectoryVerifier
from autoppia_iwa.src.demo_webs.classes import Trajectory, WebProject
from autoppia_iwa.src.execution.actions.actions import NavigateAction


def _make_project(project_id: str = "autocinema") -> WebProject:
    return WebProject(
        id=project_id,
        name="Test Project",
        backend_url="http://localhost:8090",
        frontend_url="http://localhost:8000",
        use_cases=[],
        events=[],
    )


@pytest.mark.asyncio
async def test_verify_for_project_skips_when_registry_missing(monkeypatch):
    monkeypatch.setattr(verifier_module, "get_trajectory_map", lambda _project_id: None)

    verifier = EventTrajectoryVerifier(_make_project())
    result = await verifier.verify_for_project()

    assert result["skipped"] is True
    assert "No event trajectory registry" in result["reason"]
    assert result["total_count"] == 0
    assert result["passed_count"] == 0


@pytest.mark.asyncio
async def test_verify_for_project_filters_use_cases_and_aggregates(monkeypatch):
    trajectories = {
        "UC_A": Trajectory(
            name="UC_A",
            prompt="Prompt A",
            actions=[NavigateAction(url="http://localhost:8000")],
            tests=[],
        ),
        "UC_B": Trajectory(
            name="UC_B",
            prompt="Prompt B",
            actions=[NavigateAction(url="http://localhost:8000")],
            tests=[],
        ),
    }
    monkeypatch.setattr(verifier_module, "get_trajectory_map", lambda _project_id: trajectories)

    verifier = EventTrajectoryVerifier(_make_project())

    async def _fake_run_one(*, use_case_name: str, trajectory: Trajectory):
        _ = trajectory
        if use_case_name == "UC_A":
            return True, "score=1.000 tests=1/1", {"score": 1.0, "tests_passed": 1, "total_tests": 1}
        return False, "score=0.000 tests=0/1", {"score": 0.0, "tests_passed": 0, "total_tests": 1}

    monkeypatch.setattr(verifier, "_run_one", _fake_run_one)

    filtered_result = await verifier.verify_for_project(use_cases=["uc_a"])
    assert filtered_result["skipped"] is False
    assert filtered_result["total_count"] == 1
    assert filtered_result["passed_count"] == 1
    assert filtered_result["all_passed"] is True
    assert filtered_result["use_cases_tested"] == ["UC_A"]

    all_result = await verifier.verify_for_project()
    assert all_result["total_count"] == 2
    assert all_result["passed_count"] == 1
    assert all_result["all_passed"] is False
