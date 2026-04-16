from __future__ import annotations

from types import SimpleNamespace

import pytest

from autoppia_iwa.entrypoints.benchmark.benchmark import Benchmark
from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.src.demo_webs.classes import WebProject


def _make_project(project_id: str = "autocinema") -> WebProject:
    return WebProject(
        id=project_id,
        name="Test Project",
        backend_url="http://localhost:8090",
        frontend_url="http://localhost:8000",
        use_cases=[],
        events=[],
    )


def test_benchmark_cache_dir_event_only_uses_tasks_folder(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
    )
    benchmark = Benchmark(cfg)

    cache_dir = benchmark._get_task_cache_dir("event")
    assert cache_dir.endswith("benchmark-output/cache/tasks")


def test_benchmark_cache_dir_data_extraction_only_uses_data_extraction_folder(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
    )
    benchmark = Benchmark(cfg)

    cache_dir = benchmark._get_task_cache_dir("data_extraction")
    assert cache_dir.endswith("benchmark-output/cache/DataExtraction")


def test_benchmark_uses_only_event_strategy_when_de_is_disabled(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        enable_event_tasks=True,
        enable_data_extraction_tasks=False,
    )
    benchmark = Benchmark(cfg)

    assert [strategy.name for strategy in benchmark._task_strategies] == ["event"]


def test_benchmark_uses_only_de_strategy_when_event_is_disabled(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        enable_event_tasks=False,
        enable_data_extraction_tasks=True,
    )
    benchmark = Benchmark(cfg)

    assert [strategy.name for strategy in benchmark._task_strategies] == ["data_extraction"]


@pytest.mark.asyncio
async def test_benchmark_run_closes_shared_data_provider_session(monkeypatch, tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        save_results_json=False,
    )
    benchmark = Benchmark(cfg)

    closed = {"called": False}

    async def _close_session():
        closed["called"] = True

    async def _execute_single_project_run(project, run_index):
        _ = (project, run_index)
        return {}

    monkeypatch.setattr("autoppia_iwa.entrypoints.benchmark.benchmark.close_async_session", _close_session)
    monkeypatch.setattr(benchmark, "_execute_single_project_run", _execute_single_project_run)

    await benchmark.run()
    assert closed["called"] is True
