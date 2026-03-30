from __future__ import annotations

from pathlib import Path

import pytest

from modules.debugger import server


def test_annotate_step_only_keeps_html_diff():
    step = {
        "before": {"html": "<div>a</div>", "screenshot": None},
        "after": {"html": "<div>b</div>", "screenshot": None},
        "agent": {"reasoning": "x", "done": False},
    }

    annotated = server._annotate_step(step)

    assert "html" in annotated["diffs"]
    assert "state" not in annotated["diffs"]


def test_resolve_trace_dir_requires_index(tmp_path):
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()

    with pytest.raises(Exception):
        server._resolve_trace_dir(str(trace_dir))


def test_main_sets_trace_dir_and_runs_uvicorn(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        "argparse.ArgumentParser.parse_args",
        lambda self: type("Args", (), {"trace_dir": "/tmp/traces", "port": 9999, "host": "127.0.0.1"})(),
    )
    monkeypatch.setattr(
        "uvicorn.run",
        lambda app, host, port, log_level: captured.update({"app": app, "host": host, "port": port, "log_level": log_level}),
    )

    server.main()

    assert captured["app"] is server.app
    assert captured["port"] == 9999
    assert captured["log_level"] == "warning"
