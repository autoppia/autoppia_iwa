from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.data_generation.data_extraction.flow import (
    build_data_extraction_generation_prompt,
    generate_tasks_from_project_data_extraction_use_cases,
)
from autoppia_iwa.src.data_generation.tasks.classes import Task


def _make_use_case(
    *,
    constraints: list[dict] | None,
    qfav: dict | None = None,
    additional_prompt_info: str | None = None,
):
    return SimpleNamespace(
        name="UC_DE",
        description="Describe DE use case",
        additional_prompt_info=additional_prompt_info,
        constraints=constraints,
        question_fields_and_values=qfav,
    )


def test_build_prompt_returns_none_without_constraints():
    uc = _make_use_case(constraints=None)
    assert build_data_extraction_generation_prompt(uc) is None


def test_build_prompt_with_question_fields_uses_expected_template():
    enum_like = SimpleNamespace(value="balance")
    uc = _make_use_case(
        constraints=[{"field": enum_like}],
        qfav={"rank": 5, "network": "mainnet"},
        additional_prompt_info="Extra info",
    )

    prompt = build_data_extraction_generation_prompt(uc)

    assert prompt is not None
    assert "rank = 5" in prompt
    assert "network = mainnet" in prompt
    assert "balance" in prompt
    assert "Extra info" in prompt


def test_build_prompt_with_question_fields_falls_back_when_verify_field_missing():
    uc = _make_use_case(
        constraints=[{"value": "x"}],
        qfav={"id": 1},
    )

    prompt = build_data_extraction_generation_prompt(uc)

    assert prompt is not None
    assert "the requested field" in prompt


def test_build_prompt_without_question_fields_uses_verify_field_only_template():
    uc = _make_use_case(
        constraints=[{"field": "selectedDate"}],
        qfav={},
        additional_prompt_info=None,
    )

    prompt = build_data_extraction_generation_prompt(uc)

    assert prompt is not None
    assert "selectedDate" in prompt
    assert "There is no entity identifier" in prompt


@pytest.mark.asyncio
async def test_generate_from_project_de_use_cases_returns_none_when_project_module_missing():
    result = await generate_tasks_from_project_data_extraction_use_cases(
        web_project=SimpleNamespace(id="dummy"),
        prompts_per_use_case=1,
        dynamic=True,
        data_extraction_use_cases=None,
        get_project_module_name=lambda: None,
        build_task_url_with_seed=lambda _dynamic: "https://example.com/?seed=1",
    )
    assert result is None


@pytest.mark.asyncio
async def test_generate_from_project_de_use_cases_returns_none_on_import_error():
    with patch(
        "autoppia_iwa.src.data_generation.data_extraction.flow.importlib.import_module",
        side_effect=ImportError("missing module"),
    ):
        result = await generate_tasks_from_project_data_extraction_use_cases(
            web_project=SimpleNamespace(id="dummy"),
            prompts_per_use_case=1,
            dynamic=True,
            data_extraction_use_cases=None,
            get_project_module_name=lambda: "p01_autocinema",
            build_task_url_with_seed=lambda _dynamic: "https://example.com/?seed=1",
        )
    assert result is None


@pytest.mark.asyncio
async def test_generate_from_project_de_use_cases_returns_none_when_generate_function_not_callable():
    module = SimpleNamespace(generate_de_tasks="not callable")
    with patch(
        "autoppia_iwa.src.data_generation.data_extraction.flow.importlib.import_module",
        return_value=module,
    ):
        result = await generate_tasks_from_project_data_extraction_use_cases(
            web_project=SimpleNamespace(id="dummy"),
            prompts_per_use_case=1,
            dynamic=True,
            data_extraction_use_cases=None,
            get_project_module_name=lambda: "p01_autocinema",
            build_task_url_with_seed=lambda _dynamic: "https://example.com/?seed=1",
        )
    assert result is None


@pytest.mark.asyncio
async def test_generate_from_project_de_use_cases_supports_sync_and_async_generation_and_filters_tasks():
    captured_selected_use_cases: list[set[str] | None] = []

    async def _async_generate(*, seed, task_url, selected_use_cases):
        captured_selected_use_cases.append(selected_use_cases)
        assert seed == 77
        assert task_url.startswith("https://example.com/")
        return [Task(url=task_url, prompt="A"), "ignore-me"]

    module = SimpleNamespace(generate_de_tasks=_async_generate)
    urls = iter(["https://example.com/?seed=7", "https://example.com/?seed=8"])

    with (
        patch(
            "autoppia_iwa.src.data_generation.data_extraction.flow.get_seed_from_url",
            return_value=77,
        ),
        patch(
            "autoppia_iwa.src.data_generation.data_extraction.flow.importlib.import_module",
            return_value=module,
        ),
    ):
        tasks = await generate_tasks_from_project_data_extraction_use_cases(
            web_project=SimpleNamespace(id="dummy"),
            prompts_per_use_case=2,
            dynamic=True,
            data_extraction_use_cases=[" find_balance ", "FIND_BALANCE"],
            get_project_module_name=lambda: "p01_autocinema",
            build_task_url_with_seed=lambda _dynamic: next(urls),
        )

    assert isinstance(tasks, list)
    assert len(tasks) == 2
    assert all(isinstance(task, Task) for task in tasks)
    assert captured_selected_use_cases == [{"FIND_BALANCE"}, {"FIND_BALANCE"}]


@pytest.mark.asyncio
async def test_generate_from_project_de_use_cases_handles_non_list_generated_output():
    module = SimpleNamespace(generate_de_tasks=AsyncMock(return_value={"not": "a-list"}))

    with patch(
        "autoppia_iwa.src.data_generation.data_extraction.flow.importlib.import_module",
        return_value=module,
    ):
        tasks = await generate_tasks_from_project_data_extraction_use_cases(
            web_project=SimpleNamespace(id="dummy"),
            prompts_per_use_case=0,
            dynamic=False,
            data_extraction_use_cases=None,
            get_project_module_name=lambda: "p01_autocinema",
            build_task_url_with_seed=lambda _dynamic: "https://example.com/",
        )

    assert tasks == []
