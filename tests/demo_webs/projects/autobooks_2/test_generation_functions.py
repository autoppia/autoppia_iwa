"""Tests for autobooks generation_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p02_autobooks import generation_functions as gen

SAMPLE_BOOKS = [
    {
        "name": "Dune",
        "author": "Frank Herbert",
        "desc": "Epic desert saga",
        "year": 1965,
        "page_count": 412,
        "price": 19.5,
        "rating": 4.8,
        "genres": ["Sci-Fi", "Adventure"],
    },
    {
        "name": "It",
        "author": "Stephen King",
        "desc": "Horror in Derry",
        "year": 1986,
        "page_count": 1000,
        "price": 24.0,
        "rating": 4.1,
        "genres": ["Horror"],
    },
]


@pytest.mark.asyncio
async def test_get_books_from_task_or_dataset_fetches_when_missing(monkeypatch):
    fetch = AsyncMock(return_value=SAMPLE_BOOKS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    dataset, books = await gen._get_books_from_task_or_dataset("http://localhost:8000/?seed=12", None)

    assert dataset == {"books": SAMPLE_BOOKS}
    assert books == SAMPLE_BOOKS
    fetch.assert_awaited_once_with(seed_value=12)


def test_default_auth_constraints_use_placeholders():
    constraints = gen._default_auth_constraints()
    assert constraints == [
        {"field": "username", "operator": ComparisonOperator.EQUALS, "value": "<username>"},
        {"field": "password", "operator": ComparisonOperator.EQUALS, "value": "<password>"},
    ]


def test_registration_login_logout_delete_constraints(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.projects.p02_autobooks.utils.parse_constraints_str",
        lambda text: text,
    )
    assert "<signup_username>" in gen.generate_registration_constraints()
    assert "<username>" in gen.generate_login_constraints()
    assert "<username>" in gen.generate_logout_constraints()
    assert "<username>" in gen.generate_delete_book_constraints()


@pytest.mark.asyncio
async def test_generate_book_constraints_appends_auth(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.projects.p02_autobooks.utils.build_constraints_info",
        lambda books: "name equals Dune",
    )

    result = await gen.generate_book_constraints(dataset={"books": SAMPLE_BOOKS})

    assert [c["field"] for c in result] == ["name", "username", "password"]


@pytest.mark.asyncio
async def test_generate_book_details_constraints_returns_none_without_books():
    assert await gen.generate_book_details_constraints(dataset={"books": []}) is None


@pytest.mark.asyncio
async def test_generate_book_details_constraints_returns_parsed_constraints(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.projects.p02_autobooks.utils.build_constraints_info",
        lambda books: "author equals Frank Herbert",
    )
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.projects.p02_autobooks.utils.parse_constraints_str",
        lambda text: [{"field": "author", "operator": ComparisonOperator.EQUALS, "value": "Frank Herbert"}],
    )

    result = await gen.generate_book_details_constraints(dataset={"books": SAMPLE_BOOKS})

    assert result == [{"field": "author", "operator": ComparisonOperator.EQUALS, "value": "Frank Herbert"}]


@pytest.mark.asyncio
async def test_generate_search_book_constraints_uses_dataset_choices(monkeypatch):
    choices = iter(["not_equals", "Dune"])
    monkeypatch.setattr(gen, "choice", lambda seq: next(choices))

    result = await gen.generate_search_book_constraints(dataset={"books": SAMPLE_BOOKS})

    assert result == [{"field": "query", "operator": ComparisonOperator.NOT_EQUALS, "value": "Dune"}]


@pytest.mark.asyncio
async def test_generate_search_book_constraints_returns_none_without_books():
    assert await gen.generate_search_book_constraints(dataset={"books": []}) is None


@pytest.mark.asyncio
async def test_generate_view_author_constraints_from_dataset():
    result = await gen.generate_view_author_constraints(dataset={"books": SAMPLE_BOOKS})
    assert len(result) == 1
    assert result[0]["field"] == "author_name"
    assert result[0]["value"] in {"Frank Herbert", "Stephen King"}
    assert isinstance(result[0]["operator"], ComparisonOperator)


@pytest.mark.asyncio
async def test_generate_view_author_constraints_empty_when_no_authors():
    assert await gen.generate_view_author_constraints(dataset={"books": []}) == []
    assert await gen.generate_view_author_constraints(dataset={"books": [{"name": "No Author"}]}) == []


@pytest.mark.asyncio
async def test_generate_book_filter_constraints_builds_genre_and_year(monkeypatch):
    choices = iter(["genre_and_year", "Sci-Fi", ComparisonOperator.LESS_EQUAL, 1986])
    monkeypatch.setattr(gen, "choice", lambda seq: next(choices))

    result = await gen.generate_book_filter_constraints(dataset={"books": SAMPLE_BOOKS})

    assert result == [
        {"field": "genres", "operator": ComparisonOperator.EQUALS, "value": "Sci-Fi"},
        {"field": "year", "operator": ComparisonOperator.LESS_EQUAL, "value": 1986},
    ]


@pytest.mark.asyncio
async def test_generate_book_filter_constraints_single_year(monkeypatch):
    choices = iter(["single_year", ComparisonOperator.GREATER_EQUAL, 1965])
    monkeypatch.setattr(gen, "choice", lambda seq: next(choices))

    result = await gen.generate_book_filter_constraints(dataset={"books": SAMPLE_BOOKS})

    assert result == [{"field": "year", "operator": ComparisonOperator.GREATER_EQUAL, "value": 1965}]


def test_generate_contact_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    result = gen.generate_contact_constraints()

    assert len(result) == 2
    assert {c["field"] for c in result} <= {"name", "email", "subject", "message"}


def test_generate_string_field_constraint_not_equals_fallback():
    book = {"name": "Dune"}
    assert gen._generate_string_field_constraint(book, "name", ComparisonOperator.NOT_EQUALS, [book]) == "Other name"


def test_generate_numeric_field_constraint_not_equals_fallback(monkeypatch):
    monkeypatch.setattr(gen.random, "random", lambda: 0.8)
    assert gen._generate_numeric_field_constraint({"year": 2000}, "year", ComparisonOperator.NOT_EQUALS, [{"year": 2000}]) == 2001


def test_generate_numeric_field_constraint_list_operators(monkeypatch):
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    dataset = [{"year": 1965}, {"year": 1986}, {"year": 2001}]
    assert gen._generate_numeric_field_constraint({"year": 1986}, "year", ComparisonOperator.IN_LIST, dataset)[0] == 1986
    assert 1986 not in gen._generate_numeric_field_constraint({"year": 1986}, "year", ComparisonOperator.NOT_IN_LIST, dataset)


def test_generate_rating_field_constraint_not_in_list_fallback():
    result = gen._generate_rating_field_constraint({"rating": 4.9}, ComparisonOperator.NOT_IN_LIST, [{"rating": 4.9}])
    assert result == [5, 5]


def test_generate_rating_field_constraint_in_list(monkeypatch):
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    result = gen._generate_rating_field_constraint({"rating": 4.8}, ComparisonOperator.IN_LIST, SAMPLE_BOOKS)
    assert result[0] == 4.8


def test_generate_genre_field_constraint_returns_non_existent_when_pool_empty():
    result = gen._generate_genre_field_constraint({"genres": ["Drama"]}, ComparisonOperator.NOT_CONTAINS, [{"genres": ["Drama"]}])
    assert result == "Non-existent genre"


def test_generate_constraint_from_solution_returns_none_when_validation_fails(monkeypatch):
    monkeypatch.setattr(gen, "validate_criterion", lambda value, criterion: False)

    result = gen.generate_constraint_from_solution(SAMPLE_BOOKS[0], "year", ComparisonOperator.EQUALS, SAMPLE_BOOKS)

    assert result is None


def test_generate_constraint_from_solution_returns_constraint_when_valid(monkeypatch):
    monkeypatch.setattr(gen, "validate_criterion", lambda value, criterion: True)
    result = gen.generate_constraint_from_solution(SAMPLE_BOOKS[0], "name", ComparisonOperator.EQUALS, SAMPLE_BOOKS)
    assert result == {"field": "name", "operator": ComparisonOperator.EQUALS, "value": "Dune"}


@pytest.mark.asyncio
async def test_generate_add_comment_constraints(monkeypatch):
    monkeypatch.setattr(gen, "sample", lambda seq, k: ["book_name", "content"])
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])

    result = await gen.generate_add_comment_constraints(dataset={"books": SAMPLE_BOOKS})

    assert {c["field"] for c in result} == {"book_name", "content"}


@pytest.mark.asyncio
async def test_generate_edit_book_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "sample", lambda seq, k: seq[:k])
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "randint", lambda a, b: a)

    result = await gen.generate_edit_book_constraints(dataset={"books": SAMPLE_BOOKS})

    fields = [c["field"] for c in result]
    assert fields[:2] == ["username", "password"]
    assert len(result) == 4


@pytest.mark.asyncio
async def test_generate_add_book_constraints_covers_all_field_kinds(monkeypatch):
    monkeypatch.setattr(gen, "sample", lambda seq, k: ["author", "year", "genres", "rating"])
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "randint", lambda a, b: a + 1)
    monkeypatch.setattr(gen, "uniform", lambda a, b: 4.26)

    result = await gen.generate_add_book_constraints(dataset={"books": SAMPLE_BOOKS})

    assert [c["field"] for c in result] == ["username", "password", "author", "year", "genres", "rating"]
    assert result[-1]["value"] == 4.3


def test_generate_edit_profile_field_constraint_returns_none_for_unknown_field():
    result = gen._generate_edit_profile_field_constraint("unknown", [], [], [], [], [], [])
    assert result is None


def test_generate_edit_profile_field_constraint_supported_fields(monkeypatch):
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
    assert gen._generate_edit_profile_field_constraint("first_name", ["John"], ["jo"], [], [], [], [])["value"] == "jo"
    assert gen._generate_edit_profile_field_constraint("bio", [], ["bio"], ["Long bio"], [], [], [])["value"] == "Long bio"
    assert gen._generate_edit_profile_field_constraint("website", [], ["web"], [], [], ["https://x.com"], [])["value"] == "web"


@pytest.mark.asyncio
async def test_generate_edit_profile_constraints_always_adds_website(monkeypatch):
    monkeypatch.setattr(gen, "sample", lambda seq, k: ["first_name"])
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])

    result = await gen.generate_edit_profile_constraints(dataset={"books": SAMPLE_BOOKS})

    fields = [c["field"] for c in result]
    assert fields[:2] == ["username", "password"]
    assert "first_name" in fields
    assert "website" in fields
