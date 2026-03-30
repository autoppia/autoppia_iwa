"""Tests for autozone generation_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p03_autozone import generation_functions as gen

PRODUCTS = [
    {
        "id": "p1",
        "title": "Ultra Laptop",
        "category": "Technology",
        "brand": "Autoppia",
        "rating": 4.7,
        "price": "$199.99",
        "quantity": 3,
        "items": 2,
        "total_items": 2,
        "total_amount": "$199.99",
    },
    {
        "id": "p2",
        "title": "Kitchen Pro",
        "category": "Kitchen",
        "brand": "Chef",
        "rating": 3.9,
        "price": "$99.50",
        "quantity": 5,
        "items": 1,
        "total_items": 1,
        "total_amount": "$99.50",
    },
]


@pytest.mark.asyncio
async def test_ensure_products_dataset_fetches_when_missing(monkeypatch):
    fetch = AsyncMock(return_value=PRODUCTS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    result = await gen._ensure_products_dataset("http://localhost:8000/?seed=7", None)

    assert result == PRODUCTS
    fetch.assert_awaited_once_with(seed_value=7)


@pytest.mark.asyncio
async def test_ensure_products_dataset_returns_empty_when_products_key_missing():
    assert await gen._ensure_products_dataset(dataset={"other": []}) == []


def test_generate_constraint_value_equals_for_price_parses_source():
    result = gen.generate_constraint_value("price", ComparisonOperator.EQUALS, PRODUCTS[0], all_products_data=PRODUCTS)
    assert result == 199.99


def test_generate_constraint_value_not_equals_returns_other_value(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    result = gen.generate_constraint_value("brand", ComparisonOperator.NOT_EQUALS, PRODUCTS[0], all_products_data=PRODUCTS)
    assert result == "Chef"


def test_generate_constraint_value_quantity_comparison_rounds_to_int(monkeypatch):
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 0.6)
    result = gen.generate_constraint_value("quantity", ComparisonOperator.GREATER_THAN, PRODUCTS[0], all_products_data=PRODUCTS)
    assert isinstance(result, int)
    assert result >= 1


def test_generate_constraint_value_contains_uses_substring(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    result = gen.generate_constraint_value("title", ComparisonOperator.CONTAINS, PRODUCTS[0], all_products_data=PRODUCTS)
    assert result in PRODUCTS[0]["title"]


def test_generate_constraint_value_not_contains_appends_suffix(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 123)
    result = gen.generate_constraint_value("category", ComparisonOperator.NOT_CONTAINS, PRODUCTS[0], all_products_data=PRODUCTS)
    assert result.endswith("XYZ123")


def test_generate_constraint_value_in_list_includes_source(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "shuffle", lambda seq: None)
    result = gen.generate_constraint_value("brand", ComparisonOperator.IN_LIST, PRODUCTS[0], all_products_data=PRODUCTS)
    assert PRODUCTS[0]["brand"] in result


def test_generate_constraint_value_returns_none_without_all_products():
    assert gen.generate_constraint_value("title", ComparisonOperator.EQUALS, PRODUCTS[0], all_products_data=None) is None


@pytest.mark.asyncio
async def test_generate_autozone_products_constraints_builds_selected_fields(monkeypatch):
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: ["title", "price"])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    result = await gen.generate_autozone_products_constraints(dataset={"products": PRODUCTS})

    assert [c["field"] for c in result] == ["title", "price"]


@pytest.mark.asyncio
async def test_generate_search_query_constraints_falls_back_without_products():
    result = await gen.generate_search_query_constraints(dataset={"products": []})
    assert result == [{"field": "query", "operator": ComparisonOperator.CONTAINS, "value": "products"}]


@pytest.mark.asyncio
async def test_generate_search_query_constraints_falls_back_when_value_generation_returns_none(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "generate_constraint_value", lambda *args, **kwargs: None)

    result = await gen.generate_search_query_constraints(dataset={"products": PRODUCTS})

    assert result == [{"field": "query", "operator": ComparisonOperator.CONTAINS, "value": "products"}]


@pytest.mark.asyncio
async def test_generate_quantity_change_constraints_adds_title_and_quantity(monkeypatch):
    choices = iter([PRODUCTS[0], ComparisonOperator.EQUALS, ComparisonOperator.EQUALS])
    monkeypatch.setattr(gen.random, "choice", lambda seq: next(choices))
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 4)

    result = await gen.generate_quantity_change_constraints(dataset={"products": PRODUCTS})

    assert [c["field"] for c in result] == ["title", "new_quantity"]
    assert result[1]["value"] == 4


@pytest.mark.asyncio
async def test_generate_checkout_constraints_handles_invalid_product(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: {"bad": "row"})
    assert await gen.generate_checkout_constraints(dataset={"products": PRODUCTS}) == []


@pytest.mark.asyncio
async def test_generate_order_completed_constraints_uses_title_and_quantity(monkeypatch):
    choices = iter([PRODUCTS[0], ComparisonOperator.EQUALS, ComparisonOperator.EQUALS])
    monkeypatch.setattr(gen.random, "choice", lambda seq: next(choices))

    result = await gen.generate_order_completed_constraints(dataset={"products": PRODUCTS})

    assert [c["field"] for c in result] == ["title", "quantity"]


def test_generate_carousel_scroll_constraints_always_includes_direction(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    result = gen.generate_carousel_scroll_constraints()

    assert any(c["field"] == "direction" for c in result)


@pytest.mark.asyncio
async def test_generate_category_filter_constraints_falls_back_to_all(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    result = await gen.generate_category_filter_constraints(dataset={"products": [{"category": "unknown"}]})
    assert result == [{"field": "category", "operator": ComparisonOperator.EQUALS, "value": "all"}]
