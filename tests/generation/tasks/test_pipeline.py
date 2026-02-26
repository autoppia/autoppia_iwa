from __future__ import annotations

import asyncio
import json

from autoppia_iwa.src.data_generation.tasks.classes import TaskGenerationConfig
from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
from autoppia_iwa.src.data_generation.tasks.simple.simple_task_generator import SimpleTaskGenerator
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest
from autoppia_iwa.src.data_generation.tests.simple.test_generation_pipeline import GlobalTestGenerationPipeline
from autoppia_iwa.src.demo_webs.classes import UseCase, WebProject
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator


class DummyEvent(Event):
    event_name: str = "DUMMY_EVENT"

    class ValidationCriteria(Event.ValidationCriteria):
        value: str | None = None


class MockLLMService:
    def __init__(self, responses: list[str]):
        self._responses = responses
        self._idx = 0

    async def async_predict(self, *args, **kwargs):
        response = self._responses[self._idx % len(self._responses)]
        self._idx += 1
        return response


def _build_use_case() -> UseCase:
    use_case = UseCase(
        name="DUMMY_EVENT",
        description="Test use case",
        event=DummyEvent,
        event_source_code="class DummyEvent: pass",
        examples=[
            {
                "prompt": "Do dummy action",
                "prompt_for_task_generation": "Do dummy action",
            },
            {
                "prompt": "Do another dummy action",
                "prompt_for_task_generation": "Do another dummy action",
            },
        ],
    )
    use_case.constraints = [{"field": "value", "operator": ComparisonOperator.EQUALS, "value": "ok"}]
    return use_case


def test_task_generation_pipeline_builds_tasks_and_tests():
    use_case = _build_use_case()
    project = WebProject(
        id="dummy",
        name="Dummy Project",
        backend_url="https://example.com/api/",
        frontend_url="https://example.com/",
        use_cases=[use_case],
    )
    mock_llm = MockLLMService([json.dumps(["Prompt A", "Prompt B"])])
    config = TaskGenerationConfig(prompts_per_use_case=2, use_cases=None)
    pipeline = TaskGenerationPipeline(web_project=project, config=config, llm_service=mock_llm)

    async def run():
        tasks = await pipeline.generate()
        assert len(tasks) == 2
        for task in tasks:
            assert task.use_case is not None
            assert task.web_project_id == "dummy"
            assert task.tests, "Each task should have tests attached"
            assert isinstance(task.tests[0], CheckEventTest)

    asyncio.run(run())


def test_global_test_generation_attaches_event_criteria():
    use_case = _build_use_case()
    mock_task = use_case.examples[0]["prompt"]
    project = WebProject(id="dummy", name="Dummy", backend_url="", frontend_url="", use_cases=[use_case])
    mock_llm = MockLLMService([json.dumps([mock_task])])

    pipeline = SimpleTaskGenerator(web_project=project, llm_service=mock_llm)

    async def run():
        tasks = await pipeline.generate(prompts_per_use_case=1, use_cases=[use_case.name])

        assert len(tasks) == 1
        task = tasks[0]
        assert task.use_case is use_case

        test_pipeline = GlobalTestGenerationPipeline()
        enriched = test_pipeline.add_tests_to_tasks(tasks)
        assert enriched[0].tests, "CheckEventTest should be attached"
        check_test = enriched[0].tests[0]
        assert isinstance(check_test, CheckEventTest)
        assert check_test.event_name == "DUMMY_EVENT"
        assert check_test.event_criteria["value"] == "ok"

    asyncio.run(run())


def test_prompts_per_use_case_auto(monkeypatch):
    use_case = _build_use_case()
    project = WebProject(id="dummy", name="Dummy", backend_url="", frontend_url="", use_cases=[use_case])
    pipeline = SimpleTaskGenerator(web_project=project, llm_service=None)

    recorded_counts: list[int] = []

    async def fake_generate_tasks(use_case_arg, number_of_prompts):
        recorded_counts.append(number_of_prompts)
        return []

    monkeypatch.setattr(pipeline, "generate_tasks_for_use_case", fake_generate_tasks)

    async def run():
        await pipeline.generate(use_cases=None, prompts_per_use_case=0)

    asyncio.run(run())
    assert recorded_counts == [len(use_case.examples)]
