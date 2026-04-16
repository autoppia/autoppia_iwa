from __future__ import annotations

from pathlib import Path

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import WebProject
from autoppia_iwa.src.evaluation.benchmark import Benchmark, BenchmarkConfig
from autoppia_iwa.src.web_agents.classes import IWebAgent


class _FakeAgent(IWebAgent):
    def __init__(self, agent_id: str, name: str):
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


def _benchmark(tmp_path: Path) -> Benchmark:
    return Benchmark(
        BenchmarkConfig(
            projects=[_project()],
            agents=[_FakeAgent("a1", "Agent One"), _FakeAgent("a2", "Agent Two")],
            base_dir=tmp_path,
            save_results_json=False,
            print_summary=False,
        )
    )


@pytest.mark.asyncio
async def test_run_project_returns_empty_when_no_tasks(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)

    async def _generate(project):
        return []

    monkeypatch.setattr(benchmark, "_generate_tasks", _generate)

    result = await benchmark._run_project(_project(), 1)

    assert result == {}


@pytest.mark.asyncio
async def test_run_project_builds_agent_task_matrix_and_flushes_trace(monkeypatch, tmp_path):
    benchmark = _benchmark(tmp_path)
    tasks = [
        Task(id="t1", url="http://localhost:8000", prompt="one", web_project_id="autocinema"),
        Task(id="t2", url="http://localhost:8000", prompt="two", web_project_id="autocinema"),
    ]

    async def _generate(project):
        return tasks

    async def _run_eval_job(agent, task, run_idx, idx, total):
        return type(
            "EvalResult",
            (),
            {
                "stats": type("Stats", (), {"web_agent_id": f"{agent.id}-{task.id}"})(),
                "web_agent_id": f"{agent.id}-{task.id}",
                "final_score": 1.0,
                "evaluation_time": 0.5,
            },
        )()

    flushed = {"called": False}

    class _Writer:
        def __init__(self, *args, **kwargs):
            pass

        def flush(self):
            flushed["called"] = True

    monkeypatch.setattr(benchmark, "_generate_tasks", _generate)
    monkeypatch.setattr(benchmark, "_run_eval_job", _run_eval_job)
    monkeypatch.setattr("autoppia_iwa.src.evaluation.benchmark.benchmark.TraceWriter", _Writer)

    result = await benchmark._run_project(_project(), 1)

    assert set(result.keys()) == {"a1", "a2"}
    assert set(result["a1"].keys()) == {"t1", "t2"}
    assert flushed["called"] is True
