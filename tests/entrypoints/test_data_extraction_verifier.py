import pytest

from autoppia_iwa.entrypoints.web_verification.data_extraction_verifier import DataExtractionTrajectoryVerifier
from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory, WebProject


def _make_project(project_id: str = "autocinema") -> WebProject:
    return WebProject(
        id=project_id,
        name="Demo",
        backend_url="http://localhost:8000",
        frontend_url="http://localhost:3000",
        use_cases=[],
        events=[],
    )


def _make_trajectory(*, trajectory_id: str, seed: int, use_case: str) -> DataExtractionTrajectory:
    return DataExtractionTrajectory(
        web_project_id="autocinema",
        seed=seed,
        use_case=use_case,
        question="What value should be extracted?",
        expected_answer="value",
        actions=["stub_action"],
        id=trajectory_id,
    )


def _make_dataset_only_trajectory(*, trajectory_id: str, seed: int, use_case: str, expected_answer: str) -> DataExtractionTrajectory:
    return DataExtractionTrajectory(
        web_project_id="autocinema",
        seed=seed,
        use_case=use_case,
        question="What is the director?",
        expected_answer=expected_answer,
        actions=None,
        id=trajectory_id,
    )


@pytest.mark.asyncio
async def test_verify_for_use_case_skips_when_project_has_no_registry(monkeypatch):
    project = _make_project("unknown_project")
    verifier = DataExtractionTrajectoryVerifier(project)

    monkeypatch.setattr(
        "autoppia_iwa.entrypoints.web_verification.data_extraction_verifier.get_data_extraction_trajectories",
        lambda _project_id: None,
    )

    result = await verifier.verify_for_use_case(use_case_name="FILM_DETAIL", seed=1)

    assert result["skipped"] is True
    assert "No data-extraction trajectory registry" in result["reason"]
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_verify_for_use_case_skips_when_no_matching_seed_or_use_case(monkeypatch):
    project = _make_project("autocinema")
    verifier = DataExtractionTrajectoryVerifier(project)
    trajectories = [
        _make_trajectory(trajectory_id="t1", seed=2, use_case="FILM_DETAIL"),
        _make_trajectory(trajectory_id="t2", seed=1, use_case="SEARCH_FILM"),
    ]

    monkeypatch.setattr(
        "autoppia_iwa.entrypoints.web_verification.data_extraction_verifier.get_data_extraction_trajectories",
        lambda _project_id: trajectories,
    )

    result = await verifier.verify_for_use_case(use_case_name="FILM_DETAIL", seed=1)

    assert result["skipped"] is True
    assert result["reason"] == "No data-extraction trajectories for use case 'FILM_DETAIL' and seed=1"
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_verify_for_use_case_filters_and_counts_pass_fail(monkeypatch):
    project = _make_project("autocinema")
    verifier = DataExtractionTrajectoryVerifier(project)
    trajectories = [
        _make_trajectory(trajectory_id="ok-1", seed=1, use_case="FILM_DETAIL"),
        _make_trajectory(trajectory_id="ko-1", seed=1, use_case="FILM_DETAIL"),
        _make_trajectory(trajectory_id="ignored-seed", seed=2, use_case="FILM_DETAIL"),
        _make_trajectory(trajectory_id="ignored-usecase", seed=1, use_case="SEARCH_FILM"),
    ]

    monkeypatch.setattr(
        "autoppia_iwa.entrypoints.web_verification.data_extraction_verifier.get_data_extraction_trajectories",
        lambda _project_id: trajectories,
    )

    async def _fake_load_dataset(self, seed):
        return {"movies": [{"name": "x"}]}

    async def _fake_run_one(self, trajectory):
        return (trajectory.id.startswith("ok"), f"detail-{trajectory.id}")

    monkeypatch.setattr(DataExtractionTrajectoryVerifier, "_load_dataset", _fake_load_dataset)
    monkeypatch.setattr(DataExtractionTrajectoryVerifier, "_run_one_replay", _fake_run_one)

    result = await verifier.verify_for_use_case(use_case_name="film_detail", seed=1)

    assert result["skipped"] is False
    assert result["total_count"] == 2
    assert result["passed_count"] == 1
    assert result["all_passed"] is False
    assert {row["trajectory_id"] for row in result["results"]} == {"ok-1", "ko-1"}


@pytest.mark.asyncio
async def test_verify_for_use_case_dataset_only_mode_matches_expected(monkeypatch):
    project = _make_project("autocinema")
    verifier = DataExtractionTrajectoryVerifier(project)
    trajectories = [
        _make_dataset_only_trajectory(trajectory_id="de-1", seed=1, use_case="FILM_DETAIL", expected_answer="Christopher Nolan"),
    ]

    monkeypatch.setattr(
        "autoppia_iwa.entrypoints.web_verification.data_extraction_verifier.get_data_extraction_trajectories",
        lambda _project_id: trajectories,
    )

    async def _fake_load_dataset(self, seed):
        return {"movies": [{"director": "Christopher Nolan"}]}

    monkeypatch.setattr(DataExtractionTrajectoryVerifier, "_load_dataset", _fake_load_dataset)

    result = await verifier.verify_for_use_case(use_case_name="FILM_DETAIL", seed=1)

    assert result["skipped"] is False
    assert result["all_passed"] is True
    assert result["passed_count"] == 1
    assert result["results"][0]["mode"] == "dataset_only"


@pytest.mark.asyncio
async def test_verify_for_project_runs_all_seed_trajectories(monkeypatch):
    project = _make_project("autocinema")
    verifier = DataExtractionTrajectoryVerifier(project)
    trajectories = [
        _make_trajectory(trajectory_id="ok-1", seed=1, use_case="FILM_DETAIL"),
        _make_trajectory(trajectory_id="ko-1", seed=1, use_case="SEARCH_FILM"),
        _make_trajectory(trajectory_id="ignored-seed", seed=2, use_case="FILTER_FILM"),
    ]

    monkeypatch.setattr(
        "autoppia_iwa.entrypoints.web_verification.data_extraction_verifier.get_data_extraction_trajectories",
        lambda _project_id: trajectories,
    )

    async def _fake_load_dataset(self, seed):
        return {"movies": [{"name": "x"}]}

    async def _fake_run_one(self, trajectory):
        return (trajectory.id.startswith("ok"), f"detail-{trajectory.id}")

    monkeypatch.setattr(DataExtractionTrajectoryVerifier, "_load_dataset", _fake_load_dataset)
    monkeypatch.setattr(DataExtractionTrajectoryVerifier, "_run_one_replay", _fake_run_one)

    result = await verifier.verify_for_project(seed=1)

    assert result["skipped"] is False
    assert result["project_id"] == "autocinema"
    assert result["total_count"] == 2
    assert result["passed_count"] == 1
    assert result["all_passed"] is False
    assert result["use_cases_tested"] == ["FILM_DETAIL", "SEARCH_FILM"]
