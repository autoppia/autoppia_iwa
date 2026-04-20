from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.data_generation.data_extraction.generator import DataExtractionTaskGenerator
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.base_events import Event
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator


class _DummyEvent(Event):
    event_name: str = "DUMMY_EVENT"

    class ValidationCriteria(Event.ValidationCriteria):
        value: str | None = None


def _make_use_case(name: str = "UC", *, constraints_generator=None, replace_func=None) -> UseCase:
    return UseCase(
        name=name,
        description=f"Use case {name}",
        event=_DummyEvent,
        event_source_code="class DummyEvent: pass",
        examples=[{"prompt": "Prompt", "prompt_for_task_generation": "Prompt for generation"}],
        constraints=[{"field": "value", "operator": ComparisonOperator.EQUALS, "value": "ok"}],
        constraints_generator=constraints_generator,
        replace_func=replace_func,
    )


def _make_project(use_cases: list[UseCase] | None = None) -> WebProject:
    return WebProject(
        id="dummy_project",
        name="Dummy project",
        backend_url="https://example.com/api/",
        frontend_url="https://example.com/",
        use_cases=use_cases or [],
    )


@pytest.mark.asyncio
async def test_generate_returns_dedicated_de_use_cases_when_available():
    generator = DataExtractionTaskGenerator(web_project=_make_project(), llm_service=None)
    expected_task = Task(url="https://example.com/?seed=1", prompt="Who is the director?")

    with (
        patch(
            "autoppia_iwa.src.data_generation.data_extraction.generator.generate_tasks_from_project_data_extraction_use_cases",
            AsyncMock(return_value=[expected_task]),
        ) as dedicated_mock,
        patch.object(generator, "generate_tasks_for_use_case", AsyncMock()) as generate_for_use_case_mock,
    ):
        result = await generator.generate(prompts_per_use_case=2, dynamic=True)

    assert result == [expected_task]
    dedicated_mock.assert_awaited_once()
    generate_for_use_case_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_returns_empty_when_data_extraction_use_cases_filter_has_no_match():
    generator = DataExtractionTaskGenerator(
        web_project=_make_project(use_cases=[_make_use_case(name="ONLY_UC")]),
        llm_service=None,
    )

    with patch(
        "autoppia_iwa.src.data_generation.data_extraction.generator.generate_tasks_from_project_data_extraction_use_cases",
        AsyncMock(return_value=None),
    ):
        result = await generator.generate(
            prompts_per_use_case=1,
            data_extraction_use_cases=["NON_EXISTENT"],
        )

    assert result == []


@pytest.mark.asyncio
async def test_generate_returns_empty_when_use_cases_filter_has_no_match():
    generator = DataExtractionTaskGenerator(
        web_project=_make_project(use_cases=[_make_use_case(name="ONLY_UC")]),
        llm_service=None,
    )

    with patch(
        "autoppia_iwa.src.data_generation.data_extraction.generator.generate_tasks_from_project_data_extraction_use_cases",
        AsyncMock(return_value=None),
    ):
        result = await generator.generate(
            prompts_per_use_case=1,
            use_cases=["NON_EXISTENT"],
        )

    assert result == []


@pytest.mark.asyncio
async def test_generate_continues_when_one_use_case_generation_fails():
    use_case_a = _make_use_case(name="A")
    use_case_b = _make_use_case(name="B")
    generator = DataExtractionTaskGenerator(web_project=_make_project(use_cases=[use_case_a, use_case_b]), llm_service=None)
    ok_task = Task(url="https://example.com/?seed=1", prompt="ok")

    with (
        patch(
            "autoppia_iwa.src.data_generation.data_extraction.generator.generate_tasks_from_project_data_extraction_use_cases",
            AsyncMock(return_value=None),
        ),
        patch.object(
            generator,
            "generate_tasks_for_use_case",
            AsyncMock(side_effect=[[ok_task], RuntimeError("boom")]),
        ) as gen_mock,
    ):
        result = await generator.generate(prompts_per_use_case=1, dynamic=False)

    assert result == [ok_task]
    assert gen_mock.await_count == 2


@pytest.mark.asyncio
async def test_generate_tasks_for_use_case_builds_tasks_and_passes_seed_and_dataset_to_replace_func():
    captured = {}

    def _constraints_generator(*, task_url=None, dataset=None, test_types=None):
        _ = task_url, dataset, test_types
        return {
            "constraints": [{"field": "balance", "operator": ComparisonOperator.EQUALS, "value": "42"}],
            "question_fields_and_values": {"rank": 5},
        }

    def _replace_func(text, *, seed_value=None, dataset=None, constraints=None):
        captured["seed_value"] = seed_value
        captured["dataset"] = dataset
        captured["constraints"] = constraints
        return f"{text} [seed={seed_value}] [rows={len(dataset)}]"

    use_case = _make_use_case(name="DE_UC", constraints_generator=_constraints_generator, replace_func=_replace_func)
    generator = DataExtractionTaskGenerator(web_project=_make_project(use_cases=[use_case]), llm_service=None)

    with (
        patch.object(generator, "_build_task_url_with_seed", return_value="https://example.com/app?seed=9"),
        patch.object(generator, "_resolve_seed", return_value=9),
        patch.object(generator, "_load_dataset", AsyncMock(return_value={"accounts": [{"rank": 5}]})),
        patch.object(generator, "_call_llm_with_retry", AsyncMock(return_value=["What is the balance?"])),
        patch("autoppia_iwa.src.data_generation.data_extraction.generator.random.shuffle") as shuffle_mock,
    ):
        tasks = await generator.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=True)

    assert len(tasks) == 1
    assert "What is the balance?" in tasks[0].prompt
    assert captured["seed_value"] == 9
    assert isinstance(captured["dataset"], list)
    assert captured["constraints"] is not None
    shuffle_mock.assert_called_once()


@pytest.mark.asyncio
async def test_generate_tasks_for_use_case_skips_iteration_when_constraints_generation_fails():
    def _failing_constraints_generator(*, task_url=None, dataset=None, test_types=None):
        _ = task_url, dataset, test_types
        raise RuntimeError("cannot build constraints")

    use_case = _make_use_case(name="DE_FAIL", constraints_generator=_failing_constraints_generator)
    generator = DataExtractionTaskGenerator(web_project=_make_project(use_cases=[use_case]), llm_service=None)

    with (
        patch.object(generator, "_build_task_url_with_seed", return_value="https://example.com/app?seed=3"),
        patch.object(generator, "_resolve_seed", return_value=3),
        patch.object(generator, "_load_dataset", AsyncMock(return_value={"rows": [{"id": 1}]})),
        patch.object(generator, "_call_llm_with_retry", AsyncMock(return_value=["never used"])) as llm_mock,
    ):
        tasks = await generator.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=True)

    assert tasks == []
    llm_mock.assert_not_called()


@pytest.mark.asyncio
async def test_generate_tasks_for_use_case_skips_when_no_prompt_built_or_llm_returns_empty():
    def _constraints_generator_none(*, task_url=None, dataset=None, test_types=None):
        _ = task_url, dataset, test_types
        return None

    use_case = _make_use_case(name="DE_EMPTY", constraints_generator=_constraints_generator_none)
    generator = DataExtractionTaskGenerator(web_project=_make_project(use_cases=[use_case]), llm_service=None)

    with (
        patch.object(generator, "_build_task_url_with_seed", return_value="https://example.com/app"),
        patch.object(generator, "_resolve_seed", return_value=1),
        patch.object(generator, "_load_dataset", AsyncMock(return_value={})),
        patch.object(generator, "_call_llm_with_retry", AsyncMock(return_value=["unused"])) as llm_mock,
    ):
        tasks = await generator.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)

    assert tasks == []
    llm_mock.assert_not_called()

    def _constraints_generator_ok(*, task_url=None, dataset=None, test_types=None):
        _ = task_url, dataset, test_types
        return [{"field": "f", "operator": ComparisonOperator.EQUALS, "value": "v"}]

    use_case_ok = _make_use_case(name="DE_OK", constraints_generator=_constraints_generator_ok)
    with (
        patch.object(generator, "_call_llm_with_retry", AsyncMock(return_value=[])),
        patch.object(generator, "_load_dataset", AsyncMock(return_value={})),
    ):
        tasks_no_llm = await generator.generate_tasks_for_use_case(use_case_ok, number_of_prompts=1, dynamic=False)
    assert tasks_no_llm == []


@pytest.mark.asyncio
async def test_generate_tasks_for_use_case_handles_task_assembly_exception():
    def _constraints_generator(*, task_url=None, dataset=None, test_types=None):
        _ = task_url, dataset, test_types
        return [{"field": "f", "operator": ComparisonOperator.EQUALS, "value": "v"}]

    def _replace_raises(_text, **_kwargs):
        raise RuntimeError("replacement failed")

    use_case = _make_use_case(name="DE_ASSEMBLY_FAIL", constraints_generator=_constraints_generator, replace_func=_replace_raises)
    generator = DataExtractionTaskGenerator(web_project=_make_project(use_cases=[use_case]), llm_service=None)

    with (
        patch.object(generator, "_call_llm_with_retry", AsyncMock(return_value=["Prompt to replace"])),
        patch.object(generator, "_load_dataset", AsyncMock(return_value={})),
    ):
        tasks = await generator.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)

    assert tasks == []
