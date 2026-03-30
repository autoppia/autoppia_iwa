"""Tests for autodining generation_functions."""

from __future__ import annotations

import datetime
from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p04_autodining import generation_functions as gen

RESTAURANTS = [
    {"name": "Casa Mia", "desc": "Italian comfort food", "rating": 4.4, "reviews": 120, "cuisine": "Italian", "bookings": 12},
    {"name": "Sakura", "desc": "Japanese omakase", "rating": 4.8, "reviews": 75, "cuisine": "Japanese", "bookings": 8},
]


@pytest.mark.asyncio
async def test_get_restaurants_dataset_fetches_when_missing(monkeypatch):
    fetch = AsyncMock(return_value=RESTAURANTS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    result = await gen._get_restaurants_dataset("http://localhost:8000/?seed=9", None)

    assert result == RESTAURANTS
    fetch.assert_awaited_once_with(seed_value=9)


def test_pick_different_from_list_handles_plain_and_dict_options(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    assert gen._pick_different_from_list("A", ["A", "B"]) == "B"
    assert gen._pick_different_from_list("US", [{"code": "US"}, {"code": "ES"}], "code") == "ES"


def test_collect_field_values_from_dataset_is_unique():
    result = gen._collect_field_values_from_dataset([{"name": "A"}, {"name": "A"}, {"name": "B"}], "name")
    assert set(result) == {"A", "B"}


def test_generate_constraint_value_not_equals_uses_dataset_value(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    result = gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Casa Mia", "name", RESTAURANTS)
    assert result == "Sakura"


def test_generate_constraint_value_contains_and_not_contains_for_strings(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    contains = gen._generate_constraint_value(ComparisonOperator.CONTAINS, "Italian comfort food", "desc", RESTAURANTS)
    not_contains = gen._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "hello", "message", gen.CONTACT_MESSAGES)
    assert contains in "Italian comfort food"
    assert not_contains in gen.CONTACT_MESSAGES and "hello" not in not_contains


def test_generate_constraint_value_in_list_and_not_in_list():
    in_list = gen._generate_constraint_value(ComparisonOperator.IN_LIST, "Italian", "cuisine", RESTAURANTS)
    not_in_list = gen._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Italian", "cuisine", RESTAURANTS)
    assert "Italian" in in_list
    assert "Italian" not in not_in_list


def test_generate_constraint_value_numeric_special_case_and_datetime_paths(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 1.5)
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)

    numeric = gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 4.0, "rating", RESTAURANTS)
    base_date = datetime.datetime(2026, 4, 1, 19, 0, tzinfo=datetime.UTC)
    dated = gen._generate_constraint_value(ComparisonOperator.LESS_THAN, base_date, "date", [{"date": base_date}])

    assert numeric == 2
    assert dated > base_date


@pytest.mark.asyncio
async def test_generate_value_for_field_covers_query_name_and_defaults(monkeypatch):
    monkeypatch.setattr(gen, "_get_restaurant_queries", AsyncMock(return_value=["pizza"]))
    monkeypatch.setattr(gen, "fetch_data", AsyncMock(return_value=RESTAURANTS))
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    assert await gen._generate_value_for_field("query") == "pizza"
    assert await gen._generate_value_for_field("name") == "Casa Mia"
    assert await gen._generate_value_for_field("unknown_field") == "mock_value"


@pytest.mark.asyncio
async def test_generate_constraints_for_single_field_serializes_datetime(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "_generate_value_for_field", AsyncMock(return_value=datetime.datetime(2026, 4, 1, tzinfo=datetime.UTC)))

    result = await gen.generate_constraints_for_single_field("date", {"date": [ComparisonOperator.EQUALS]})

    assert result[0]["field"] == "date"
    assert isinstance(result[0]["value"], str)


@pytest.mark.asyncio
async def test_generate_constraints_for_fields_respects_required_and_date_bounds(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen, "_generate_value_for_field", AsyncMock(return_value=max(gen.MOCK_DATES) + datetime.timedelta(days=30)))

    result = await gen._generate_constraints_for_fields(
        all_fields=["date", "time"],
        allowed_ops={"date": [ComparisonOperator.EQUALS], "time": [ComparisonOperator.EQUALS]},
        required_fields=["date"],
        max_optional=1,
        validate_dates=True,
        dataset=RESTAURANTS,
    )

    assert result[0]["field"] == "date"
    assert result[0]["value"] <= max(gen.MOCK_DATES).isoformat()


@pytest.mark.asyncio
async def test_generate_contact_constraints_returns_empty_on_missing_value(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: ["username"])
    monkeypatch.setattr(gen, "_generate_value_for_field", AsyncMock(return_value="Alice"))
    monkeypatch.setattr(gen, "_generate_constraint_value", lambda *args, **kwargs: None)

    assert await gen.generate_contact_constraints() == []


@pytest.mark.asyncio
async def test_generate_contact_constraints_builds_fields(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: ["username", "email"])
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "_generate_value_for_field", AsyncMock(side_effect=["Alice", "alice@example.com"]))
    monkeypatch.setattr(gen, "_generate_constraint_value", lambda op, default_value, field, dataset: default_value)

    result = await gen.generate_contact_constraints()

    assert [c["field"] for c in result] == ["username", "email"]


def test_generate_restaurant_constraints_validates_inputs_and_generates_values(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    with pytest.raises(ValueError):
        gen.generate_restaurant_constraints(dataset=[], fields=["name"], allowed_ops={"name": [ComparisonOperator.EQUALS]})

    result = gen.generate_restaurant_constraints(
        dataset={"restaurants": RESTAURANTS},
        fields=["name", "rating"],
        allowed_ops={"name": [ComparisonOperator.EQUALS], "rating": [ComparisonOperator.GREATER_THAN]},
        max_constraints=2,
    )

    assert len(result) == 1
    assert result[0]["field"] == "name"


@pytest.mark.asyncio
async def test_book_restaurant_and_country_selected_include_booking_fields(monkeypatch):
    monkeypatch.setattr(gen, "_get_restaurants_dataset", AsyncMock(return_value=RESTAURANTS))
    monkeypatch.setattr(gen, "generate_restaurant_constraints", lambda **kwargs: [{"field": "name", "operator": ComparisonOperator.EQUALS, "value": "Casa Mia"}])
    monkeypatch.setattr(
        gen,
        "_generate_constraints_for_fields",
        AsyncMock(return_value=[{"field": "people", "operator": ComparisonOperator.EQUALS, "value": 2}]),
    )
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    booked = await gen.generate_book_restaurant_constraints(dataset=RESTAURANTS)
    country = await gen.generate_country_selected_constraints(dataset=RESTAURANTS)

    assert [c["field"] for c in booked] == ["name", "people"]
    assert [c["field"] for c in country] == ["name", "people"]


@pytest.mark.asyncio
async def test_single_field_helpers_are_wired(monkeypatch):
    monkeypatch.setattr(gen, "generate_constraints_for_single_field", AsyncMock(return_value=[{"field": "feature", "operator": ComparisonOperator.EQUALS, "value": "Fast booking"}]))

    assert await gen.generate_about_feature_click_constraints()
    assert await gen.generate_help_category_selected_constraints()
    assert await gen.generate_help_faq_toggled_constraints()
    assert await gen.generate_contact_card_click_constraints()
