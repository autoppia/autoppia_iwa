from __future__ import annotations

import json

import pytest

from autoppia_iwa.entrypoints.benchmark import run as benchmark_run
from autoppia_iwa.src.web_agents.examples.random_clicker.agent import RandomClickerWebAgent


def test_build_agent_supports_random_clicker():
    agent = benchmark_run._build_agent("random-clicker")
    assert isinstance(agent, RandomClickerWebAgent)
    assert agent.id == "random-clicker"


def test_stage_tasks_supports_single_project_payload(tmp_path):
    class _Config:
        base_dir = tmp_path

    payload = {"project_id": "autobooks", "tasks": [{"id": "t1"}]}
    source = tmp_path / "tasks.json"
    source.write_text(json.dumps(payload))

    benchmark_run._stage_tasks(source, _Config())

    staged = tmp_path / "benchmark-output" / "cache" / "tasks" / "autobooks_tasks.json"
    assert json.loads(staged.read_text())["project_id"] == "autobooks"


def test_stage_tasks_supports_multi_project_payload(tmp_path):
    class _Config:
        base_dir = tmp_path

    payload = {
        "autobooks": {"project_id": "autobooks", "tasks": [{"id": "t1"}]},
        "autocinema": {"project_id": "autocinema", "tasks": [{"id": "t2"}]},
    }
    source = tmp_path / "tasks.json"
    source.write_text(json.dumps(payload))

    benchmark_run._stage_tasks(source, _Config())

    staged_dir = tmp_path / "benchmark-output" / "cache" / "tasks"
    assert (staged_dir / "autobooks_tasks.json").exists()
    assert (staged_dir / "autocinema_tasks.json").exists()


@pytest.mark.asyncio
async def test_run_builds_random_clicker_benchmark(monkeypatch, tmp_path):
    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    captured = {}

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.utils.task_generation.get_projects_by_ids",
        lambda _all, ids: [fake_project] if ids == ["autobooks"] else [],
    )

    class FakeBenchmark:
        def __init__(self, config):
            captured["config"] = config
            self.last_run_report = {"summary": {"ok": True}}

        async def run(self):
            return {"ok": True}

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.Benchmark", FakeBenchmark)

    report = await benchmark_run.run(
        agent="random-clicker",
        project_ids=["autobooks"],
        output_dir=str(tmp_path),
        headless=True,
    )

    assert report == {"summary": {"ok": True}}
    assert captured["config"].projects == [fake_project]
    assert isinstance(captured["config"].agents[0], RandomClickerWebAgent)


@pytest.mark.asyncio
async def test_run_rejects_legacy_concurrent_mode(monkeypatch):
    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)

    with pytest.raises(ValueError, match="Only stateful benchmark mode is supported"):
        await benchmark_run.run(agent="random-clicker", mode="concurrent")


def test_main_exits_non_zero_on_bad_tasks_file(monkeypatch, tmp_path, capsys):
    bad_tasks = tmp_path / "bad.json"
    bad_tasks.write_text(json.dumps({"unexpected": []}))
    args = type(
        "Args",
        (),
        {
            "agent": "random-clicker",
            "project": None,
            "use_case": None,
            "tasks": str(bad_tasks),
            "output": str(tmp_path),
            "max_steps": 5,
            "prompts_per_use_case": 1,
            "runs": 1,
            "parallel": 1,
            "web_agent_prefix": "benchmark-agent",
            "validator_prefix": None,
            "headless": True,
        },
    )()
    monkeypatch.setattr(benchmark_run, "_parse_args", lambda: args)
    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [])

    with pytest.raises(SystemExit) as exc:
        benchmark_run.main()

    assert exc.value.code == 1
    assert "Unsupported tasks file format" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_stateful_benchmark_passes_screenshot_to_agent(monkeypatch, tmp_path):
    from autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig

    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    task = Task(url="http://localhost:3000", prompt="Do something", web_project_id="autobooks")

    class FakeScore:
        def __init__(self, success: bool, raw_score: float):
            self.success = success
            self.raw_score = raw_score
            self.tests_passed = int(success)
            self.total_tests = 1

    class FakeSnapshot:
        def __init__(self, html: str, url: str, screenshot: bytes | None):
            self.html = html
            self.url = url
            self.screenshot = screenshot

    class FakeStepResult:
        def __init__(self, success: bool, screenshot: bytes | None):
            self.score = FakeScore(success=success, raw_score=1.0 if success else 0.0)
            self.snapshot = FakeSnapshot("<html>state</html>", "http://localhost:3000/page", screenshot)
            self.action_result = None

    class FakeTaskExecutionSession:
        def __init__(self, **kwargs):
            assert kwargs["capture_screenshot"] is True
            assert kwargs["validator_id"] == "validator-1"

        async def reset(self):
            return FakeStepResult(success=False, screenshot=b"frame-bytes")

        async def step(self, action):
            return FakeStepResult(success=True, screenshot=b"after")

        async def close(self):
            return None

    class FakeAgent:
        id = "agent-1"
        name = "Agent One"

        def __init__(self):
            self.calls = []

        async def step(self, **kwargs):
            self.calls.append(kwargs)
            return []

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TaskExecutionSession", FakeTaskExecutionSession)

    agent = FakeAgent()
    config = BenchmarkConfig(
        projects=[fake_project],
        agents=[agent],
        evaluator_mode="stateful",
        base_dir=tmp_path,
        save_results_json=False,
        print_summary=False,
    )
    benchmark = Benchmark(config)

    await benchmark._run_stateful(task, agent, "eval-1", "validator-1")

    assert len(agent.calls) == 1
    assert agent.calls[0]["screenshot"] == b"frame-bytes"


@pytest.mark.asyncio
async def test_run_builds_benchmark_with_isolation_prefixes(monkeypatch, tmp_path):
    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    captured = {}

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])

    class FakeBenchmark:
        def __init__(self, config):
            captured["config"] = config
            self.last_run_report = {"summary": {"ok": True}}

        async def run(self):
            return {"ok": True}

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.Benchmark", FakeBenchmark)

    await benchmark_run.run(
        agent="random-clicker",
        output_dir=str(tmp_path),
        parallel=4,
        web_agent_prefix="eval-agent",
        validator_prefix="eval-validator",
    )

    assert captured["config"].max_parallel_evaluations == 4
    assert captured["config"].web_agent_id_prefix == "eval-agent"
    assert captured["config"].validator_id_prefix == "eval-validator"


@pytest.mark.asyncio
async def test_run_eval_job_generates_unique_eval_and_validator_ids(monkeypatch, tmp_path):
    from autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig

    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    task = Task(url="http://localhost:3000", prompt="Do something", web_project_id="autobooks")

    class FakeAgent:
        id = "agent-1"
        name = "Agent One"

    captured = {}

    async def fake_run_stateful(task_arg, agent_arg, eval_id, validator_id):
        captured["task"] = task_arg
        captured["agent"] = agent_arg
        captured["eval_id"] = eval_id
        captured["validator_id"] = validator_id
        return None

    config = BenchmarkConfig(
        projects=[fake_project],
        agents=[FakeAgent()],
        base_dir=tmp_path,
        save_results_json=False,
        print_summary=False,
        web_agent_id_prefix="benchmark-agent",
        validator_id_prefix="validator-bench",
    )
    benchmark = Benchmark(config)
    monkeypatch.setattr(benchmark, "_run_stateful", fake_run_stateful)

    await benchmark._run_eval_job(FakeAgent(), task, 2, 1, 1)

    assert captured["task"] is task
    assert captured["eval_id"].startswith("benchmark-agent-")
    assert captured["eval_id"].endswith("-r2")
    assert captured["validator_id"].startswith("validator-bench-")
    assert captured["validator_id"].endswith("-r2")


@pytest.mark.asyncio
async def test_run_stateful_result_uses_eval_id_in_stats(monkeypatch, tmp_path):
    from autoppia_iwa.src.data_generation.tasks.classes import Task
    from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig

    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    task = Task(url="http://localhost:3000", prompt="Do something", web_project_id="autobooks")

    class FakeScore:
        def __init__(self, success: bool, raw_score: float):
            self.success = success
            self.raw_score = raw_score
            self.tests_passed = int(success)
            self.total_tests = 1

    class FakeSnapshot:
        def __init__(self):
            self.html = "<html>state</html>"
            self.url = "http://localhost:3000/page"
            self.screenshot = b"frame-bytes"

    class FakeStepResult:
        def __init__(self, success: bool):
            self.score = FakeScore(success=success, raw_score=1.0 if success else 0.0)
            self.snapshot = FakeSnapshot()
            self.action_result = None

    class FakeTaskExecutionSession:
        def __init__(self, **kwargs):
            pass

        async def reset(self):
            return FakeStepResult(success=False)

        async def step(self, action):
            return FakeStepResult(success=True)

        async def close(self):
            return None

    class FakeAgent:
        id = "agent-1"
        name = "Agent One"

        async def step(self, **kwargs):
            return []

    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TaskExecutionSession", FakeTaskExecutionSession)

    config = BenchmarkConfig(
        projects=[fake_project],
        agents=[FakeAgent()],
        base_dir=tmp_path,
        save_results_json=False,
        print_summary=False,
    )
    benchmark = Benchmark(config)

    result = await benchmark._run_stateful(task, FakeAgent(), "eval-123", "validator-123")

    assert result.web_agent_id == "eval-123"
    assert result.stats is not None
    assert result.stats.web_agent_id == "eval-123"
