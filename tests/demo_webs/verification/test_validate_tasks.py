import json

import pytest

from autoppia_iwa.src.demo_webs.web_verification import validate_tasks


class _FakeLLM:
    def __init__(self, response):
        self.response = response

    async def async_predict(self, **kwargs):
        return self.response


@pytest.mark.asyncio
async def test_is_task_consistent_rejects_missing_constraint_value():
    valid, reason = await validate_tasks.is_task_consistent(
        {
            "prompt": "Find a movie by title Inception",
            "constraints": [{"field": "director", "operator": "equals", "value": "Nolan"}],
        },
        _FakeLLM('{"valid": true, "reason": "ok"}'),
    )

    assert valid is False
    assert "director" in reason


@pytest.mark.asyncio
async def test_run_validation_writes_summary_file(tmp_path, monkeypatch):
    input_file = tmp_path / "misgenerated_tasks_autocinema.json"
    input_file.write_text(
        json.dumps(
            {
                "use_cases": {
                    "VIEW_MOVIE": {
                        "flagged_tasks": [
                            {
                                "task_id": "task-1",
                                "prompt": "Find the movie Inception",
                                "constraints": [{"field": "title", "operator": "equals", "value": "Inception"}],
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_tasks, "VERIFICATION_DIR", tmp_path)
    monkeypatch.setattr(validate_tasks, "validate_operator_with_llm", lambda *args, **kwargs: __import__("asyncio").sleep(0, result=(True, "ok")))

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(validate_tasks.asyncio, "to_thread", fake_to_thread)

    await validate_tasks.run_validation("autocinema", _FakeLLM('{"valid": true, "reason": "ok"}'))

    output_file = tmp_path / "autocinema_tasksconsistence.json"
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["summary"] == {"total": 1, "correct": 1, "incorrect": 0}


@pytest.mark.asyncio
async def test_main_bootstraps_and_runs_all_projects(monkeypatch):
    calls = []
    fake_llm = object()

    monkeypatch.setattr(validate_tasks, "PROJECT_IDS", ["autocinema", "autobooks"])
    monkeypatch.setattr(validate_tasks, "AppBootstrap", lambda: calls.append("bootstrap"))
    monkeypatch.setattr(validate_tasks, "DIContainer", type("FakeDI", (), {"llm_service": staticmethod(lambda: fake_llm)}))

    async def fake_run_validation(project_id, llm_service):
        calls.append((project_id, llm_service))

    monkeypatch.setattr(validate_tasks, "run_validation", fake_run_validation)

    await validate_tasks.main()

    assert calls == [
        "bootstrap",
        ("autocinema", fake_llm),
        ("autobooks", fake_llm),
    ]
