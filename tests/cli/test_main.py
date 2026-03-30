from __future__ import annotations

from unittest.mock import Mock

import pytest

from autoppia_iwa.cli import main as cli_main


def test_cli_main_prints_help(capsys):
    assert cli_main.main([]) == 0
    out = capsys.readouterr().out
    assert "usage: iwa <command>" in out
    assert "benchmark" in out


def test_cli_main_unknown_command(capsys):
    assert cli_main.main(["missing"]) == 1
    out = capsys.readouterr().out
    assert "Unknown command: missing" in out


def test_cli_main_dash_help_prints_command_help(capsys):
    assert cli_main.main(["--help"]) == 0
    out = capsys.readouterr().out
    assert "usage: iwa <command>" in out
    assert "generate-tasks" in out


@pytest.mark.parametrize(
    ("command", "target"),
    [
        ("check", "autoppia_iwa.entrypoints.check.run.main"),
        ("benchmark", "autoppia_iwa.entrypoints.benchmark.run.main"),
        ("generate-tasks", "autoppia_iwa.entrypoints.generate_tasks.run.main"),
        ("verify", "autoppia_iwa.entrypoints.web_verification.run.main"),
        ("debug", "modules.debugger.server.main"),
    ],
)
def test_cli_main_dispatches(monkeypatch, command: str, target: str):
    called = Mock()
    monkeypatch.setattr(target, called)
    assert cli_main.main([command, "--help"]) == 0
    called.assert_called_once_with()


def test_cli_help_subcommand_dispatches(monkeypatch):
    called = Mock()
    monkeypatch.setattr("autoppia_iwa.entrypoints.benchmark.run.main", called)
    assert cli_main.main(["help", "benchmark"]) == 0
    called.assert_called_once_with()
