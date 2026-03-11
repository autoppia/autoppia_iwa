"""Tests for entrypoints.benchmark.utils.results."""

from unittest.mock import MagicMock

from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics
from autoppia_iwa.entrypoints.benchmark.utils.results import (
    _has_zero_score,
    print_performance_statistics,
    save_results_to_json,
)


def test_has_zero_score_false():
    assert _has_zero_score({}) is False
    assert _has_zero_score({"a": {"t1": {"score": 1.0}}}) is False


def test_has_zero_score_true():
    assert _has_zero_score({"a": {"t1": {"score": 0.0}}}) is True
    assert _has_zero_score({"a": {"t1": {"score": 1.0}, "t2": {"score": 0.0}}}) is True


def test_save_results_to_json(tmp_path):
    results = {"agent1": {"task1": {"score": 0.8, "task_use_case": "uc1", "prompt": "P"}}}
    agent = MagicMock()
    agent.id = "agent1"
    agent.name = "MyAgent"
    timing = TimingMetrics()
    timing.start()
    timing.end()
    timing.record_solution_time("agent1", "task1", 1.0)
    timing.record_evaluation_time("agent1", "task1", 0.5)
    out = save_results_to_json(results, [agent], timing, str(tmp_path))
    assert "timestamp" in out
    assert "agents" in out
    assert "MyAgent" in out["agents"]
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert "benchmark_results" in files[0].name


def test_save_results_to_json_zero_score_prefix(tmp_path):
    results = {"agent1": {"task1": {"score": 0.0}}}
    agent = MagicMock()
    agent.id = "agent1"
    agent.name = "AgentOne"
    timing = TimingMetrics()
    save_results_to_json(results, [agent], timing, str(tmp_path))
    files = list(tmp_path.glob("r-*.json"))
    assert len(files) == 1


def test_print_performance_statistics(capsys):
    results = {"agent1": {"task1": {"score": 1.0}}}
    agent = MagicMock()
    agent.id = "agent1"
    agent.name = "TestAgent"
    timing = TimingMetrics()
    timing.start()
    timing.end()
    print_performance_statistics(results, [agent], timing)
    captured = capsys.readouterr()
    assert "PERFORMANCE REPORT" in captured.out
    assert "TestAgent" in captured.out
