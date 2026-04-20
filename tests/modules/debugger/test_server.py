from __future__ import annotations

import pytest
from fastapi import HTTPException

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


def test_resolve_trace_dir_requires_index(tmp_path, monkeypatch):
    # Relative path under cwd so _resolve_trace_dir uses the safe cwd-relative branch
    # (absolute /tmp/... paths are not under the project cwd and return 403).
    monkeypatch.chdir(tmp_path)
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()

    with pytest.raises(HTTPException) as exc_info:
        server._resolve_trace_dir("trace")
    assert exc_info.value.status_code == 404


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


def test_resolved_lookup_keys_rejects_unsafe_input():
    assert server._resolved_lookup_keys("/tmp/traces") == []
    assert server._resolved_lookup_keys("../traces") == []
    assert server._resolved_lookup_keys("./benchmark-output\\traces/run_1") == ["benchmark-output/traces/run_1"]


def test_resolve_trace_dir_accepts_absolute_default_when_allowlisted(monkeypatch, tmp_path):
    trace_dir = tmp_path / "trace"
    trace_dir.mkdir()
    (trace_dir / "trace_index.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(server, "DEFAULT_TRACE_DIR", str(trace_dir))
    monkeypatch.setattr(server, "_trace_dir_allowlist", lambda: {str(trace_dir): trace_dir})

    assert server._resolve_trace_dir() == trace_dir


def test_resolve_trace_dir_accepts_safe_relative_alias(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    trace_dir = tmp_path / "benchmark-output" / "traces" / "run_1"
    trace_dir.mkdir(parents=True)
    (trace_dir / "trace_index.json").write_text("{}", encoding="utf-8")

    assert server._resolve_trace_dir("./benchmark-output/traces/run_1") == trace_dir
