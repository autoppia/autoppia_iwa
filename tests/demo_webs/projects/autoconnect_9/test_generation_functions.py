from __future__ import annotations

from datetime import datetime

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p09_autoconnect import generation_functions as gf

USERS = [
    {
        "username": "alexsmith",
        "name": "Alex Smith",
        "title": "Founder",
        "bio": "Building things",
        "about": "Loves startups\nand products.",
        "experience": [
            {
                "title": "CEO",
                "duration": "2020 - Present",
                "description": "Leading company strategy\nand execution.",
                "company": "Startly",
                "location": "Remote",
            }
        ],
    },
    {
        "username": "bettyjones",
        "name": "Betty Jones",
        "title": "Designer",
        "bio": "Design systems",
        "about": "Design leader",
        "experience": [
            {
                "title": "Lead Designer",
                "duration": "2019 - Present",
                "description": "Owns the product design system.",
                "company": "Pixel Labs",
                "location": "New York, NY",
            }
        ],
    },
    {
        "username": "carlng",
        "name": "Carl Ng",
        "title": "Engineer",
        "bio": "Backend specialist",
        "about": "Writes APIs and infra",
        "experience": [
            {
                "title": "Senior Engineer",
                "duration": "2018 - Present",
                "description": "Builds resilient distributed systems.",
                "company": "Infra Co",
                "location": "Austin, TX",
            }
        ],
    },
]

POSTS = [
    {
        "content": "e yesterday we launched a new platform for creators",
        "name": "Betty Jones",
        "user": {"name": "Betty Jones", "username": "bettyjones"},
    },
    {
        "content": "Learning distributed systems in public",
        "name": "Carl Ng",
        "user": {"name": "Carl Ng", "username": "carlng"},
    },
]

JOBS = [
    {"title": "Backend Engineer", "company": "Acme", "location": "Remote", "salary": "$75,000", "experience": "3+ years"},
    {"title": "Product Designer", "company": "Globex", "location": "Boston, MA", "salary": "100000-125000", "experience": "4+ years"},
]

RECOMMENDATIONS = [
    {"title": "Remote Works Company"},
    {"title": "Design Guild"},
]


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
def patched_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_get_entity_list(task_url, dataset, entity_type):
        mapping = {
            "users": USERS,
            "posts": POSTS,
            "jobs": JOBS,
            "recommendations": RECOMMENDATIONS,
        }
        return mapping[entity_type]

    monkeypatch.setattr(gf, "_get_entity_list", _fake_get_entity_list)


def test_extract_entity_dataset_and_nested_helpers():
    assert gf._extract_entity_dataset(None, "users") is None
    assert gf._extract_entity_dataset(USERS, "users") == USERS
    assert gf._extract_entity_dataset({"users": USERS}, "users") == USERS
    assert gf._get_nested_value({"a": {"b": 3}}, "a.b") == 3
    assert gf._get_nested_value({"a": {}}, "a.b", "x") == "x"


def test_salary_helpers_and_string_normalizers():
    assert gf._parse_min_salary_from_raw_value("$75,000") == 75000
    assert gf._parse_min_salary_from_raw_value("100000-125000") == 100000
    assert gf._parse_min_salary_from_raw_value("150000+") == 150000
    assert gf._parse_min_salary_from_raw_value("bad") is None
    assert gf._match_salary_to_filter_option(75000, gf.FILTER_JOBS_OPTIONS["salary"]) == "50000-75000"
    constraint = {"field": "salary", "value": "$75,000"}
    gf._apply_salary_filter_to_constraint(constraint, gf.FILTER_JOBS_OPTIONS["salary"])
    assert constraint["value"] == "50000-75000"
    assert gf._normalize_constraint_string(" a\n b  c ") == "a b c"
    assert gf._single_word_for_contains("Remote Works Company") == "Company"
    assert gf._normalize_constraint_value("e yesterday\nwe shipped", trim_leading_single_letter=True) == "yesterday we shipped"


def test_generate_constraint_value_supports_common_operator_types(deterministic_random):
    dataset = [{"score": 10, "name": "Alice Johnson"}, {"score": 20, "name": "Bob Stone"}]
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Alice", "name", dataset) == "Alice"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Alice Johnson", "name", dataset) == "Bob Stone"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Alice Johnson", "name", dataset)
    assert isinstance(contains_value, str)
    assert contains_value
    assert contains_value in "Alice Johnson"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "Alice Johnson", "name", dataset) == "zzz"
    assert set(gf._generate_constraint_value(ComparisonOperator.IN_LIST, "Alice Johnson", "name", dataset)) == {"Alice Johnson", "Bob Stone"}
    assert gf._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Alice Johnson", "name", dataset) == ["Bob Stone"]
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 10, "score", dataset) < 20
    assert gf._generate_constraint_value(ComparisonOperator.LESS_EQUAL, datetime(2026, 1, 1), "created_at", [{"created_at": datetime(2026, 1, 1)}]) == datetime(2026, 1, 1)


def test_generate_constraints_supports_field_maps_and_nested_values(deterministic_random):
    dataset = [
        {"name": "Alice Johnson", "company": {"name": "Acme"}, "title": "Engineer"},
        {"name": "Bob Stone", "company": {"name": "Globex"}, "title": "Designer"},
    ]
    constraints = gf._generate_constraints(
        dataset,
        {"query": ["equals"], "company_name": ["equals"]},
        field_map={"query": ["name", "title"], "company_name": "company.name"},
        selected_fields=["query", "company_name"],
    )
    assert {c["field"] for c in constraints} == {"query", "company_name"}


def test_normalize_edit_profile_and_experience_helpers():
    assert gf._normalize_edit_profile_value("name", "Carl Ng", ComparisonOperator.CONTAINS) == "Carl"
    assert gf._normalize_edit_profile_value("about", "Line 1\nLine 2", ComparisonOperator.EQUALS) == "Line 1 Line 2"
    experience_data = gf._get_experience_data_for_user(USERS[2])
    assert experience_data[0]["title"] == "Senior Engineer"
    assert experience_data[0]["restaurant"] == "Carl Ng"


@pytest.mark.asyncio
async def test_generate_view_and_connect_user_constraints(deterministic_random, patched_entities):
    profile_constraints = await gf.generate_view_user_profile_constraints("http://localhost:8000/?seed=1")
    connect_constraints = await gf.generate_connect_with_user_constraints("http://localhost:8000/?seed=1")
    assert profile_constraints[0]["field"] == "name"
    assert all(c["field"] in {"target_username", "target_name"} for c in connect_constraints)
    assert all(c["value"] != "Alex Smith" for c in connect_constraints)


@pytest.mark.asyncio
async def test_generate_post_related_constraints(deterministic_random, patched_entities):
    like_constraints = await gf.generate_like_post_constraints("http://localhost:8000/?seed=1")
    comment_constraints = await gf.generate_comment_on_post_constraints("http://localhost:8000/?seed=1")
    save_constraints = await gf.generate_save_post_constraints("http://localhost:8000/?seed=1")
    remove_constraints = await gf.generate_remove_post_constraints("http://localhost:8000/?seed=1")
    unhide_constraints = await gf.generate_unhide_post_constraints("http://localhost:8000/?seed=1")
    assert {c["field"] for c in like_constraints} == {"poster_name", "poster_content"}
    assert {c["field"] for c in comment_constraints} >= {"comment_text"}
    assert {c["field"] for c in save_constraints} == {"author", "content"}
    assert remove_constraints == save_constraints
    assert unhide_constraints == save_constraints


def test_generate_post_status_constraints(deterministic_random):
    constraints = gf.generate_post_status_constraints()
    assert len(constraints) == 1
    assert constraints[0]["field"] == "content"


@pytest.mark.asyncio
async def test_generate_recommendation_constraints(deterministic_random, patched_entities):
    follow_constraints = await gf.generate_follow_page_constraints("http://localhost:8000/?seed=1")
    unfollow_constraints = await gf.generate_unfollow_page_constraints("http://localhost:8000/?seed=1")
    assert {c["field"] for c in follow_constraints} == {"recommendation"}
    assert {c["field"] for c in unfollow_constraints} == {"recommendation"}


@pytest.mark.asyncio
async def test_generate_job_constraints(deterministic_random, patched_entities):
    apply_constraints = await gf.generate_apply_for_job_constraints("http://localhost:8000/?seed=1")
    search_users_constraints = await gf.generate_search_users_constraints("http://localhost:8000/?seed=1")
    search_jobs_constraints = await gf.generate_search_jobs_constraints("http://localhost:8000/?seed=1")
    view_job_constraints = await gf.generate_view_job_constraints("http://localhost:8000/?seed=1")
    back_constraints = await gf.generate_back_to_all_jobs_constraints("http://localhost:8000/?seed=1")
    cancel_constraints = await gf.generate_cancel_application_constraints("http://localhost:8000/?seed=1")
    assert {c["field"] for c in apply_constraints}
    assert {c["field"] for c in search_users_constraints} == {"query"}
    assert {c["field"] for c in search_jobs_constraints} == {"query"}
    assert {c["field"] for c in view_job_constraints}
    assert {c["field"] for c in back_constraints}
    assert cancel_constraints == apply_constraints


def test_generate_filter_jobs_constraints(deterministic_random):
    constraints = gf.generate_filter_jobs_constraints()
    assert {c["field"] for c in constraints} == {"experience", "salary", "location", "remote"}
    salary_constraint = next(c for c in constraints if c["field"] == "salary")
    assert salary_constraint["value"] in gf.FILTER_JOBS_OPTIONS["salary"]


@pytest.mark.asyncio
async def test_generate_profile_and_experience_constraints(deterministic_random, patched_entities):
    edit_profile_constraints = await gf.generate_edit_profile_constraints("http://localhost:8000/?seed=1")
    edit_experience_constraints = await gf.generate_edit_experience_constraints("http://localhost:8000/?seed=1")
    add_experience_constraints = await gf.generate_add_experience_constraints("http://localhost:8000/?seed=1")
    assert {c["field"] for c in edit_profile_constraints}
    assert {c["field"] for c in edit_experience_constraints}
    assert {c["field"] for c in add_experience_constraints} == {"company", "duration", "title", "location", "description"}
