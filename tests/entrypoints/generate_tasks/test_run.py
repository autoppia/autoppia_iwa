from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.entrypoints.generate_tasks import run as generate_tasks_run


class _Task:
    def __init__(self, task_id: str):
        self.task_id = task_id

    def serialize(self):
        return {"id": self.task_id}


@pytest.mark.asyncio
async def test_run_generates_and_saves_tasks(monkeypatch, tmp_path, capsys):
    fake_project = type("Project", (), {"id": "autobooks", "name": "Autobooks"})()

    monkeypatch.setattr("autoppia_iwa.src.bootstrap.AppBootstrap", lambda: None)
    monkeypatch.setattr("autoppia_iwa.src.demo_webs.config.demo_web_projects", [fake_project])
    monkeypatch.setattr(
        "autoppia_iwa.src.evaluation.benchmark.utils.task_generation.get_projects_by_ids",
        lambda _all, ids: [fake_project] if ids == ["autobooks"] else [],
    )

    class FakePipeline:
        def __init__(self, web_project, config):
            self.web_project = web_project
            self.config = config

        async def generate(self):
            return [_Task("t1"), _Task("t2")]

    monkeypatch.setattr("autoppia_iwa.src.data_generation.tasks.pipeline.TaskGenerationPipeline", FakePipeline)

    output = tmp_path / "tasks.json"
    result = await generate_tasks_run.run(project_ids=["autobooks"], output=str(output), prompts_per_use_case=1)

    assert "autobooks" in result
    saved = json.loads(output.read_text())
    assert saved["autobooks"]["tasks"] == [{"id": "t1"}, {"id": "t2"}]
    assert "Saved to" in capsys.readouterr().out


def test_main_exits_zero_on_success(monkeypatch):
    args = type(
        "Args",
        (),
        {
            "project": ["autobooks"],
            "use_case": None,
            "prompts_per_use_case": 1,
            "output": "tasks.json",
            "dynamic": False,
        },
    )()
    monkeypatch.setattr(generate_tasks_run, "_parse_args", lambda: args)
    monkeypatch.setattr(generate_tasks_run, "run", AsyncMock(return_value={"ok": True}))

    with pytest.raises(SystemExit) as exc:
        generate_tasks_run.main()

    assert exc.value.code == 0


def test_main_exits_non_zero_on_value_error(monkeypatch, capsys):
    args = type(
        "Args",
        (),
        {
            "project": ["missing"],
            "use_case": None,
            "prompts_per_use_case": 1,
            "output": "tasks.json",
            "dynamic": False,
        },
    )()
    monkeypatch.setattr(generate_tasks_run, "_parse_args", lambda: args)

    async def _fail(**_kwargs):
        raise ValueError("bad project")

    monkeypatch.setattr(generate_tasks_run, "run", _fail)

    with pytest.raises(SystemExit) as exc:
        generate_tasks_run.main()

    assert exc.value.code == 1
    assert "bad project" in capsys.readouterr().out
