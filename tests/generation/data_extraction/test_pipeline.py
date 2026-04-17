from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.data_extraction.pipeline import DataExtractionTaskGenerationPipeline
from autoppia_iwa.src.data_generation.tasks.classes import Task, TaskGenerationConfig
from autoppia_iwa.src.demo_webs.classes import WebProject


def _make_project() -> WebProject:
    return WebProject(
        id="dummy_project",
        name="Dummy project",
        backend_url="https://example.com/api/",
        frontend_url="https://example.com/",
        use_cases=[],
    )


@pytest.mark.asyncio
async def test_data_extraction_pipeline_generate_success():
    config = TaskGenerationConfig(
        prompts_per_use_case=2,
        use_cases=["UC_A"],
        dynamic=True,
        test_types="data_extraction_only",
        data_extraction_use_cases=["UC_DE"],
    )
    pipeline = DataExtractionTaskGenerationPipeline(web_project=_make_project(), config=config, llm_service=MagicMock())

    generated = [Task(url="https://example.com/?seed=1", prompt="Question?")]
    enriched = [Task(url="https://example.com/?seed=1", prompt="Question?", tests=[])]

    with (
        patch.object(pipeline.task_generator, "generate", AsyncMock(return_value=generated)) as generate_mock,
        patch.object(pipeline.global_test_pipeline, "add_tests_to_tasks", return_value=enriched) as add_tests_mock,
    ):
        result = await pipeline.generate()

    assert result == enriched
    generate_mock.assert_awaited_once_with(
        prompts_per_use_case=2,
        use_cases=["UC_A"],
        dynamic=True,
        test_types="data_extraction_only",
        data_extraction_use_cases=["UC_DE"],
    )
    add_tests_mock.assert_called_once_with(
        generated,
        test_types="data_extraction_only",
        data_extraction_use_cases=["UC_DE"],
    )


@pytest.mark.asyncio
async def test_data_extraction_pipeline_generate_returns_empty_on_exception():
    config = TaskGenerationConfig(prompts_per_use_case=1, dynamic=False, test_types="data_extraction_only")
    pipeline = DataExtractionTaskGenerationPipeline(web_project=_make_project(), config=config, llm_service=MagicMock())

    with patch.object(pipeline.task_generator, "generate", AsyncMock(side_effect=RuntimeError("boom"))):
        result = await pipeline.generate()

    assert result == []
