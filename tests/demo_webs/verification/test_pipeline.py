import pytest

from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.web_verification.config import WebVerificationConfig
from autoppia_iwa.src.demo_webs.web_verification.pipeline import WebVerificationPipeline


class _DummyGenerator:
    def __init__(self, *args, **kwargs):
        pass


class _DummyIWAPClient:
    def __init__(self, *args, **kwargs):
        pass


class _DummyLLMReviewer:
    def __init__(self, *args, **kwargs):
        pass


class _DummyDynamicVerifier:
    def __init__(self, *args, **kwargs):
        pass


def _build_project(use_cases):
    return WebProject(
        id="autocinema",
        name="Autocinema",
        backend_url="http://localhost:8001",
        frontend_url="http://localhost:8000",
        urls=["http://localhost:8000"],
        use_cases=use_cases,
    )


@pytest.mark.asyncio
async def test_pipeline_run_returns_empty_results_without_use_cases(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.SimpleTaskGenerator",
        _DummyGenerator,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.IWAPClient",
        _DummyIWAPClient,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.LLMReviewer",
        _DummyLLMReviewer,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DynamicVerifier",
        _DummyDynamicVerifier,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DIContainer.llm_service",
        lambda: object(),
    )
    project = _build_project([])
    pipeline = WebVerificationPipeline(project, WebVerificationConfig())

    result = await pipeline.run()

    assert result["project_id"] == "autocinema"
    assert result["use_cases"] == {}


@pytest.mark.asyncio
async def test_pipeline_run_processes_use_cases_and_saves_results(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.SimpleTaskGenerator",
        _DummyGenerator,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.IWAPClient",
        _DummyIWAPClient,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.LLMReviewer",
        _DummyLLMReviewer,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DynamicVerifier",
        _DummyDynamicVerifier,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DIContainer.llm_service",
        lambda: object(),
    )
    use_case = UseCase(
        name="BOOK_TICKET",
        description="Book a ticket",
        event=object,
        event_source_code="class Event: ...",
        examples=[],
    )
    pipeline = WebVerificationPipeline(_build_project([use_case]), WebVerificationConfig())
    saved = {"called": False}

    async def fake_process(u):
        return {"processed": u.name}

    async def fake_save():
        saved["called"] = True

    monkeypatch.setattr(pipeline, "_process_use_case", fake_process)
    monkeypatch.setattr(pipeline, "_save_results", fake_save)

    result = await pipeline.run()

    assert result["use_cases"]["BOOK_TICKET"] == {"processed": "BOOK_TICKET"}
    assert saved["called"] is True
