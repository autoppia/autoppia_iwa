from __future__ import annotations

from types import SimpleNamespace

import pytest

from autoppia_iwa.entrypoints.benchmark.config import BenchmarkConfig
from autoppia_iwa.entrypoints.benchmark.task_strategies import (
    DataExtractionTaskStrategy,
    EventTaskStrategy,
)
from autoppia_iwa.src.demo_webs.classes import WebProject


def _make_project(project_id: str = "autocinema", de_use_cases: list[str] | None = None) -> WebProject:
    return WebProject(
        id=project_id,
        name="Test Project",
        backend_url="http://localhost:8090",
        frontend_url="http://localhost:8000",
        use_cases=[],
        events=[],
        data_extraction_use_cases=de_use_cases,
    )


def test_event_strategy_uses_config_use_cases(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project()],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        use_cases=["SEARCH_MOVIE"],
    )
    project = cfg.projects[0]
    strategy = EventTaskStrategy()
    assert strategy.get_selected_use_cases(cfg, project) == ["SEARCH_MOVIE"]


def test_data_extraction_strategy_uses_config_filter_when_provided(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project(de_use_cases=["A", "B", "C"])],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        data_extraction_use_cases=["B"],
    )
    project = cfg.projects[0]
    strategy = DataExtractionTaskStrategy()
    assert strategy.get_selected_use_cases(cfg, project) == ["B"]


def test_data_extraction_strategy_defaults_to_project_de_use_cases_when_none(tmp_path):
    cfg = BenchmarkConfig(
        projects=[_make_project(de_use_cases=["A", "B", "C"])],
        agents=[SimpleNamespace(id="agent-1")],
        base_dir=tmp_path,
        data_extraction_use_cases=None,
    )
    project = cfg.projects[0]
    strategy = DataExtractionTaskStrategy()
    assert strategy.get_selected_use_cases(cfg, project) == ["A", "B", "C"]


def test_config_requires_at_least_one_enabled_pipeline(tmp_path):
    with pytest.raises(ValueError, match="At least one task pipeline must be enabled"):
        BenchmarkConfig(
            projects=[_make_project()],
            agents=[SimpleNamespace(id="agent-1")],
            base_dir=tmp_path,
            enable_event_tasks=False,
            enable_data_extraction_tasks=False,
        )
