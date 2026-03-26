"""Tests for SimpleTaskGenerator to improve coverage of simple_task_generator.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import (
    SimpleTaskGenerator,
)
from autoppia_iwa.src.demo_webs.base_events import Event
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator


def _make_project(project_id: str = "dummy", frontend_url: str = "https://example.com/", use_cases: list | None = None) -> WebProject:
    return WebProject(
        id=project_id,
        name="Test",
        backend_url="https://example.com/api/",
        frontend_url=frontend_url,
        use_cases=use_cases or [],
    )


class _DummyEvent(Event):
    event_name: str = "DUMMY_EVENT"

    class ValidationCriteria(Event.ValidationCriteria):
        value: str | None = None


def _make_use_case(name: str = "DUMMY_EVENT", replace_func=None, has_async_constraints: bool = False) -> UseCase:
    uc = UseCase(
        name=name,
        description="Test use case",
        event=_DummyEvent,
        event_source_code="class DummyEvent: pass",
        examples=[{"prompt": "Do X", "prompt_for_task_generation": "Do X"}],
        replace_func=replace_func,
    )
    uc.constraints = [{"field": "value", "operator": ComparisonOperator.EQUALS, "value": "ok"}]
    if has_async_constraints:

        async def _gen(*args, **kwargs):
            return "constraint info"

        uc.generate_constraints_async = _gen
    return uc


# -----------------------------------------------------------------------------
# _parse_llm_response and _clean_list_response
# -----------------------------------------------------------------------------


class TestParseLlmResponse:
    """Tests for _parse_llm_response."""

    def test_list_input_returns_strings(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._parse_llm_response(["a", "b"]) == ["a", "b"]
        assert gen._parse_llm_response([1, 2]) == ["1", "2"]

    def test_dict_with_list_value_returns_strings(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._parse_llm_response({"prompts": ["x", "y"]}) == ["x", "y"]
        assert gen._parse_llm_response({"key": ["only"]}) == ["only"]

    def test_dict_without_list_returns_empty(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._parse_llm_response({}) == []
        assert gen._parse_llm_response({"a": 1, "b": "x"}) == []

    def test_string_valid_json_array(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._parse_llm_response('["p1", "p2"]') == ["p1", "p2"]

    def test_string_invalid_json_returns_empty(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._parse_llm_response("not json at all") == []

    def test_string_with_think_blocks_cleaned_and_parsed(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        text = '<think>ignore</think>\n["a","b"]'
        assert gen._parse_llm_response(text) == ["a", "b"]


class TestCleanListResponse:
    """Tests for _clean_list_response."""

    def test_empty_content_returns_empty_array(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._clean_list_response("") == "[]"

    def test_valid_json_list_returns_json_string(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._clean_list_response('["a", "b"]') == '["a", "b"]'

    def test_invalid_json_fallback_to_empty_array(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._clean_list_response("not valid") == "[]"

    def test_non_list_json_wrapped_in_list(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        result = gen._clean_list_response('{"x": 1}')
        parsed = json.loads(result)
        assert isinstance(parsed, list) and len(parsed) == 1


# -----------------------------------------------------------------------------
# generate() edge cases
# -----------------------------------------------------------------------------


class TestGenerate:
    """Tests for generate()."""

    @pytest.mark.asyncio
    async def test_no_matching_use_cases_returns_empty(self):
        use_case = _make_use_case(name="RealUC")
        project = _make_project(use_cases=[use_case])
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        result = await gen.generate(use_cases=["NonExistentUC"], prompts_per_use_case=1)
        assert result == []

    @pytest.mark.asyncio
    async def test_exception_in_generate_tasks_for_use_case_continues_and_returns_partial(self):
        use_case_a = _make_use_case(name="A")
        use_case_b = _make_use_case(name="B")
        project = _make_project(use_cases=[use_case_a, use_case_b])
        mock_llm = MagicMock()
        mock_llm.async_predict = AsyncMock(side_effect=[json.dumps(["Task A"]), RuntimeError("fail")])
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        result = await gen.generate(prompts_per_use_case=1, use_cases=None)
        # First use case may succeed, second raises; we should get at least partial result or empty
        assert isinstance(result, list)


# -----------------------------------------------------------------------------
# URL / seed helpers
# -----------------------------------------------------------------------------


class TestBuildConstraintUrl:
    """Tests for _build_constraint_url and _build_constraint_context."""

    def test_dynamic_false_returns_base_url(self):
        project = _make_project(frontend_url="https://base.com/page")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._build_constraint_url("https://base.com/page", False) == "https://base.com/page"

    def test_dynamic_true_adds_seed_when_missing(self):
        project = _make_project(frontend_url="https://base.com/page")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        out = gen._build_constraint_url("https://base.com/page", True)
        assert "seed=" in out and "https://base.com/page" in out

    def test_dynamic_true_keeps_url_when_seed_present(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        url_with_seed = "https://base.com/?seed=42"
        assert gen._build_constraint_url(url_with_seed, True) == url_with_seed

    def test_build_constraint_context_returns_context(self):
        project = _make_project(frontend_url="https://base.com/")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        ctx = gen._build_constraint_context("https://base.com/", True)
        assert ctx.url and ctx.seed >= 1


class TestBuildTaskUrlWithSeed:
    """Tests for _build_task_url_with_seed."""

    def test_dynamic_false_returns_frontend_url(self):
        project = _make_project(frontend_url="https://app.com/")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._build_task_url_with_seed(dynamic=False) == "https://app.com/"

    def test_dynamic_true_adds_seed(self):
        project = _make_project(frontend_url="https://app.com/")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        out = gen._build_task_url_with_seed(dynamic=True)
        assert "seed=" in out


# -----------------------------------------------------------------------------
# Entity type helpers
# -----------------------------------------------------------------------------


class TestEntityTypeHelpers:
    """Tests for _get_entity_type_for_project and _get_entity_types_for_project."""

    def test_get_entity_type_for_project_known(self):
        project = _make_project(project_id="autocinema")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_entity_type_for_project("autocinema_1") == "movies"
        assert gen._get_entity_type_for_project("autobooks_2") == "books"

    def test_get_entity_type_for_project_unknown_returns_none(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_entity_type_for_project("unknown_project") is None

    def test_get_entity_types_for_project_known(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_entity_types_for_project("autocrm_5") == ["matters", "clients", "logs", "events", "files"]

    def test_get_entity_types_for_project_unknown_returns_none(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_entity_types_for_project("unknown") is None


# -----------------------------------------------------------------------------
# _get_project_module_name
# -----------------------------------------------------------------------------


class TestGetProjectModuleName:
    """Tests for _get_project_module_name."""

    def test_returns_none_when_iterdir_raises(self):
        project = _make_project(project_id="dummy")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch.object(Path, "iterdir", side_effect=OSError("read error")):
            result = gen._get_project_module_name()
        assert result is None


# -----------------------------------------------------------------------------
# _get_base_url, _resolve_seed, _dataset_length
# -----------------------------------------------------------------------------


class TestUrlAndDatasetHelpers:
    """Tests for _get_base_url, _resolve_seed, _dataset_length."""

    def test_get_base_url_uses_urls_first(self):
        project = _make_project()
        project.urls = ["https://first.com/", "https://second.com/"]
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_base_url() == "https://first.com/"

    def test_get_base_url_fallback_to_frontend(self):
        project = _make_project(frontend_url="https://front.com/")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        assert gen._get_base_url() == "https://front.com/"

    def test_resolve_seed_caches(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        url = "https://x.com/?seed=7"
        a = gen._resolve_seed(url)
        b = gen._resolve_seed(url)
        assert a == b == 7

    def test_dataset_length_none_returns_none(self):
        assert SimpleTaskGenerator._dataset_length(None) is None

    def test_dataset_length_list_returns_len(self):
        assert SimpleTaskGenerator._dataset_length([1, 2, 3]) == 3


# -----------------------------------------------------------------------------
# _call_llm_with_retry
# -----------------------------------------------------------------------------


class TestCallLlmWithRetry:
    """Tests for _call_llm_with_retry."""

    @pytest.mark.asyncio
    async def test_retry_on_parse_failure_then_succeed(self):
        project = _make_project()
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(side_effect=["not valid json", json.dumps(["Valid prompt"])])
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm, max_retries=3, retry_delay=0.01)
        result = await gen._call_llm_with_retry("prompt")
        assert result == ["Valid prompt"]
        assert mock_llm.async_predict.call_count >= 2

    @pytest.mark.asyncio
    async def test_all_attempts_fail_returns_empty(self):
        project = _make_project()
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(return_value="never valid")
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm, max_retries=2, retry_delay=0.01)
        result = await gen._call_llm_with_retry("prompt")
        assert result == []
        assert mock_llm.async_predict.call_count == 2

    @pytest.mark.asyncio
    async def test_exception_on_first_call_retries_then_succeeds(self):
        project = _make_project()
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(side_effect=[RuntimeError("net error"), json.dumps(["Ok"])])
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm, max_retries=3, retry_delay=0.01)
        result = await gen._call_llm_with_retry("prompt")
        assert result == ["Ok"]


# -----------------------------------------------------------------------------
# generate_tasks_for_use_case branches: no constraints async, empty prompt list, replace_func, apply_replacements_async
# -----------------------------------------------------------------------------


class TestGenerateTasksForUseCaseBranches:
    """Tests for generate_tasks_for_use_case edge cases."""

    @pytest.mark.asyncio
    async def test_no_prompts_from_llm_skips_and_continues(self):
        use_case = _make_use_case()
        project = _make_project(use_cases=[use_case])
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(return_value="[]")
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        tasks = await gen.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)
        assert tasks == []

    @pytest.mark.asyncio
    async def test_use_case_without_generate_constraints_async_uses_fallback_constraints(self):
        use_case = _make_use_case(has_async_constraints=False)
        project = _make_project(use_cases=[use_case])
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(["Do something"]))
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        tasks = await gen.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)
        assert len(tasks) == 1
        assert tasks[0].prompt == "Do something"

    @pytest.mark.asyncio
    async def test_replace_func_with_seed_value_and_dataset(self):
        def replace(text: str, seed_value: int = 1, dataset=None, **kwargs) -> str:
            return text.replace("X", str(seed_value))

        use_case = _make_use_case(replace_func=replace)
        project = _make_project(use_cases=[use_case])
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(["Show X"]))
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        tasks = await gen.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)
        assert len(tasks) == 1
        assert "1" in tasks[0].prompt

    @pytest.mark.asyncio
    async def test_use_case_with_apply_replacements_async(self):
        async def replace_async(text: str, **kwargs) -> str:
            return text + " (async)"

        use_case = _make_use_case(replace_func=replace_async)  # use async replace_func
        # do NOT set use_case.apply_replacements_async = ...
        project = _make_project(use_cases=[use_case])
        mock_llm = MagicMock()
        mock_llm.config = MagicMock(temperature=0.5)
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(["Prompt"]))
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        tasks = await gen.generate_tasks_for_use_case(use_case, number_of_prompts=1, dynamic=False)
        assert len(tasks) == 1
        assert tasks[0].prompt == "Prompt (async)"


# -----------------------------------------------------------------------------
# _load_dataset (mocked project dir / fetch_data)
# -----------------------------------------------------------------------------


class TestLoadDataset:
    """Tests for _load_dataset with mocks."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_project_dir(self):
        project = _make_project(project_id="nonexistent")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch.object(gen, "_get_project_module_name", return_value=None):
            result = await gen._load_dataset(1)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_module_has_no_fetch_data(self):
        project = _make_project(project_id="dummy")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        mock_module = MagicMock(spec=[])
        with patch.object(gen, "_get_project_module_name", return_value="autocinema_1"), patch("importlib.import_module", return_value=mock_module):
            result = await gen._load_dataset(1)
        assert result is None


# -----------------------------------------------------------------------------
# _load_dataset_for_module
# -----------------------------------------------------------------------------


class TestLoadDatasetForModule:
    """Tests for _load_dataset_for_module."""

    @pytest.mark.asyncio
    async def test_returns_cached_value_on_second_call(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        gen._dataset_cache[("some.module", 42)] = [1, 2, 3]
        result = await gen._load_dataset_for_module("some.module", 42)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_returns_none_when_module_has_no_get_data(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        mock_module = MagicMock(spec=[])
        with patch("importlib.import_module", return_value=mock_module):
            result = await gen._load_dataset_for_module("tests.generation.tasks.simple.test_simple_task_generator", 1)
        assert result is None


# -----------------------------------------------------------------------------
# _preload_dataset_for_use_case
# -----------------------------------------------------------------------------


class TestPreloadDatasetForUseCase:
    """Tests for _preload_dataset_for_use_case."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_constraints_generator(self):
        use_case = _make_use_case()
        use_case.constraints_generator = None
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        result = await gen._preload_dataset_for_use_case(use_case, 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_generator_has_no_dataset_param(self):
        use_case = _make_use_case()

        def gen_no_dataset(task_url, something_else):
            return "ok"

        use_case.constraints_generator = gen_no_dataset
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        result = await gen._preload_dataset_for_use_case(use_case, 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_generator_has_no_module(self):
        use_case = _make_use_case()

        def gen_with_dataset(task_url, dataset):
            return "ok"

        use_case.constraints_generator = gen_with_dataset
        use_case.constraints_generator.__module__ = None
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        result = await gen._preload_dataset_for_use_case(use_case, 1)
        assert result is None


# -----------------------------------------------------------------------------
# _update_use_cases_prompt_info
# -----------------------------------------------------------------------------


class TestUpdateUseCasesPromptInfo:
    """Tests for _update_use_cases_prompt_info."""

    @pytest.mark.asyncio
    async def test_returns_early_when_no_module_name(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch.object(gen, "_get_project_module_name", return_value=None):
            await gen._update_use_cases_prompt_info("https://example.com/")
        # No exception, completes

    @pytest.mark.asyncio
    async def test_returns_early_when_use_cases_module_import_fails(self):
        project = _make_project(project_id="dummy")
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch.object(gen, "_get_project_module_name", return_value="autocinema_1"), patch("importlib.import_module", side_effect=ImportError("no module")):
            await gen._update_use_cases_prompt_info("https://example.com/")
        # No exception


# -----------------------------------------------------------------------------
# Logging helpers (_log_task_generation ImportError branch, _ensure_task_generation_level)
# -----------------------------------------------------------------------------


class TestLogTaskGeneration:
    """Tests for _log_task_generation and _ensure_task_generation_level."""

    def test_ensure_task_generation_level_creates_level_on_value_error(self):
        from autoppia_iwa.src.data_generation.tasks.simple import simple_task_generator as m

        with patch.object(m.logger, "level") as mock_level:
            mock_level.side_effect = [ValueError("no level"), None]
            m._ensure_task_generation_level()
            assert mock_level.call_count >= 2

    def test_log_task_generation_uses_fallback_on_import_error(self):
        import builtins

        from autoppia_iwa.src.data_generation.tasks.simple import simple_task_generator as m

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if "entrypoints.benchmark.utils.logging" in (name or ""):
                raise ImportError("no benchmark logging")
            return real_import(name, *args, **kwargs)

        with patch.object(m, "_ensure_task_generation_level"), patch.object(m.logger, "log"), patch("builtins.__import__", fake_import):
            m._log_task_generation("fallback message", context="TASK_GENERATION")


# -----------------------------------------------------------------------------
# _dataset_length, _load_dataset_for_module import error, _call_llm no config, _parse_llm exception, _clean_list_response
# -----------------------------------------------------------------------------


class TestDatasetLength:
    """Tests for _dataset_length static method."""

    def test_returns_none_for_none(self):
        assert SimpleTaskGenerator._dataset_length(None) is None

    def test_returns_len_for_list(self):
        assert SimpleTaskGenerator._dataset_length([1, 2, 3]) == 3

    def test_returns_none_for_type_error(self):
        """Covers lines 466-467: when len(dataset) raises TypeError, return None."""

        class NoLen:
            pass

        assert SimpleTaskGenerator._dataset_length(NoLen()) is None


class TestLoadDatasetForModuleImportError:
    """Covers _load_dataset_for_module when import_module raises."""

    @pytest.mark.asyncio
    async def test_returns_none_when_import_raises(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch("importlib.import_module", side_effect=ImportError("no module")):
            result = await gen._load_dataset_for_module("nonexistent.module", 1)
        assert result is None


class TestCallLlmWithRetryNoConfig:
    """Covers _call_llm_with_retry when llm_service has no config (line 518)."""

    @pytest.mark.asyncio
    async def test_uses_unknown_temp_when_no_config(self):
        project = _make_project()
        mock_llm = MagicMock()
        del mock_llm.config
        mock_llm.async_predict = AsyncMock(return_value=json.dumps(["ok"]))
        gen = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)
        with patch("builtins.print", MagicMock()):
            result = await gen._call_llm_with_retry("prompt")
        assert result == ["ok"]


class TestParseLlmResponseException:
    """Covers _parse_llm_response exception branch (lines 570-572)."""

    def test_returns_empty_on_exception(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        with patch.object(gen, "_clean_list_response", side_effect=RuntimeError("parse error")):
            result = gen._parse_llm_response("some string")
        assert result == []


class TestCleanListResponseCodePaths:
    """Covers _clean_list_response <think> and code block removal, non-list wrap."""

    def test_removes_think_blocks_and_parses(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        content = '<think>reasoning</think>\n["a","b"]'
        result = gen._clean_list_response(content)
        parsed = json.loads(result)
        assert parsed == ["a", "b"]

    def test_removes_markdown_code_blocks(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        content = '```json\n["x"]\n```'
        result = gen._clean_list_response(content)
        parsed = json.loads(result)
        assert parsed == ["x"]

    def test_preserves_signup_placeholders(self):
        project = _make_project()
        gen = SimpleTaskGenerator(web_project=project, llm_service=MagicMock())
        content = '["Register with <signup_username> <signup_email> <signup_password> <email> <username> <password>"]'
        result = gen._clean_list_response(content)
        parsed = json.loads(result)
        assert parsed == ["Register with <signup_username> <signup_email> <signup_password> <email> <username> <password>"]
