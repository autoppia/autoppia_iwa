from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.entrypoints.check import run as check_run


class _Project:
    def __init__(self, project_id: str, name: str):
        self.id = project_id
        self.name = name
        self.backend_url = f"http://backend/{project_id}"
        self.frontend_url = f"http://frontend/{project_id}"


@pytest.mark.asyncio
async def test_run_returns_true_when_all_checks_pass(monkeypatch, capsys):
    monkeypatch.setattr("autoppia_iwa.config.env.init_env", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [_Project("p1", "Project 1")])
    monkeypatch.setattr(check_run, "_check_health", AsyncMock(return_value={"database_pool_operational": True, "version": "1.2.3"}))
    monkeypatch.setattr(check_run, "_check_frontend", AsyncMock(return_value=True))

    result = await check_run.run()

    assert result is True
    out = capsys.readouterr().out
    assert "1/1 healthy" in out


@pytest.mark.asyncio
async def test_run_invalid_project_raises(monkeypatch):
    monkeypatch.setattr("autoppia_iwa.config.env.init_env", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [_Project("p1", "Project 1")])

    with pytest.raises(ValueError, match="Unknown project: missing"):
        await check_run.run(project_id="missing")


@pytest.mark.asyncio
async def test_run_returns_false_when_backend_or_frontend_fails(monkeypatch, capsys):
    monkeypatch.setattr("autoppia_iwa.config.env.init_env", lambda: None)
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.config.demo_web_projects",
        [_Project("p1", "Project 1"), _Project("p2", "Project 2")],
    )
    monkeypatch.setattr(check_run, "_check_health", AsyncMock(side_effect=[None, {"database_pool_operational": False, "version": "2.0"}]))
    monkeypatch.setattr(check_run, "_check_frontend", AsyncMock(side_effect=[False, True]))

    result = await check_run.run()

    assert result is False
    out = capsys.readouterr().out
    assert "0/2 healthy" in out
    assert "[x]" in out


def test_parse_args_reads_project_flag(monkeypatch):
    monkeypatch.setattr("sys.argv", ["iwa", "--project", "autocinema"])
    args = check_run._parse_args()
    assert args.project == "autocinema"


def test_main_exits_zero_when_run_succeeds(monkeypatch):
    monkeypatch.setattr(check_run, "_parse_args", lambda: type("Args", (), {"project": None})())

    def _run(coro):
        coro.close()
        return True

    monkeypatch.setattr(check_run.asyncio, "run", _run)

    with pytest.raises(SystemExit) as exc:
        check_run.main()

    assert exc.value.code == 0


def test_main_exits_one_when_run_returns_false(monkeypatch):
    monkeypatch.setattr(check_run, "_parse_args", lambda: type("Args", (), {"project": None})())

    def _run(coro):
        coro.close()
        return False

    monkeypatch.setattr(check_run.asyncio, "run", _run)

    with pytest.raises(SystemExit) as exc:
        check_run.main()

    assert exc.value.code == 1


def test_main_exits_non_zero_for_invalid_project(monkeypatch, capsys):
    monkeypatch.setattr(check_run, "_parse_args", lambda: type("Args", (), {"project": "missing"})())

    with pytest.raises(SystemExit) as exc:
        check_run.main()

    assert exc.value.code == 1
    assert "Unknown project: missing" in capsys.readouterr().out
