"""
Tests for the generate_tasks API endpoint.
Uses mocked generate_tasks_for_project so no LLM/OpenAI is called.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch target: the endpoint module imports generate_tasks_for_project and get_projects_by_ids
PATCH_TASK_GEN = "autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.generate_tasks_for_project"


def _make_fake_task(use_case_name: str, prompt: str):
    """Minimal task-like object with use_case.name and prompt for endpoint response building."""
    return SimpleNamespace(use_case=SimpleNamespace(name=use_case_name), prompt=prompt)


@pytest.fixture
def mock_generate_tasks():
    """Mock generate_tasks_for_project to return fake tasks without calling LLM."""
    with patch(PATCH_TASK_GEN, new_callable=AsyncMock) as m:
        m.return_value = [
            _make_fake_task("SEARCH_BOOK", "Find a book named 'Test Book'"),
            _make_fake_task("SEARCH_BOOK", "Search for a book by author 'Test Author'"),
            _make_fake_task("BOOK_DETAIL", "Show details for the book 'Another Title'"),
        ]
        yield m


@pytest.fixture
def client():
    """FastAPI test client for the generate_tasks app."""
    from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import app

    return TestClient(app)


def test_post_generate_tasks_returns_200_and_structure(client, mock_generate_tasks):
    """POST /generate-tasks with hardcoded request returns 200 and correct response shape."""
    payload = {
        "projects": ["autobooks"],
        "prompts_per_use_case": 1,
        "selective_use_cases": [],
        "runs": 1,
        "dynamic": False,
    }
    response = client.post("/generate-tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "generated_tasks" in data
    generated = data["generated_tasks"]
    assert isinstance(generated, list)
    assert len(generated) >= 1
    # One entry per project_id
    project_entry = generated[0]
    assert "project_id" in project_entry
    assert project_entry["project_id"] == "autobooks"
    assert "tasks" in project_entry
    tasks_by_uc = project_entry["tasks"]
    assert isinstance(tasks_by_uc, dict)
    # Our mock returns SEARCH_BOOK and BOOK_DETAIL
    assert "SEARCH_BOOK" in tasks_by_uc
    assert "BOOK_DETAIL" in tasks_by_uc
    assert len(tasks_by_uc["SEARCH_BOOK"]) == 2
    assert len(tasks_by_uc["BOOK_DETAIL"]) == 1
    assert "Find a book named 'Test Book'" in tasks_by_uc["SEARCH_BOOK"]
    assert "Show details for the book 'Another Title'" in tasks_by_uc["BOOK_DETAIL"]

    mock_generate_tasks.assert_called_once()
    call_kwargs = mock_generate_tasks.call_args[1]
    assert call_kwargs["prompts_per_use_case"] == 1
    assert call_kwargs["use_cases"] is None
    assert call_kwargs["dynamic"] is False


def test_post_generate_tasks_with_selective_use_cases(client, mock_generate_tasks):
    """POST /generate-tasks with selective_use_cases passes them to generator."""
    payload = {
        "projects": ["autobooks"],
        "prompts_per_use_case": 2,
        "selective_use_cases": ["SEARCH_BOOK", "BOOK_DETAIL"],
        "runs": 1,
        "dynamic": True,
    }
    response = client.post("/generate-tasks", json=payload)
    assert response.status_code == 200
    mock_generate_tasks.assert_called_once()
    call_kwargs = mock_generate_tasks.call_args[1]
    assert call_kwargs["use_cases"] == ["SEARCH_BOOK", "BOOK_DETAIL"]
    assert call_kwargs["prompts_per_use_case"] == 2
    assert call_kwargs["dynamic"] is True


def test_post_generate_tasks_multiple_runs(client, mock_generate_tasks):
    """POST /generate-tasks with runs=2 calls generator twice per project."""
    payload = {
        "projects": ["autobooks"],
        "prompts_per_use_case": 1,
        "selective_use_cases": [],
        "runs": 2,
        "dynamic": False,
    }
    response = client.post("/generate-tasks", json=payload)
    assert response.status_code == 200
    # 2 runs x 1 project = 2 calls
    assert mock_generate_tasks.call_count == 2


def test_post_generate_tasks_invalid_body_returns_422(client):
    """Invalid request body returns 422."""
    # Empty projects list is invalid (min 1 item implied by usage)
    response = client.post("/generate-tasks", json={})
    assert response.status_code == 422


def test_post_generate_tasks_multiple_projects(client, mock_generate_tasks):
    """POST with multiple projects calls generator for each project."""
    payload = {
        "projects": ["autobooks", "autocinema"],
        "prompts_per_use_case": 1,
        "selective_use_cases": [],
        "runs": 1,
        "dynamic": False,
    }
    response = client.post("/generate-tasks", json=payload)
    assert response.status_code == 200
    assert mock_generate_tasks.call_count == 2
    data = response.json()
    assert len(data["generated_tasks"]) == 2
    project_ids = {t["project_id"] for t in data["generated_tasks"]}
    assert project_ids == {"autobooks", "autocinema"}


def test_post_generate_tasks_runs_capped_at_max(client, mock_generate_tasks):
    """runs=10 (max allowed) results in 10 generator calls."""
    from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import MAX_GENERATION_RUNS

    payload = {
        "projects": ["autobooks"],
        "prompts_per_use_case": 1,
        "selective_use_cases": [],
        "runs": MAX_GENERATION_RUNS,
        "dynamic": False,
    }
    response = client.post("/generate-tasks", json=payload)
    assert response.status_code == 200
    assert mock_generate_tasks.call_count == MAX_GENERATION_RUNS


def test_generate_task_config_model():
    """GenerateTaskConfig validates and defaults."""
    from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import GenerateTaskConfig

    config = GenerateTaskConfig(projects=["autobooks"], prompts_per_use_case=2)
    assert config.projects == ["autobooks"]
    assert config.prompts_per_use_case == 2
    assert config.selective_use_cases == []
    assert config.runs == 1
    assert config.dynamic is False

    config2 = GenerateTaskConfig(
        projects=["a", "b"],
        prompts_per_use_case=1,
        selective_use_cases=["UC1"],
        runs=3,
        dynamic=True,
    )
    assert config2.selective_use_cases == ["UC1"]
    assert config2.runs == 3
    assert config2.dynamic is True


@pytest.mark.asyncio
async def test_cli_main_project_not_found():
    """cli_main returns when project not found."""
    with patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.get_projects_by_ids") as mock_get:
        mock_get.return_value = []
        from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import cli_main

        await cli_main()
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_cli_main_no_tasks_generated():
    """cli_main when generate_tasks_for_project returns empty."""
    from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import (
        cli_main,
        demo_web_projects,
        get_projects_by_ids,
    )

    projects = get_projects_by_ids(demo_web_projects, ["autobooks"])
    assert projects

    with patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.get_projects_by_ids", return_value=projects), patch(PATCH_TASK_GEN, new_callable=AsyncMock, return_value=[]):
        await cli_main()


@pytest.mark.asyncio
async def test_cli_main_success_saves_tasks(tmp_path):
    """cli_main with mocked generator and save saves to cache."""
    from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import (
        cli_main,
        demo_web_projects,
        get_projects_by_ids,
    )

    projects = get_projects_by_ids(demo_web_projects, ["autobooks"])
    assert projects

    with patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.get_projects_by_ids", return_value=projects), patch(PATCH_TASK_GEN, new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = [
            _make_fake_task("SEARCH_BOOK", "Find a book"),
        ]
        with (
            patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.CACHE_DIR", str(tmp_path / "cache")),
            patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.save_tasks_to_json", new_callable=AsyncMock) as mock_save,
        ):
            mock_save.return_value = True
            await cli_main()
        mock_gen.assert_called_once()
        mock_save.assert_called_once()


def test_main_cli_mode_calls_cli_main():
    """main() with --cli runs cli_main."""
    with (
        patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.cli_main", new_callable=AsyncMock),
        patch("autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint.asyncio.run") as mock_run,
    ):
        from autoppia_iwa.entrypoints.generate_tasks.generate_tasks_endpoint import main

        with patch("sys.argv", ["prog", "--cli"]):
            main()
        mock_run.assert_called_once()
