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

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.config.WebVerificationConfig", FakeConfig)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.pipeline.WebVerificationPipeline", FakePipeline)

    result = await verify_run.run(project_id="autobooks", seeds="1,2,3", no_llm_review=True, verbose=True)

    assert result == {"ok": True}
    assert captured["project"] is fake_project
    assert captured["config_kwargs"]["seed_values"] == [1, 2, 3]
    assert captured["config_kwargs"]["llm_review_enabled"] is False
    assert captured["config_kwargs"]["evaluate_trajectories"] is False
    assert captured["config_kwargs"]["evaluate_trajectories_only"] is False
    assert captured["config_kwargs"].get("use_case_filter") is None
    assert "summary-text" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_run_passes_evaluate_trajectories_to_config(monkeypatch, capsys):
    fake_project = type("Project", (), {"id": "autodrive", "name": "Autodrive"})()
    captured = {}

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.utils.task_generation.get_projects_by_ids",
        lambda _all, ids: [fake_project] if ids == ["autodrive"] else [],
    )

    class FakeConfig:
        def __init__(self, **kwargs):
            captured["config_kwargs"] = kwargs

    class FakePipeline:
        def __init__(self, web_project=None, config=None):
            captured["project"] = web_project
            captured["config"] = config

        async def run(self):
            return {"ok": True}

        def get_summary(self):
            return ""

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.config.WebVerificationConfig", FakeConfig)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.pipeline.WebVerificationPipeline", FakePipeline)

    await verify_run.run(project_id="autodrive", evaluate_trajectories=True)

    assert captured["config_kwargs"]["evaluate_trajectories"] is True


@pytest.mark.asyncio
async def test_run_trajectories_only_sets_config_flags(monkeypatch, capsys):
    fake_project = type("Project", (), {"id": "autohealth", "name": "Autohealth"})()
    captured = {}

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.utils.task_generation.get_projects_by_ids",
        lambda _all, ids: [fake_project] if ids == ["autohealth"] else [],
    )

    class FakeConfig:
        def __init__(self, **kwargs):
            captured["config_kwargs"] = kwargs

    class FakePipeline:
        def __init__(self, *a, **k):
            pass

        async def run(self):
            return {}

        def get_summary(self):
            return ""

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.config.WebVerificationConfig", FakeConfig)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.pipeline.WebVerificationPipeline", FakePipeline)

    await verify_run.run(project_id="autohealth", trajectories_only=True)

    assert captured["config_kwargs"]["evaluate_trajectories_only"] is True
    assert captured["config_kwargs"]["evaluate_trajectories"] is True
    assert captured["config_kwargs"]["iwap_enabled"] is False
    assert captured["config_kwargs"]["llm_review_enabled"] is False


@pytest.mark.asyncio
async def test_run_passes_use_case_filter_to_config(monkeypatch, capsys):
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
        def __init__(self, *a, **k):
            pass

        async def run(self):
            return {}

        def get_summary(self):
            return ""

    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.config.WebVerificationConfig", FakeConfig)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.web_verification.pipeline.WebVerificationPipeline", FakePipeline)

    await verify_run.run(project_id="autobooks", use_cases=["LOGIN", "SEARCH"])

    assert captured["config_kwargs"]["use_case_filter"] == ["LOGIN", "SEARCH"]


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
            "evaluate_trajectories": False,
            "trajectories_only": False,
            "use_case": None,
        },
    )()
    monkeypatch.setattr(verify_run, "_parse_args", lambda: args)
    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [])

    with pytest.raises(SystemExit) as exc:
        verify_run.main()

    assert exc.value.code == 1
    assert "Project IDs not found" in capsys.readouterr().out
