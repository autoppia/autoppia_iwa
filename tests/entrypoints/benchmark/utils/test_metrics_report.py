from __future__ import annotations

import json
from pathlib import Path

import pytest

from autoppia_iwa.entrypoints.benchmark.utils import metrics_report


def _sample_results() -> dict:
    return {
        "timestamp": "2026-03-30T12:00:00",
        "total_execution_time": 12.34,
        "config_summary": {
            "tasks_source": "json",
            "tasks_json_path": "/tmp/tasks.json",
        },
        "projects": {
            "Autocinema": {
                "Agent One": {
                    "overall": {
                        "total": 2,
                        "success_count": 1,
                        "success_rate": 0.5,
                        "avg_solution_time": 1.25,
                        "avg_cost_per_task_usd": 0.12,
                        "total_cost_usd": 0.24,
                        "total_input_tokens": 100,
                        "total_output_tokens": 50,
                    },
                    "use_cases": {
                        "FILM_DETAIL": {
                            "task-1": {
                                "success": 1.0,
                                "time": 1.2,
                                "evaluation_time": 0.4,
                                "cost_usd": 0.1,
                                "input_tokens": 10,
                                "output_tokens": 5,
                                "steps_count": 2,
                            }
                        }
                    },
                }
            }
        },
    }


def test_safe_helpers_and_format_cost():
    assert metrics_report._safe_float("1.5") == 1.5
    assert metrics_report._safe_float("x", 7.0) == 7.0
    assert metrics_report._safe_int("2") == 2
    assert metrics_report._safe_int(None, 9) == 9
    assert metrics_report._fmt_cost(None) == "—"
    assert metrics_report._fmt_cost("0.1") == "$0.100000"


def test_load_consolidated_results_validation(tmp_path):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        metrics_report.load_consolidated_results(missing)

    bad_dir = tmp_path / "dir"
    bad_dir.mkdir()
    with pytest.raises(ValueError, match="not a file"):
        metrics_report.load_consolidated_results(bad_dir)

    invalid = tmp_path / "bad.json"
    invalid.write_text("{not-json}")
    with pytest.raises(ValueError, match="Invalid JSON"):
        metrics_report.load_consolidated_results(invalid)

    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps([1, 2, 3]))
    with pytest.raises(ValueError, match="Expected JSON object"):
        metrics_report.load_consolidated_results(wrong)


def test_print_and_collect_report_returns_plain_text_lines(capsys):
    lines = metrics_report.print_and_collect_report(_sample_results())
    joined = "\n".join(lines)

    assert "BENCHMARK METRICS REPORT" in joined
    assert "Autocinema" in joined
    assert "Agent One" in joined
    assert lines
    assert capsys.readouterr().out


def test_run_report_finds_latest_file_and_writes_summary(tmp_path, capsys):
    old_file = tmp_path / "benchmark_results_old.json"
    new_file = tmp_path / "benchmark_results_new.json"
    old_file.write_text(json.dumps(_sample_results()))
    new_file.write_text(json.dumps(_sample_results()))

    metrics_report.run_report(output_dir=tmp_path, write_summary_file=True)

    summary = tmp_path / f"metrics_summary_{new_file.stem}.txt"
    assert summary.exists()
    assert "Summary written to" in capsys.readouterr().out


def test_run_report_warns_when_summary_cannot_be_written(monkeypatch, tmp_path, capsys):
    results_path = tmp_path / "benchmark_results_sample.json"
    results_path.write_text(json.dumps(_sample_results()))

    def _boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", _boom)

    metrics_report.run_report(results_path=results_path, write_summary_file=True)

    assert "could not write summary file" in capsys.readouterr().err


def test_main_returns_1_on_missing_file(monkeypatch):
    monkeypatch.setattr(metrics_report.sys, "argv", ["metrics_report.py", "/definitely/missing.json"])
    assert metrics_report.main() == 1


def test_main_returns_0_when_run_report_succeeds(monkeypatch):
    monkeypatch.setattr(metrics_report.sys, "argv", ["metrics_report.py", "/tmp/file.json"])
    monkeypatch.setattr(metrics_report, "run_report", lambda **kwargs: None)
    assert metrics_report.main() == 0
