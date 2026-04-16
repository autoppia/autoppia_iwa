from __future__ import annotations

import io
import json
from pathlib import Path
from types import ModuleType

import pytest
from rich.console import Console

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


def test_render_report_warns_for_missing_or_invalid_projects():
    for payload in ({"config_summary": {}, "projects": None}, {"config_summary": {}, "projects": []}):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, no_color=True)
        metrics_report._render_report(payload, console)
        text = buf.getvalue()
        assert "Warning" in text


def test_render_report_skips_invalid_agents_and_zero_total_entries():
    payload = _sample_results()
    payload["projects"]["Autocinema"]["invalid-agent"] = "skip-me"
    payload["projects"]["Autocinema"]["Zero Agent"] = {"overall": {"total": 0}, "use_cases": {"X": {}}}
    payload["projects"]["Broken"] = []

    lines = metrics_report.print_and_collect_report(payload)
    joined = "\n".join(lines)

    assert "Agent One" in joined
    assert "Zero Agent" not in joined


def test_render_report_handles_project_panel_exception(monkeypatch):
    payload = _sample_results()
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, no_color=True)
    original_print = console.print

    def _boom(*args, **kwargs):
        renderable = args[0] if args else None
        if getattr(renderable, "title", "") == "[bold]Project: Autocinema[/bold]":
            raise RuntimeError("boom")
        return original_print(*args, **kwargs)

    monkeypatch.setattr(console, "print", _boom)

    metrics_report._render_report(payload, console)

    assert "Error: boom" in buf.getvalue()


def test_run_report_raises_when_no_results_can_be_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="No results path provided"):
        metrics_report.run_report(output_dir=tmp_path, write_summary_file=False)


def test_run_report_skips_summary_write_when_report_lines_are_empty(monkeypatch, tmp_path):
    results_path = tmp_path / "benchmark_results_sample.json"
    results_path.write_text(json.dumps(_sample_results()))
    monkeypatch.setattr(metrics_report, "print_and_collect_report", lambda data: [])

    metrics_report.run_report(results_path=results_path, write_summary_file=True)

    assert not list(tmp_path.glob("metrics_summary_*.txt"))


def test_main_returns_1_when_run_report_raises_value_error(monkeypatch):
    monkeypatch.setattr(metrics_report.sys, "argv", ["metrics_report.py", "/tmp/file.json"])

    def _boom(**kwargs):
        raise ValueError("bad input")

    monkeypatch.setattr(metrics_report, "run_report", _boom)
    assert metrics_report.main() == 1


def test_main_without_args_uses_configured_default_output_dir(monkeypatch, tmp_path):
    captured = {}
    fake_module = ModuleType("autoppia_iwa.config.config")
    fake_module.PROJECT_BASE_DIR = tmp_path / "repo" / "autoppia_iwa"
    monkeypatch.setattr(metrics_report.sys, "argv", ["metrics_report.py"])
    monkeypatch.setitem(__import__("sys").modules, "autoppia_iwa.config.config", fake_module)

    def _capture(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(metrics_report, "run_report", _capture)

    assert metrics_report.main() == 0
    assert captured["output_dir"].endswith("benchmark-output/results")
