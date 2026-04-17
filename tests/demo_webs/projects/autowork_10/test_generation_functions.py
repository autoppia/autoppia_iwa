from __future__ import annotations

from datetime import date, datetime, time

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p10_autowork import generation_functions as gf

EXPERTS = [
    {
        "slug": "alice-smith",
        "name": "Alice Smith",
        "title": "Backend Engineer",
        "team": "Microsoft",
        "skills": "Python",
    },
    {
        "slug": "bob-jones",
        "name": "Bob Jones",
        "title": "UX Designer",
        "team": "Apple",
        "skills": "Figma",
    },
]

SKILLS = ["Python", "React", "Figma"]


@pytest.fixture
def deterministic_random(monkeypatch: pytest.MonkeyPatch) -> None:
    def _choice(seq):
        if isinstance(seq, str):
            return seq[-1]
        return next(iter(seq))

    monkeypatch.setattr(gf, "choice", _choice)
    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "shuffle", lambda population: None)
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)


@pytest.fixture
def patched_datasets(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_ensure_dataset(task_url=None, dataset=None, *, entity_type: str):
        if entity_type == "experts":
            return EXPERTS
        if entity_type == "skills":
            return SKILLS
        return []

    monkeypatch.setattr(gf, "_ensure_dataset", _fake_ensure_dataset)


def test_collection_and_list_helpers():
    dataset = [{"name": "A"}, {"name": "A"}, {"name": "B"}, {"name": None}]
    assert set(gf._collect_field_values_from_dataset(dataset, "name")) == {"A", "B"}
    assert gf._list_to_field_dataset(["x", "y"], "skill") == [{"skill": "x"}, {"skill": "y"}]


@pytest.mark.asyncio
async def test_get_experts_and_skills_wrappers(monkeypatch: pytest.MonkeyPatch):
    async def _bad_experts(*args, **kwargs):
        return ["not-a-dict"]

    async def _bad_skills(*args, **kwargs):
        return [{"name": "Python"}]

    monkeypatch.setattr(gf, "_ensure_dataset", _bad_experts)
    assert await gf._get_experts_data("http://localhost") == []

    monkeypatch.setattr(gf, "_ensure_dataset", _bad_skills)
    skills = await gf._get_skills_list("http://localhost")
    assert "Python" in skills


def test_generate_constraint_value_for_core_types(deterministic_random):
    dataset = [{"score": 10, "name": "Alice Smith"}, {"score": 20, "name": "Bob Jones"}]
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Alice", "name", dataset) == "Alice"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Alice Smith", "name", dataset) == "Bob Jones"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Alice Smith", "name", dataset)
    assert isinstance(contains_value, str)
    assert contains_value
    assert contains_value in "Alice Smith"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Alice Smith", "name", dataset) == ["Bob Jones"]
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 10, "score", dataset) < 10
    assert gf._generate_constraint_value(ComparisonOperator.LESS_EQUAL, datetime(2026, 1, 1), "created_at", [{"created_at": datetime(2026, 1, 1)}]) == datetime(2026, 1, 1)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, time(10, 0), "meeting_time", [{"meeting_time": time(10, 0)}]) == time(10, 0)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, date(2026, 1, 1), "day", [{"day": date(2026, 1, 1)}]) == date(2026, 1, 1)


def test_generate_single_field_helpers(deterministic_random):
    budget = gf.generate_budget_type_constraint()
    scope = gf.generate_project_size_constraint()
    timeline = gf.generate_timeline_constraint()
    rate_range = gf.generate_rate_range_constraint()
    description = gf.generate_write_job_description_constraint()
    assert budget[0]["field"] == "budget_type"
    assert scope[0]["field"] == "scope"
    assert timeline[0]["field"] == "duration"
    assert {c["field"] for c in rate_range} == {"rate_from", "rate_to"}
    assert description[0]["field"] == "description"


def test_generate_constraints_supports_custom_dataset_mapping(deterministic_random):
    constraints = gf._generate_constraints(
        EXPERTS,
        {"team": ["equals"], "query": ["equals"]},
        field_map={
            "team": {"field": "team", "dataset": gf._list_to_field_dataset(["Microsoft", "Apple"], "team")},
            "query": ["name", "title"],
        },
        selected_fields=["team", "query"],
    )
    assert {c["field"] for c in constraints} == {"team", "query"}


@pytest.mark.asyncio
async def test_generate_expert_selection_constraints(deterministic_random, patched_datasets):
    book = await gf.generate_book_consultant_constraint("http://localhost:8000/?seed=1")
    hire = await gf.generate_hire_button_clicked_constraint("http://localhost:8000/?seed=1")
    message = await gf.generate_content_expert_message_sent_constraint("http://localhost:8000/?seed=1")
    team = await gf.generate_select_hiring_team_constraint("http://localhost:8000/?seed=1")
    consultation = await gf.generate_hire_consultation_constraint("http://localhost:8000/?seed=1")
    quick = await gf.generate_quick_hire_constraint("http://localhost:8000/?seed=1")
    cancel = await gf.generate_cancel_hire_constraint("http://localhost:8000/?seed=1")
    assert len(book) >= 1
    assert len(hire) >= 1
    assert {c["field"] for c in message} >= {"message"}
    assert {c["field"] for c in team}
    assert {c["field"] for c in consultation}
    assert quick == book
    assert len(cancel) >= 1


@pytest.mark.asyncio
async def test_generate_posting_and_title_constraints(deterministic_random):
    posting = await gf.generate_job_posting_constraint()
    title = gf.generate_write_job_title_constraint()
    assert {c["field"] for c in posting}
    assert title[0]["field"] == "query"


@pytest.mark.asyncio
async def test_generate_skill_and_job_form_constraints(deterministic_random, patched_datasets):
    search_skill = await gf.generate_search_skill_constraint("http://localhost:8000/?seed=1")
    add_skill = await gf.generate_add_skill_constraint("http://localhost:8000/?seed=1")
    submit_job = await gf.generate_submit_job_constraint("http://localhost:8000/?seed=1")
    close_job = await gf.generate_close_posting_job_constraint("http://localhost:8000/?seed=1")
    assert search_skill[0]["field"] == "skill"
    assert {c["field"] for c in add_skill}
    assert {c["field"] for c in submit_job}
    assert {c["field"] for c in close_job}


def test_value_for_job_form_field_generates_rates_and_options(deterministic_random):
    constraints: list[dict] = []
    rate_constraints: list[dict] = []
    sample_skills = {"skills": "Python"}
    popular_skill_data = [{"skills": "Python"}]
    assert gf._value_for_job_form_field("budgetType", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("description", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("duration", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("scope", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("skills", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("title", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints)
    assert gf._value_for_job_form_field("rate_from", ComparisonOperator.EQUALS, sample_skills, popular_skill_data, rate_constraints, constraints) is None
    assert {c["field"] for c in constraints} == {"rate_from", "rate_to"}


@pytest.mark.asyncio
async def test_generate_favorite_expert_constraints(deterministic_random, patched_datasets):
    selected = await gf.generate_favorite_expert_selected_constraint("http://localhost:8000/?seed=1")
    removed = await gf.generate_favorite_expert_removed_constraint("http://localhost:8000/?seed=1")
    browse = gf.generate_browse_favorite_expert_constraint()
    assert {c["field"] for c in selected}
    assert removed == selected
    assert browse[0]["field"] == "source"


def test_generate_edit_profile_constraints(deterministic_random):
    about = gf.generate_edit_about_constraint()
    name = gf.generate_edit_profile_name_constraint()
    title = gf.generate_edit_profile_title_constraint()
    location = gf.generate_edit_profile_location_constraint()
    email = gf.generate_edit_profile_email_constraint()
    assert about[0]["field"] == "value"
    assert name[0]["field"] == "value"
    assert title[0]["field"] == "value"
    assert location[0]["field"] == "value"
    assert email[0]["field"] == "value"


def test_generate_to_and_from_constraints(deterministic_random):
    constraints = gf.generate_to_and_from_constraints(["equals"], ["equals"])
    assert {c["field"] for c in constraints} == {"rate_from", "rate_to"}
    rate_from = next(c for c in constraints if c["field"] == "rate_from")
    rate_to = next(c for c in constraints if c["field"] == "rate_to")
    assert rate_to["value"] > rate_from["value"]


@pytest.mark.asyncio
async def test_generate_autowork_contact_page_viewed_constraints(deterministic_random):
    out = await gf.generate_autowork_contact_page_viewed_constraints()
    assert len(out) == 1
    assert out[0]["field"] == "page"


@pytest.mark.asyncio
async def test_generate_autowork_contact_form_submitted_constraints(deterministic_random):
    normal = await gf.generate_autowork_contact_form_submitted_constraints()
    assert len(normal) >= 1
    assert {c["field"] for c in normal} <= {"name", "email", "subject", "message"}

    de = await gf.generate_autowork_contact_form_submitted_constraints(test_types="data_extraction_only")
    assert isinstance(de, dict)
    assert "constraints" in de and "question_fields_and_values" in de
