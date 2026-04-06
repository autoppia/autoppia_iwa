import pytest

from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.web_verification.config import WebVerificationConfig
from autoppia_iwa.src.demo_webs.web_verification.pipeline import WebVerificationPipeline, _TrajectoryOnlyLlmStub


class _DummyGenerator:
    def __init__(self, *args, **kwargs):
        pass


class _DummyIWAPClient:
    def __init__(self, *args, **kwargs):
        pass

    async def get_tasks_with_solutions(self, **kwargs):
        return {"success": False, "error": "mock"}


class _DummyLLMReviewer:
    def __init__(self, *args, **kwargs):
        pass

    async def review_task_and_constraints(self, task):
        return {"valid": True, "task_id": getattr(task, "id", None), "retry_count": 0}


class _DummyDynamicVerifier:
    def __init__(self, *args, **kwargs):
        pass

    async def verify_dataset_diversity_with_seeds(self, seed_values):
        return {
            "skipped": False,
            "passed": True,
            "all_different": True,
            "seeds_tested": seed_values,
            "comparison_results": [],
            "summary": "",
            "loaded_count": len(seed_values),
            "expected_count": len(seed_values),
        }

    async def verify_trajectory(self, *args, **kwargs):
        return {
            "all_passed": True,
            "passed_count": 1,
            "total_count": 1,
            "seeds_tested": [1],
            "results": {
                1: {
                    "evaluation": {
                        "final_score": 1.0,
                        "success": True,
                        "tests_passed": 1,
                        "total_tests": 1,
                    },
                },
            },
            "summary": "trajectory ok",
            "needs_review": False,
            "trajectory_name": "ENTER_LOCATION",
        }


def _build_project(use_cases):
    return WebProject(
        id="autocinema",
        name="Autocinema",
        backend_url="http://localhost:8001",
        frontend_url="http://localhost:8000",
        urls=["http://localhost:8000"],
        use_cases=use_cases,
    )


def test_pipeline_trajectories_only_uses_stub_llm_not_di_container(monkeypatch):
    def boom():
        raise AssertionError("DIContainer.llm_service() must not run in trajectories-only mode")

    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DIContainer.llm_service",
        boom,
    )
    use_case = UseCase(
        name="X",
        description="",
        event=object,
        event_source_code="",
        examples=[],
    )
    project = _build_project([use_case])
    cfg = WebVerificationConfig(
        evaluate_trajectories_only=True,
        llm_review_enabled=False,
        iwap_enabled=False,
        dynamic_verification_enabled=True,
        seed_values=[1],
    )
    pipeline = WebVerificationPipeline(project, cfg)
    assert isinstance(pipeline.llm_service, _TrajectoryOnlyLlmStub)


@pytest.mark.asyncio
async def test_pipeline_trajectories_only_skips_v2_dataset_diversity(monkeypatch, tmp_path):
    v2_calls: list[list[int]] = []

    class _TrackV2(_DummyDynamicVerifier):
        async def verify_dataset_diversity_with_seeds(self, seed_values):
            v2_calls.append(list(seed_values))
            return {"passed": True, "skipped": False}

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
        _TrackV2,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DIContainer.llm_service",
        lambda: object(),
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.get_trajectory_map",
        lambda _pid: None,
    )

    use_case = UseCase(
        name="BOOK_TICKET",
        description="",
        event=object,
        event_source_code="",
        examples=[],
    )
    cfg = WebVerificationConfig(
        evaluate_trajectories_only=True,
        llm_review_enabled=False,
        iwap_enabled=False,
        dynamic_verification_enabled=True,
        seed_values=[1, 50, 100],
        output_dir=str(tmp_path),
    )
    pipeline = WebVerificationPipeline(_build_project([use_case]), cfg)

    async def fake_save():
        return None

    monkeypatch.setattr(pipeline, "_save_results", fake_save)

    result = await pipeline.run()

    assert v2_calls == []
    dd = result["use_cases"]["BOOK_TICKET"]["dataset_diversity_verification"]
    assert dd.get("skipped") is True
    assert "trajectories-only" in (dd.get("reason") or "").lower()


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


@pytest.mark.asyncio
async def test_pipeline_use_case_filter_only_processes_matching(monkeypatch):
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
    uc_a = UseCase(
        name="A",
        description="",
        event=object,
        event_source_code="",
        examples=[],
    )
    uc_b = UseCase(
        name="B",
        description="",
        event=object,
        event_source_code="",
        examples=[],
    )
    cfg = WebVerificationConfig(use_case_filter=["B"])
    pipeline = WebVerificationPipeline(_build_project([uc_a, uc_b]), cfg)
    processed: list[str] = []

    async def fake_process(u):
        processed.append(u.name)
        return {"ok": True}

    monkeypatch.setattr(pipeline, "_process_use_case", fake_process)

    async def fake_save():
        return None

    monkeypatch.setattr(pipeline, "_save_results", fake_save)

    result = await pipeline.run()

    assert processed == ["B"]
    assert set(result["use_cases"].keys()) == {"B"}


@pytest.mark.asyncio
async def test_pipeline_evaluate_trajectories_calls_verify_trajectory(monkeypatch):
    from autoppia_iwa.src.data_generation.tasks.classes import Task

    traj_calls: list[int] = []

    class _Gen:
        def __init__(self, *args, **kwargs):
            pass

        async def generate_tasks_for_use_case(self, use_case, number_of_prompts=1, dynamic=False, base_url=None):
            return [
                Task(
                    url="http://localhost:8012/?seed=1",
                    prompt="prompt",
                    use_case=use_case,
                    web_project_id="autodrive",
                )
            ]

    class _TrackingDynamicVerifier(_DummyDynamicVerifier):
        async def verify_trajectory(self, *args, **kwargs):
            traj_calls.append(1)
            return await _DummyDynamicVerifier.verify_trajectory(self, *args, **kwargs)

    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.SimpleTaskGenerator",
        _Gen,
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
        _TrackingDynamicVerifier,
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.web_verification.pipeline.DIContainer.llm_service",
        lambda: object(),
    )

    use_case = UseCase(
        name="ENTER_LOCATION",
        description="Enter pickup",
        event=object,
        event_source_code="class Event: ...",
        examples=[],
    )
    project = WebProject(
        id="autodrive",
        name="Autodrive",
        backend_url="http://localhost:8001",
        frontend_url="http://localhost:8012",
        urls=["http://localhost:8012"],
        use_cases=[use_case],
    )
    cfg = WebVerificationConfig(
        evaluate_trajectories=True,
        dynamic_enabled=True,
        dynamic_verification_enabled=True,
        llm_review_enabled=True,
        iwap_enabled=True,
        seed_values=[1],
        tasks_per_use_case=1,
    )
    pipeline = WebVerificationPipeline(project, cfg)

    async def no_save():
        return None

    monkeypatch.setattr(pipeline, "_save_results", no_save)

    result = await pipeline.run()

    assert traj_calls == [1]
    tv = result["use_cases"]["ENTER_LOCATION"].get("trajectory_verification")
    assert tv is not None
    assert tv.get("all_passed") is True
