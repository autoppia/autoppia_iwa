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


class _FakeAction:
    type = "click"

    def model_dump(self):
        return {"type": self.type, "selector": "#ok"}


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


def test_build_terminal_report_delegates_with_results_path(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    benchmark.last_run_report = {"summary": {"ok": True}}
    benchmark.last_results_path = "/tmp/report.json"

    captured = {}

    def _build_terminal_report(report, *, config, results_path):
        captured["report"] = report
        captured["config"] = config
        captured["results_path"] = results_path
        return "terminal report"

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.build_terminal_report", _build_terminal_report)

    assert benchmark.build_terminal_report() == "terminal report"
    assert captured["report"] == {"summary": {"ok": True}}
    assert captured["results_path"] == "/tmp/report.json"


def test_save_results_builds_report_when_missing(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    benchmark._results = {"Autocinema": {"Agent One": {"passed": 1}}}

    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.benchmark.build_run_report",
        lambda **kwargs: {"summary": kwargs["summary"], "projects": kwargs["project_reports"]},
    )

    saved = {}

    def _save_run_report(data, path):
        saved["data"] = data
        saved["path"] = path

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.save_run_report", _save_run_report)

    benchmark._save_results()

    assert saved["data"] == {"summary": benchmark._results, "projects": benchmark._project_reports}
    assert saved["path"].suffix == ".json"
    assert benchmark.last_results_path == str(saved["path"])


@pytest.mark.asyncio
async def test_run_project_returns_empty_when_no_tasks(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)

    async def _generate_tasks(project):
        return []

    monkeypatch.setattr(benchmark, "_generate_tasks", _generate_tasks)
    assert await benchmark._run_project(_project(), 1) == {}


@pytest.mark.asyncio
async def test_run_project_builds_results_from_jobs(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    tasks = [
        Task(id="t1", url="http://localhost:8000", prompt="a", web_project_id="autocinema"),
        Task(id="t2", url="http://localhost:8000", prompt="b", web_project_id="autocinema"),
    ]

    async def _generate_tasks(project):
        return tasks

    async def _run_eval_job(agent, task, run_idx, idx, total):
        return SimpleNamespace(
            stats=SimpleNamespace(web_agent_id=f"eval-{task.id}"),
            web_agent_id=f"eval-{task.id}",
        )

    monkeypatch.setattr(benchmark, "_generate_tasks", _generate_tasks)
    monkeypatch.setattr(benchmark, "_run_eval_job", _run_eval_job)
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.benchmark.build_task_result",
        lambda **kwargs: {"task_id": kwargs["task"].id, "eval_id": kwargs["eval_id"], "run_idx": kwargs["run_idx"]},
    )

    result = await benchmark._run_project(_project(), 1)

    assert result["agent-1"]["t1"]["eval_id"] == "eval-t1"
    assert result["agent-1"]["t2"]["task_id"] == "t2"


@pytest.mark.asyncio
async def test_run_stateful_executes_actions_records_trace_and_closes(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    task = Task(id="t1", url="http://localhost:8000", prompt="do", web_project_id="autocinema")
    agent = _FakeAgent()
    action_result = SimpleNamespace(action=_FakeAction(), successfully_executed=True, error=None)

    class _FakeEvaluator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.closed = False

        async def reset(self):
            return SimpleNamespace(
                snapshot=SimpleNamespace(html="<html/>", url="http://localhost:8000", screenshot=b"img"),
                score=SimpleNamespace(success=False, raw_score=0.0, tests_passed=0, total_tests=1),
                action_result=None,
            )

        async def step(self, action):
            return SimpleNamespace(
                snapshot=SimpleNamespace(html="<html>done</html>", url="http://localhost:8000/done", screenshot=b"img2"),
                score=SimpleNamespace(success=True, raw_score=1.0, tests_passed=1, total_tests=1),
                action_result=action_result,
            )

        async def close(self):
            self.closed = True

    class _EpisodeTrace:
        def __init__(self):
            self.steps = []
            self.closed = None

        def record_step(self, **kwargs):
            self.steps.append(kwargs)

        def close(self, **kwargs):
            self.closed = kwargs

    class _TraceWriter:
        def __init__(self):
            self.episode = _EpisodeTrace()

        def start_episode(self, **kwargs):
            self.start_kwargs = kwargs
            return self.episode

    async def _step(**kwargs):
        return [_FakeAction()]

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TaskExecutionSession", _FakeEvaluator)
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.EvaluationStats", lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.EvaluationResult", lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr(agent, "step", _step)
    benchmark._trace_writer = _TraceWriter()

    result = await benchmark._run_stateful(task, agent, "eval-1", "validator-1")

    assert result.final_score == 1.0
    assert result.stats.action_count == 1
    assert result.execution_history == [action_result]
    assert benchmark._trace_writer.episode.steps[0]["actions"][0]["type"] == "click"
    assert benchmark._trace_writer.episode.closed["success"] is True


@pytest.mark.asyncio
async def test_run_stateful_breaks_on_agent_step_exception(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    task = Task(id="t1", url="http://localhost:8000", prompt="do", web_project_id="autocinema")
    agent = _FakeAgent()

    class _FakeEvaluator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def reset(self):
            return SimpleNamespace(
                snapshot=SimpleNamespace(html="<html/>", url="http://localhost:8000", screenshot=None),
                score=SimpleNamespace(success=False, raw_score=0.25, tests_passed=0, total_tests=1),
                action_result=None,
            )

        async def close(self):
            return None

    async def _step(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TaskExecutionSession", _FakeEvaluator)
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.EvaluationStats", lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.EvaluationResult", lambda **kwargs: SimpleNamespace(**kwargs))
    monkeypatch.setattr(agent, "step", _step)

    result = await benchmark._run_stateful(task, agent, "eval-1", "validator-1")

    assert result.final_score == 0.25
    assert result.stats.action_count == 0


@pytest.mark.asyncio
async def test_run_orchestrates_projects_and_optional_outputs(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    benchmark.config.print_summary = True
    benchmark.config.save_results_json = True

    async def _run_project(project, run_idx):
        return {"ok": project.id, "run": run_idx}

    monkeypatch.setattr(benchmark, "_run_project", _run_project)
    monkeypatch.setattr(benchmark, "_aggregate_project", lambda project, run_results: benchmark._results.setdefault(project.name, {"runs": len(run_results)}))
    monkeypatch.setattr(benchmark, "_build_run_report", lambda: {"summary": benchmark._results})
    monkeypatch.setattr(benchmark, "_save_results", lambda: setattr(benchmark, "last_results_path", "/tmp/results.json"))
    monkeypatch.setattr(benchmark, "build_terminal_report", lambda: "summary")

    result = await benchmark.run()

    assert result["Autocinema"]["runs"] == 1
    assert benchmark.last_run_report == {"summary": benchmark._results}
