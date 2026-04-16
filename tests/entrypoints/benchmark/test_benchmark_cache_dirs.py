from __future__ import annotations

from types import SimpleNamespace

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
        test_types="event_only",
        base_dir=tmp_path,
    )
    benchmark = Benchmark(cfg)

    cache_dir = benchmark._get_task_cache_dir()
    assert cache_dir.endswith("benchmark-output/cache/tasks")


def test_benchmark_cache_dir_data_extraction_only_uses_data_extraction_folder(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        test_types="data_extraction_only",
        base_dir=tmp_path,
    )
    benchmark = Benchmark(cfg)

    cache_dir = benchmark._get_task_cache_dir()
    assert cache_dir.endswith("benchmark-output/cache/DataExtraction")
