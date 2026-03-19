from __future__ import annotations

import pytest

from autoppia_iwa.entrypoints.web_verification import run as verify_run


@pytest.mark.asyncio
async def test_run_builds_pipeline(monkeypatch, capsys):
    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()
    captured = {}

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.utils.task_generation.get_projects_by_ids",
        lambda _all, ids: [fake_project] if ids == ["autobooks"] else [],
    )

    class FakeConfig:
        def __init__(self, **kwargs):
            captured["config_kwargs"] = kwargs

    class FakePipeline:
        def __init__(self, web_project, config):
            captured["project"] = web_project
            captured["config"] = config

        async def run(self):
            return {"ok": True}

        def get_summary(self):
            return "summary-text"

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.WebVerificationConfig", FakeConfig)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.WebVerificationPipeline", FakePipeline)

    result = await verify_run.run(project_id="autobooks", seeds="1,2,3", no_llm_review=True, verbose=True)

    assert result == {"ok": True}
    assert captured["project"] is fake_project
    assert captured["config_kwargs"]["seed_values"] == [1, 2, 3]
    assert captured["config_kwargs"]["llm_review_enabled"] is False
    assert "summary-text" in capsys.readouterr().out


def test_main_exits_non_zero_on_invalid_project(monkeypatch, capsys):
    args = type(
        "Args",
        (),
        {
            "project": "missing",
            "output": "./out",
            "tasks_per_use_case": 1,
            "seeds": "1",
            "no_llm_review": False,
            "verbose": False,
        },
    )()
    monkeypatch.setattr(verify_run, "_parse_args", lambda: args)
    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [])

    with pytest.raises(SystemExit) as exc:
        verify_run.main()

    assert exc.value.code == 1
    assert "Project IDs not found" in capsys.readouterr().out
