"""Tests for MultiStepTaskGenerator (multi-step/composited task generation)."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from autoppia_iwa.src.data_generation.tasks.classes import BrowserSpecification, Task
from autoppia_iwa.src.data_generation.tasks.multi_step.multi_step_task_generator import (
    MultiStepTaskGenerator,
)
from autoppia_iwa.src.demo_webs.classes import WebProject


def _make_web_project(
    project_id: str = "test-project",
    frontend_url: str = "https://example.com",
    urls: list[str] | None = None,
) -> WebProject:
    return WebProject(
        id=project_id,
        name="Test",
        backend_url="https://example.com/api/",
        frontend_url=frontend_url,
        use_cases=[],
        urls=urls or [],
    )


class TestParseLlmListOfStrings:
    """Tests for _parse_llm_list_of_strings."""

    def test_valid_json_list_of_strings(self):
        project = _make_web_project()
        llm = MagicMock()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=llm)
        result = gen._parse_llm_list_of_strings('["Step one", "Step two"]')
        assert result == ["Step one", "Step two"]

    def test_json_list_with_non_strings_converted_to_str(self):
        project = _make_web_project()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        result = gen._parse_llm_list_of_strings("[1, 2, true]")
        assert result == ["1", "2", "True"]

    def test_markdown_json_block_stripped_and_parsed(self):
        project = _make_web_project()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        text = '```json\n["A", "B"]\n```'
        result = gen._parse_llm_list_of_strings(text)
        assert result == ["A", "B"]

    def test_not_a_list_returns_empty(self):
        project = _make_web_project()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        result = gen._parse_llm_list_of_strings('{"key": "value"}')
        assert result == []

    def test_invalid_json_returns_empty(self):
        project = _make_web_project()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        result = gen._parse_llm_list_of_strings("not json at all")
        assert result == []


class TestAssembleCompositeTask:
    """Tests for _assemble_composite_task."""

    def test_returns_task_with_prompt_and_url(self):
        project = _make_web_project(project_id="proj-1", frontend_url="https://app.example.com/")
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        task = gen._assemble_composite_task(
            composite_prompt="First do X, then do Y.",
            url="https://app.example.com/",
        )
        assert isinstance(task, Task)
        assert task.prompt == "First do X, then do Y."
        assert task.url == "https://app.example.com/"
        assert task.web_project_id == "proj-1"
        assert task.use_case is None
        assert isinstance(task.specifications, BrowserSpecification)

    def test_uses_project_urls_first_when_set(self):
        project = _make_web_project(
            frontend_url="https://fallback.com",
            urls=["https://primary.com/page"],
        )
        gen = MultiStepTaskGenerator(web_project=project, llm_service=MagicMock())
        task = gen._assemble_composite_task(composite_prompt="Do it", url="https://primary.com/page")
        assert task.url == "https://primary.com/page"


class TestGenerateCompositedTasks:
    """Tests for generate_composited_tasks."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_base_tasks(self):
        project = _make_web_project()
        mock_llm = MagicMock()
        gen = MultiStepTaskGenerator(web_project=project, llm_service=mock_llm)
        gen.global_task_pipeline.generate = AsyncMock(return_value=[])
        result = await gen.generate_composited_tasks(
            prompts_per_use_case=2,
            number_of_composites=1,
            tasks_per_composite=2,
        )
        assert result == []
        gen.global_task_pipeline.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_composited_tasks_when_llm_returns_prompts(self):
        project = _make_web_project(frontend_url="https://demo.test/")
        base_task_1 = Task(url="https://demo.test/", prompt="Prompt A", web_project_id=project.id)
        base_task_2 = Task(url="https://demo.test/", prompt="Prompt B", web_project_id=project.id)
        composite_prompts = ["Do A then B in one flow."]
        mock_llm = MagicMock()
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(composite_prompts))
        gen = MultiStepTaskGenerator(web_project=project, llm_service=mock_llm)
        gen.global_task_pipeline.generate = AsyncMock(return_value=[base_task_1, base_task_2])
        result = await gen.generate_composited_tasks(
            prompts_per_use_case=2,
            number_of_composites=1,
            tasks_per_composite=2,
        )
        assert len(result) == 1
        assert result[0].prompt == "Do A then B in one flow."
        assert result[0].url == "https://demo.test/"
        assert result[0].web_project_id == project.id

    @pytest.mark.asyncio
    async def test_assembly_exception_logged_and_other_tasks_still_returned(self):
        project = _make_web_project()
        base_tasks = [
            Task(url="https://x.com", prompt="P1", web_project_id=project.id),
        ]
        mock_llm = MagicMock()
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(["Valid composite prompt"]))
        gen = MultiStepTaskGenerator(web_project=project, llm_service=mock_llm)
        gen.global_task_pipeline.generate = AsyncMock(return_value=base_tasks)
        result = await gen.generate_composited_tasks(
            prompts_per_use_case=1,
            number_of_composites=1,
            tasks_per_composite=1,
        )
        assert len(result) == 1
        assert result[0].prompt == "Valid composite prompt"
