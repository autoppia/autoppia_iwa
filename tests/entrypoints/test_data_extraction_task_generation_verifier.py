import pytest

from autoppia_iwa.entrypoints.web_verification.data_extraction_task_generation_verifier import DataExtractionTaskGenerationVerifier
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest
from autoppia_iwa.src.demo_webs.classes import WebProject


def _make_project(project_id: str = "autocinema", de_use_cases: list[str] | None = None) -> WebProject:
    return WebProject(
        id=project_id,
        name="Demo",
        backend_url="http://localhost:8000",
        frontend_url="http://localhost:3000",
        use_cases=[],
        events=[],
        data_extraction_use_cases=de_use_cases,
    )


def _make_detask(*, use_case: str, expected: str, seed: int = 1) -> Task:
    task = Task(
        web_project_id="autocinema",
        url=f"http://localhost:3000/?seed={seed}",
        prompt=f"Question for {use_case}",
        tests=[DataExtractionTest(expected_answer=expected)],
    )
    task.de_use_case_name = use_case
    task.task_type = "DEtask"
    task.de_expected_answer = expected
    return task


@pytest.mark.asyncio
async def test_verify_for_project_skips_when_no_de_use_cases(monkeypatch):
    verifier = DataExtractionTaskGenerationVerifier(_make_project(de_use_cases=None))
    monkeypatch.setattr(
        DataExtractionTaskGenerationVerifier,
        "_get_default_de_use_cases_from_module",
        lambda self: [],
    )

    result = await verifier.verify_for_project(seed=1)

    assert result["skipped"] is True
    assert "No DE use cases configured" in result["reason"]
    assert result["total_count"] == 0


@pytest.mark.asyncio
async def test_verify_for_project_passes_when_one_valid_task_per_use_case(monkeypatch):
    verifier = DataExtractionTaskGenerationVerifier(_make_project(de_use_cases=["FIND_A", "FIND_B"]))
    tasks = [
        _make_detask(use_case="FIND_A", expected="alpha", seed=1),
        _make_detask(use_case="FIND_B", expected="beta", seed=1),
    ]

    async def _fake_generate(self, *, seed: int, selected_use_cases: set[str]):
        _ = seed, selected_use_cases
        return tasks, None

    async def _fake_load_dataset(self, seed: int):
        _ = seed
        return {"items": [{"value": "alpha"}, {"value": "beta"}]}

    monkeypatch.setattr(DataExtractionTaskGenerationVerifier, "_generate_de_tasks", _fake_generate)
    monkeypatch.setattr(DataExtractionTaskGenerationVerifier, "_load_dataset", _fake_load_dataset)

    result = await verifier.verify_for_project(seed=1)

    assert result["skipped"] is False
    assert result["all_passed"] is True
    assert result["passed_count"] == 2
    assert result["total_count"] == 2
    assert {row["use_case"] for row in result["results"]} == {"FIND_A", "FIND_B"}


@pytest.mark.asyncio
async def test_verify_for_project_flags_missing_or_inconsistent_tasks(monkeypatch):
    verifier = DataExtractionTaskGenerationVerifier(_make_project(de_use_cases=["FIND_A", "FIND_B"]))
    tasks = [
        _make_detask(use_case="FIND_A", expected="not-in-dataset", seed=99),
    ]

    async def _fake_generate(self, *, seed: int, selected_use_cases: set[str]):
        _ = seed, selected_use_cases
        return tasks, None

    async def _fake_load_dataset(self, seed: int):
        _ = seed
        return {"items": [{"value": "alpha"}]}

    monkeypatch.setattr(DataExtractionTaskGenerationVerifier, "_generate_de_tasks", _fake_generate)
    monkeypatch.setattr(DataExtractionTaskGenerationVerifier, "_load_dataset", _fake_load_dataset)

    result = await verifier.verify_for_project(seed=1)

    assert result["skipped"] is False
    assert result["all_passed"] is False
    assert result["passed_count"] == 0
    assert result["total_count"] == 2
    details = {row["use_case"]: row["detail"] for row in result["results"]}
    assert "Failed checks" in details["FIND_A"]
    assert details["FIND_B"] == "No generated DEtask for this use case"


@pytest.mark.asyncio
async def test_verify_for_project_skips_when_generation_fails(monkeypatch):
    verifier = DataExtractionTaskGenerationVerifier(_make_project(de_use_cases=["FIND_A"]))

    async def _fake_generate(self, *, seed: int, selected_use_cases: set[str]):
        _ = seed, selected_use_cases
        return None, "module not found"

    monkeypatch.setattr(DataExtractionTaskGenerationVerifier, "_generate_de_tasks", _fake_generate)

    result = await verifier.verify_for_project(seed=1)

    assert result["skipped"] is True
    assert result["reason"] == "module not found"
    assert result["total_count"] == 0
