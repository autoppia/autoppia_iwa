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


def test_main_exits_non_zero_for_invalid_project(monkeypatch, capsys):
    monkeypatch.setattr(check_run, "_parse_args", lambda: type("Args", (), {"project": "missing"})())

    with pytest.raises(SystemExit) as exc:
        check_run.main()

    assert exc.value.code == 1
    assert "Unknown project: missing" in capsys.readouterr().out
