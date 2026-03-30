"""Unit tests for demo_webs.classes (UseCase, WebProject, BackendEvent)."""

from unittest.mock import MagicMock

import pytest

from autoppia_iwa.src.demo_webs.classes import (
    CONSTRAINTS_INFO_PLACEHOLDER,
    BackendEvent,
    UseCase,
    WebProject,
)
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator


class TestUseCaseConstraintsToStr:
    def test_empty_constraints_returns_empty_string(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints=None,
        )
        assert uc.constraints_to_str() == ""

    def test_single_constraint(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints=[{"field": "name", "operator": ComparisonOperator.EQUALS, "value": "Alice"}],
        )
        s = uc.constraints_to_str()
        assert "name" in s
        assert "equals" in s
        assert "Alice" in s

    def test_constraint_with_list_value(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints=[{"field": "tags", "operator": ComparisonOperator.CONTAINS, "value": ["a", "b"]}],
        )
        s = uc.constraints_to_str()
        assert "tags" in s
        assert "a" in s and "b" in s


class TestUseCaseReplacements:
    def test_apply_replacements_no_replace_func_replaces_placeholder(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints=[{"field": "x", "operator": "equals", "value": "v"}],
        )
        text = f"Hello {CONSTRAINTS_INFO_PLACEHOLDER} world"
        result = uc.apply_replacements(text)
        assert CONSTRAINTS_INFO_PLACEHOLDER not in result
        assert "x equals v" in result or "1)" in result

    def test_apply_replacements_no_placeholder_unchanged(self):
        uc = UseCase(name="UC", description="d", event=None, event_source_code="", examples=[], constraints=None)
        result = uc.apply_replacements("No placeholder here")
        assert result == "No placeholder here"

    def test_apply_replacements_sync_replace_func(self):
        def replace(text, **kwargs):
            return text.replace("X", "Y")

        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            replace_func=replace,
        )
        result = uc.apply_replacements("Hello X")
        assert result == "Hello Y"

    @pytest.mark.asyncio
    async def test_apply_replacements_async_replace_func(self):
        async def replace(text, **kwargs):
            return text.replace("X", "Y")

        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            replace_func=replace,
        )
        result = await uc.apply_replacements_async("Hello X")
        assert result == "Hello Y"


class TestUseCaseConstraintsGeneration:
    @pytest.mark.asyncio
    async def test_generate_constraints_async_passes_dataset_to_single_param_generator(self):
        captured = {}

        def generator(dataset):
            captured["dataset"] = dataset
            return [{"field": "name", "operator": "equals", "value": "Alice"}]

        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints_generator=generator,
        )

        result = await uc.generate_constraints_async(dataset={"users": [{"name": "Alice"}]})
        assert "Alice" in result
        assert captured["dataset"] == {"users": [{"name": "Alice"}]}

    @pytest.mark.asyncio
    async def test_generate_constraints_async_passes_named_kwargs(self):
        captured = {}

        async def generator(*, task_url=None, dataset=None):
            captured["task_url"] = task_url
            captured["dataset"] = dataset
            return [{"field": "city", "operator": "equals", "value": "Madrid"}]

        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[],
            constraints_generator=generator,
        )

        result = await uc.generate_constraints_async(task_url="http://localhost/?seed=5", dataset={"users": []})
        assert "Madrid" in result
        assert captured["task_url"] == "http://localhost/?seed=5"
        assert captured["dataset"] == {"users": []}


class TestUseCaseExamples:
    def test_get_example_prompts_from_use_case(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[
                {"prompt": "p1", "prompt_for_task_generation": "gen1"},
                {"prompt": "p2", "prompt_for_task_generation": "gen2"},
            ],
        )
        prompts = uc.get_example_prompts_from_use_case()
        assert prompts == ["gen1", "gen2"]

    def test_get_example_prompts_str(self):
        uc = UseCase(
            name="UC",
            description="d",
            event=None,
            event_source_code="",
            examples=[
                {"prompt_for_task_generation": "a"},
                {"prompt_for_task_generation": "b"},
            ],
        )
        assert uc.get_example_prompts_str(separator=" | ") == "a | b"


class TestUseCaseSerialize:
    def test_serialize_includes_event_name_and_constraints(self):
        uc = UseCase(
            name="UC1",
            description="d",
            event=MagicMock(__name__="MockEvent"),
            event_source_code="code",
            examples=[],
            constraints=[{"field": "f", "operator": "equals", "value": "v"}],
        )
        data = uc.serialize()
        assert data["name"] == "UC1"
        assert data["event"] == "MockEvent"
        assert data.get("constraints") is not None

    def test_deserialize_rehydrates_event_class(self, monkeypatch):
        class FakeEvent:
            @staticmethod
            def get_source_code_of_class():
                return "class FakeEvent: ..."

        monkeypatch.setattr(
            "autoppia_iwa.src.demo_webs.base_events.EventRegistry.get_event_class",
            lambda name: FakeEvent,
        )

        uc = UseCase.deserialize(
            {
                "name": "UC1",
                "description": "d",
                "event": "FakeEvent",
                "event_source_code": True,
                "examples": [],
            }
        )

        assert uc.event is FakeEvent
        assert uc.event_source_code == "class FakeEvent: ..."


class TestWebProject:
    def test_web_project_minimal(self):
        p = WebProject(
            id="proj1",
            name="Project 1",
            backend_url="http://localhost:8000",
            frontend_url="http://localhost:3000",
        )
        assert p.id == "proj1"
        assert p.name == "Project 1"
        assert p.is_web_real is False
        assert p.sandbox_mode is False


class TestBackendEvent:
    def test_backend_event_minimal(self):
        e = BackendEvent(event_name="TEST_EVENT")
        assert e.event_name == "TEST_EVENT"
        assert e.data is None

    def test_backend_event_with_data(self):
        e = BackendEvent(event_name="E", data={"key": "value"}, web_agent_id="agent1")
        assert e.data == {"key": "value"}
        assert e.web_agent_id == "agent1"
