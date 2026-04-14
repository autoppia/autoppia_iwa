from __future__ import annotations

import importlib

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest

MODULES = [
    "autoppia_iwa.src.demo_webs.projects.autobooks_2.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autocalendar_11.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autoconnect_9.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autocrm_5.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autodelivery_7.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autodining_4.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autodrive_13.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autohealth_14.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autolist_12.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autolodge_8.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.automail_6.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autowork_10.dataExtractionUseCases",
    "autoppia_iwa.src.demo_webs.projects.autozone_3.dataExtractionUseCases",
]


def _fake_task_for_use_case(*, project_id: str, task_url: str, use_case_name: str) -> Task:
    task = Task(
        web_project_id=project_id,
        url=task_url,
        prompt=f"Question for {use_case_name}",
        tests=[DataExtractionTest(expected_answer=f"answer-{use_case_name}")],
    )
    task.de_use_case_name = use_case_name
    task.task_type = "DEtask"
    task.de_expected_answer = f"answer-{use_case_name}"
    return task


@pytest.mark.parametrize("module_path", MODULES)
@pytest.mark.asyncio
async def test_generate_de_tasks_for_each_project_module(monkeypatch, module_path: str):
    module = importlib.import_module(module_path)
    expected_count = len(module.DATA_EXTRACTION_USE_CASES)

    async def _fake_fetch_data(*args, **kwargs):
        _ = args, kwargs
        return [{"name": "row", "value": "x"}]

    def _fake_build_de_task(**kwargs):
        return _fake_task_for_use_case(
            project_id=kwargs["project_id"],
            task_url=kwargs["task_url"],
            use_case_name=kwargs["use_case_name"],
        )

    monkeypatch.setattr(module, "fetch_data", _fake_fetch_data)
    monkeypatch.setattr(module, "build_de_task", _fake_build_de_task)

    tasks = await module.generate_de_tasks(seed=1, task_url="http://localhost:8000", selected_use_cases=None)

    assert len(tasks) == expected_count
    assert all(isinstance(task, Task) for task in tasks)
    assert all(getattr(task, "task_type", "") == "DEtask" for task in tasks)


@pytest.mark.parametrize("module_path", MODULES)
@pytest.mark.asyncio
async def test_generate_de_tasks_respects_selected_use_cases(monkeypatch, module_path: str):
    module = importlib.import_module(module_path)
    first_uc = module.DATA_EXTRACTION_USE_CASES[0].name
    if len(module.DATA_EXTRACTION_USE_CASES) > 1:
        selected_input = {
            first_uc.lower(),
            f" {module.DATA_EXTRACTION_USE_CASES[1].name} ",
        }
    else:
        selected_input = {f" {first_uc.lower()} "}

    async def _fake_fetch_data(*args, **kwargs):
        _ = args, kwargs
        return [{"name": "row", "value": "x"}]

    def _fake_build_de_task(**kwargs):
        return _fake_task_for_use_case(
            project_id=kwargs["project_id"],
            task_url=kwargs["task_url"],
            use_case_name=kwargs["use_case_name"],
        )

    monkeypatch.setattr(module, "fetch_data", _fake_fetch_data)
    monkeypatch.setattr(module, "build_de_task", _fake_build_de_task)

    tasks = await module.generate_de_tasks(
        seed=2,
        task_url="http://localhost:8000",
        selected_use_cases=selected_input,
    )

    names = {getattr(task, "de_use_case_name", "") for task in tasks}
    assert names == {name.strip().upper() for name in selected_input}
    assert len(tasks) == len(selected_input)


@pytest.mark.asyncio
async def test_autowork_load_rows_falls_back_from_jobs_to_experts(monkeypatch):
    module = importlib.import_module("autoppia_iwa.src.demo_webs.projects.autowork_10.dataExtractionUseCases")
    calls: list[str] = []

    async def _fake_fetch_data(*args, **kwargs):
        entity = kwargs.get("entity_type")
        calls.append(str(entity))
        if entity == "jobs":
            return []
        return [{"name": "expert-row"}]

    monkeypatch.setattr(module, "fetch_data", _fake_fetch_data)

    rows = await module._load_rows_for_use_case(seed=3, use_case_name="FIND_JOB")

    assert rows == [{"name": "expert-row"}]
    assert calls[:2] == ["jobs", "experts"]


@pytest.mark.asyncio
async def test_automail_load_rows_uses_email_fallback_on_template_error(monkeypatch):
    module = importlib.import_module("autoppia_iwa.src.demo_webs.projects.automail_6.dataExtractionUseCases")
    calls: list[str] = []

    async def _fake_fetch_data(*args, **kwargs):
        entity = kwargs.get("entity_type")
        calls.append(str(entity))
        if entity == "templates":
            raise RuntimeError("templates unavailable")
        return [{"subject": "hello", "from_name": "sender"}]

    monkeypatch.setattr(module, "fetch_data", _fake_fetch_data)

    rows = await module._load_rows_for_use_case(seed=5, use_case_name="FIND_TEMPLATE")

    assert rows == [{"subject": "hello", "from_name": "sender"}]
    assert calls[:2] == ["templates", "emails"]
