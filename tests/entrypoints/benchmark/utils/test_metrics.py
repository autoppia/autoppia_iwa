"""Tests for entrypoints.benchmark.utils.metrics."""

import statistics

from autoppia_iwa.entrypoints.benchmark.utils.metrics import (
    TimingMetrics,
    compute_statistics,
)


def test_timing_metrics_start_end_total():
    m = TimingMetrics()
    assert m.get_total_time() == 0.0
    m.start()
    m.end()
    assert m.get_total_time() >= 0.0


def test_timing_metrics_record_solution_and_evaluation():
    m = TimingMetrics()
    m.record_solution_time("agent1", "task1", 1.5)
    m.record_solution_time("agent1", "task2", 2.5)
    m.record_evaluation_time("agent1", "task1", 0.5)
    assert m.get_avg_solution_time("agent1") == 2.0
    assert m.get_avg_evaluation_time("agent1") == 0.5
    assert m.get_avg_solution_time("unknown") == 0.0
    assert m.get_avg_evaluation_time("unknown") == 0.0


def test_compute_statistics_empty():
    out = compute_statistics([])
    assert out["count"] == 0
    assert out["mean"] is None
    assert out["median"] is None
    assert out["min"] is None
    assert out["max"] is None
    assert out["stdev"] is None


def test_compute_statistics_values():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    out = compute_statistics(values)
    assert out["count"] == 5
    assert out["mean"] == 3.0
    assert out["median"] == 3.0
    assert out["min"] == 1.0
    assert out["max"] == 5.0
    assert out["stdev"] == statistics.stdev(values)


def test_compute_statistics_single_value():
    out = compute_statistics([4.5])
    assert out["count"] == 1
    assert out["mean"] == 4.5
    assert out["stdev"] == 0.0
