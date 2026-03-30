from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig
from autoppia_iwa.src.web_agents.classes import IWebAgent


class _FakeAgent(IWebAgent):
    def __init__(self, agent_id: str = "agent-1", name: str = "Agent One"):
        self.id = agent_id
        self.name = name

    async def step(self, *, task, html, screenshot=None, url, step_index, history=None):
        return []


def _project() -> WebProject:
    return WebProject(
        id="autocinema",
        name="Autocinema",
        backend_url="http://localhost:8090",
        frontend_url="http://localhost:8000",
    )


def _benchmark(tmp_path: Path, *, agents=None, projects=None) -> Benchmark:
    config = BenchmarkConfig(
        projects=projects if projects is not None else [_project()],
        agents=agents if agents is not None else [_FakeAgent()],
        base_dir=tmp_path,
        save_results_json=False,
        print_summary=False,
    )
    return Benchmark(config)


def test_benchmark_validate_rejects_missing_projects_and_duplicate_agents(tmp_path):
    with pytest.raises(ValueError, match="No projects configured"):
        _benchmark(tmp_path, projects=[])

    dup_agents = [_FakeAgent("dup"), _FakeAgent("dup")]
    with pytest.raises(ValueError, match="Agent IDs must be unique"):
        _benchmark(tmp_path, agents=dup_agents)


@pytest.mark.asyncio
async def test_generate_tasks_uses_pipeline_and_saves_cache(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    tasks = [Task(id="t1", url="http://localhost:8000", prompt="do", web_project_id="autocinema")]

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.load_tasks_from_json", lambda *args, **kwargs: [])

    class _Pipeline:
        def __init__(self, web_project, config):
            self.web_project = web_project
            self.config = config

        async def generate(self):
            return tasks

    saved = {}

    async def _save_tasks(tasks_arg, project_arg, cache_dir):
        saved["tasks"] = tasks_arg
        saved["project"] = project_arg
        saved["cache_dir"] = cache_dir

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TaskGenerationPipeline", _Pipeline)
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.save_tasks_to_json", _save_tasks)

    result = await benchmark._generate_tasks(_project())

    assert result == tasks
    assert saved["tasks"] == tasks
    assert saved["project"].id == "autocinema"
    assert saved["cache_dir"].endswith("benchmark-output/cache/tasks")


def test_compact_history_serializes_execution_events(tmp_path):
    benchmark = _benchmark(tmp_path)

    class _Action:
        def model_dump(self):
            return {"type": "ClickAction"}

    history = [
        SimpleNamespace(action=_Action(), successfully_executed=True, error=None),
        SimpleNamespace(action=None, successfully_executed=False, error="timeout"),
    ]

    compact = benchmark._compact_history(history)

    assert compact == [
        {"index": 0, "action": {"type": "ClickAction"}, "success": True, "error": None},
        {"index": 1, "action": None, "success": False, "error": "timeout"},
    ]


def test_aggregate_project_and_save_results_use_reporting_helpers(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    project = _project()

    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.benchmark.aggregate_project_results",
        lambda **kwargs: (
            {"Agent One": {"passed": 2, "total": 3, "success_rate": 2 / 3}},
            {"project": kwargs["project"].id},
        ),
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.benchmark.build_run_report",
        lambda **kwargs: {"summary": kwargs["summary"], "projects": kwargs["project_reports"]},
    )

    saved = {}

    def _save_run_report(data, path):
        saved["data"] = data
        saved["path"] = path

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.save_run_report", _save_run_report)

    benchmark._aggregate_project(project, run_results=[{"ok": True}])
    benchmark.last_run_report = benchmark._build_run_report()
    benchmark._save_results()

    assert benchmark._results[project.name]["Agent One"]["passed"] == 2
    assert benchmark._project_reports[project.name] == {"project": project.id}
    assert saved["data"] == benchmark.last_run_report
    assert saved["path"].name.startswith("benchmark_")
