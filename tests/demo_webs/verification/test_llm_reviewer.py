from pydantic import BaseModel

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.web_verification.llm_reviewer import LLMReviewer


class _FakeLLM:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def async_predict(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class _ValidationCriteria(BaseModel):
    title: str | None = None
    rating: int | None = None


class _DummyEvent:
    ValidationCriteria = _ValidationCriteria


def _build_task(constraints):
    use_case = UseCase(
        name="VIEW_MOVIE",
        description="Review a movie entry",
        event=_DummyEvent,
        event_source_code="class ValidationCriteria: ...",
        examples=[],
        constraints=constraints,
    )
    return Task(
        id="task-1",
        url="http://localhost:8000/movies?seed=1",
        prompt="Open the movie with title Inception and rating 5",
        tests=[],
        use_case=use_case,
    )


def test_parse_llm_response_extracts_json_and_enforces_binary_score():
    reviewer = LLMReviewer(llm_service=_FakeLLM({}))

    result = reviewer._parse_llm_response("""```json\n{\"valid\": true, \"score\": 0.4, \"issues\": [], \"reasoning\": \"ok\"}\n```""")

    assert result["valid"] is True
    assert result["score"] == 1.0


def test_heuristic_value_presence_check_flags_missing_values():
    reviewer = LLMReviewer(llm_service=_FakeLLM({}))

    result = reviewer._heuristic_value_presence_check(
        "Open the movie with title Inception",
        [{"field": "rating", "operator": "equals", "value": 5}],
    )

    assert result["pass"] is False
    assert "Missing value '5' for field 'rating'" in result["issues"]


def test_review_task_and_constraints_skips_llm_when_no_constraints():
    llm = _FakeLLM({"valid": True, "score": 1.0, "issues": [], "reasoning": "ok"})
    reviewer = LLMReviewer(llm_service=llm)
    task = _build_task(constraints=None)

    result = __import__("asyncio").run(reviewer.review_task_and_constraints(task))

    assert result["valid"] is True
    assert result["score"] == 1.0
    assert result["skipped"] is True
    assert llm.calls == []


def test_extract_available_fields_uses_validation_criteria():
    reviewer = LLMReviewer(llm_service=_FakeLLM({}))
    task = _build_task(constraints=[{"field": "title", "operator": "equals", "value": "Inception"}])

    fields = reviewer._extract_available_fields(task.use_case, task.use_case.name)

    assert "title" in fields
    assert "rating" in fields
