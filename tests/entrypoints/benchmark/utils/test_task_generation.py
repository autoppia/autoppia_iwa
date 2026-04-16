"""Tests for canonical benchmark task generation utilities."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.benchmark.utils import task_generation


def _make_project(pid: str = "p1", name: str = "Project 1") -> WebProject:
    return WebProject(
        id=pid,
        name=name,
        backend_url="http://example.com/",
        frontend_url="http://example.com/",
        use_cases=[],
    )


def test_filter_tasks_by_use_cases_none_means_no_filter():
    class _UC:
        def __init__(self, name: str):
            self.name = name

    class _T:
        def __init__(self, name: str):
            self.use_case = _UC(name)

    tasks = [_T("LOGIN"), _T("SEARCH")]
    assert task_generation.filter_tasks_by_use_cases(tasks, None) is tasks
    assert len(task_generation.filter_tasks_by_use_cases(tasks, [])) == 2


def test_filter_tasks_by_use_cases_matches_name_case_insensitive():
    class _UC:
        def __init__(self, name: str):
            self.name = name

    class _T:
        def __init__(self, name: str):
            self.use_case = _UC(name)

    tasks = [_T("REQUEST_QUICK_APPOINTMENT"), _T("LOGIN"), _T("REQUEST_QUICK_APPOINTMENT")]
    out = task_generation.filter_tasks_by_use_cases(tasks, ["request_quick_appointment"])
    assert len(out) == 2
    assert all(t.use_case.name.startswith("REQUEST") for t in out)


def test_filter_tasks_by_use_cases_drops_tasks_without_use_case_or_de_name():
    class _T:
        use_case = None

    tasks = [_T(), _T()]
    assert task_generation.filter_tasks_by_use_cases(tasks, ["LOGIN"]) == []
    assert task_generation.filter_tasks_by_use_cases(tasks, ["LOGIN"], test_types="data_extraction_only") == []


def test_filter_tasks_by_use_cases_matches_de_use_case_name_for_data_extraction():
    class _T:
        use_case = None
        de_use_case_name = "FIND_PRICE"

    tasks = [_T()]
    out = task_generation.filter_tasks_by_use_cases(tasks, ["find_price"], test_types="data_extraction_only")
    assert len(out) == 1


def test_get_cache_filename():
    project = _make_project("autocinema_1", "Auto Cinema")
    path = task_generation.get_cache_filename(project, "/tmp/cache")
    assert path == Path("/tmp/cache/autocinema_1_tasks.json")

    project_slash = _make_project("foo/bar", "Foo")
    path_slash = task_generation.get_cache_filename(project_slash, "/tmp")
    assert path_slash == Path("/tmp/foo_bar_tasks.json")


@pytest.mark.asyncio
async def test_save_tasks_to_json(tmp_path):
    project = _make_project()
    tasks = [
        Task(url="http://example.com", prompt="Do something", web_project_id="p1"),
    ]
    result = await task_generation.save_tasks_to_json(tasks, project, str(tmp_path))
    assert result is True
    filename = tmp_path / "p1_tasks.json"
    assert filename.exists()
    data = json.loads(filename.read_text())
    assert data["project_id"] == "p1"
    assert data["project_name"] == "Project 1"
    assert "tasks" in data
    assert len(data["tasks"]) == 1


@pytest.mark.asyncio
async def test_save_tasks_to_json_creates_parent_dirs(tmp_path):
    project = _make_project()
    tasks = [Task(url="http://x", prompt="X", web_project_id="p1")]
    deep_dir = tmp_path / "a" / "b" / "c"
    result = await task_generation.save_tasks_to_json(tasks, project, str(deep_dir))
    assert result is True
    assert (deep_dir / "p1_tasks.json").exists()


@pytest.mark.asyncio
async def test_load_tasks_from_json_none_when_missing(tmp_path):
    project = _make_project("missing", "M")
    out = await task_generation.load_tasks_from_json(project, str(tmp_path))
    assert out is None


@pytest.mark.asyncio
async def test_load_tasks_from_json(tmp_path):
    project = _make_project()
    tasks = [
        Task(url="http://example.com", prompt="Task 1", web_project_id="p1"),
    ]
    await task_generation.save_tasks_to_json(tasks, project, str(tmp_path))
    loaded = await task_generation.load_tasks_from_json(project, str(tmp_path))
    assert loaded is not None
    assert len(loaded) == 1
    assert loaded[0].prompt == "Task 1"
    assert loaded[0].url == "http://example.com"


@pytest.mark.asyncio
async def test_load_tasks_from_json_empty_tasks_list_returns_none(tmp_path):
    project = _make_project()
    filename = task_generation.get_cache_filename(project, str(tmp_path))
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(json.dumps({"project_id": "p1", "tasks": []}, indent=2))
    out = await task_generation.load_tasks_from_json(project, str(tmp_path))
    assert out is None


@pytest.mark.asyncio
async def test_generate_tasks_for_project_returns_list():
    project = _make_project()
    with patch.object(
        task_generation.TaskGenerationPipeline,
        "generate",
        new_callable=AsyncMock,
    ) as mock_gen:
        mock_gen.return_value = [
            Task(url="http://x", prompt="P", web_project_id=project.id),
        ]
        tasks = await task_generation.generate_tasks_for_project(project, prompts_per_use_case=1)
    assert len(tasks) == 1
    assert tasks[0].prompt == "P"


@pytest.mark.asyncio
async def test_generate_tasks_for_project_exception_returns_empty():
    project = _make_project()
    with patch.object(
        task_generation.TaskGenerationPipeline,
        "generate",
        side_effect=ValueError("fail"),
    ):
        tasks = await task_generation.generate_tasks_for_project(project)
    assert tasks == []


def test_get_projects_by_ids_empty_all_projects():
    out = task_generation.get_projects_by_ids([], ["a"])
    assert out == []


def test_get_projects_by_ids_empty_ids():
    p = _make_project()
    out = task_generation.get_projects_by_ids([p], [])
    assert out == []


def test_get_projects_by_ids_success():
    p1 = _make_project("a", "A")
    p2 = _make_project("b", "B")
    out = task_generation.get_projects_by_ids([p1, p2], ["b", "a"])
    assert out == [p2, p1]


def test_get_projects_by_ids_missing_raises():
    p1 = _make_project("a", "A")
    with pytest.raises(ValueError, match="Project IDs not found"):
        task_generation.get_projects_by_ids([p1], ["a", "missing"])


def test_entrypoint_task_generation_module_re_exports_canonical_objects():
    from autoppia_iwa.entrypoints.benchmark.utils import task_generation as entrypoint_task_generation

    assert entrypoint_task_generation.get_projects_by_ids is task_generation.get_projects_by_ids
    assert entrypoint_task_generation.save_tasks_to_json is task_generation.save_tasks_to_json
