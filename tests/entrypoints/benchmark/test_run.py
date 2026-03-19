from __future__ import annotations

import json
from pathlib import Path

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
        mode="concurrent",
        headless=True,
    )

    assert report == {"summary": {"ok": True}}
    assert captured["config"].projects == [fake_project]
    assert isinstance(captured["config"].agents[0], RandomClickerWebAgent)


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
            "mode": "concurrent",
            "max_steps": 5,
            "prompts_per_use_case": 1,
            "runs": 1,
            "parallel": 1,
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
