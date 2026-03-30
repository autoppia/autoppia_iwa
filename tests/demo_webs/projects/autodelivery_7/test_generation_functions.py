"""Tests for autodelivery generation_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p07_autodelivery import generation_functions as gen

RESTAURANTS = [
    {
        "name": "Pizza Hub",
        "cuisine": "Italian",
        "rating": 4.6,
        "description": "Great pizza and pasta",
        "menu": [{"name": "Margherita", "price": 12.5, "size": "medium"}],
        "reviews": [{"rating": 5, "author": "Ana", "date": "2026-01-01", "comment": "Excellent"}],
    },
    {
        "name": "Sushi Bar",
        "cuisine": "Japanese",
        "rating": 4.1,
        "description": "Fresh sushi",
        "menu": [{"name": "Salmon Roll", "price": 10.0, "size": "small"}],
        "reviews": [{"rating": 4, "author": "Luis", "date": "2026-01-02", "comment": "Nice"}],
    },
]


def test_extract_entity_dataset_supports_list_and_dict():
    assert gen._extract_entity_dataset(RESTAURANTS, "restaurants") == RESTAURANTS
    assert gen._extract_entity_dataset({"restaurants": RESTAURANTS}, "restaurants") == RESTAURANTS


@pytest.mark.asyncio
async def test_ensure_restaurant_dataset_fetches(monkeypatch):
    fetch = AsyncMock(return_value=RESTAURANTS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    result = await gen._ensure_restaurant_dataset("http://localhost:8000/?seed=3", None)

    assert result == RESTAURANTS
    fetch.assert_awaited_once_with(seed_value=3)


def test_generate_constraint_value_covers_string_list_and_rating(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 0.5)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "shuffle", lambda seq: None)

    assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Pizza Hub", "name", RESTAURANTS) == "Sushi Bar"
    assert gen._generate_constraint_value(ComparisonOperator.CONTAINS, "Pizza Hub", "name", RESTAURANTS) in "Pizza Hub"
    assert "Pizza Hub" in gen._generate_constraint_value(ComparisonOperator.IN_LIST, "Pizza Hub", "name", RESTAURANTS)
    assert isinstance(gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 4.6, "rating", RESTAURANTS), float)


@pytest.mark.asyncio
async def test_search_and_view_restaurant_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    search = await gen.generate_search_restaurant_constraints(dataset=RESTAURANTS)
    view = await gen.generate_view_restaurant_constraints(dataset=RESTAURANTS)

    assert search[0]["field"] == "query"
    assert view


@pytest.mark.asyncio
async def test_menu_item_helpers(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)

    all_items = await gen._get_menu_items(dataset=RESTAURANTS)
    restaurant_items = gen._get_menu_items_for_restaurant(RESTAURANTS[0])

    assert all_items
    assert restaurant_items[0]["restaurant"] == "Pizza Hub"


@pytest.mark.asyncio
async def test_add_to_cart_modal_and_increment_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    modal = await gen.generate_add_to_cart_modal_open_constraints(dataset=RESTAURANTS)
    increment = await gen.generate_increment_item_restaurant_constraints(dataset=RESTAURANTS)

    assert modal
    assert any(c["field"] == "quantity" for c in increment)


def test_get_new_quantity_value_is_bounded(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    assert 2 <= gen._get_new_quantity_value(ComparisonOperator.EQUALS) <= 10
    assert 2 <= gen._get_new_quantity_value(ComparisonOperator.NOT_EQUALS) <= 10


@pytest.mark.asyncio
async def test_review_cart_and_dropoff_generators(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    delete_review = await gen.generate_delete_review_constraints(dataset=RESTAURANTS)
    add_to_cart = await gen.generate_add_to_cart_constraints(dataset=RESTAURANTS)
    dropoff = await gen.generate_dropoff_option_constraints(dataset=RESTAURANTS)

    assert delete_review
    assert add_to_cart
    assert any(c["field"] == "delivery_preference" for c in dropoff)


def test_address_dataset_helper():
    assert len(gen._get_address_dataset()) == len(gen.ADDRESSES)


@pytest.mark.asyncio
async def test_address_place_order_and_filters(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen, "generate_add_to_cart_constraints", AsyncMock(return_value=[{"field": "item", "operator": ComparisonOperator.EQUALS, "value": "Margherita"}]))

    address = await gen.generate_address_added_constraints(dataset=RESTAURANTS)
    place_order = await gen.generate_place_order_constraints()
    restaurant_filter = await gen.generate_restaurant_filter_constraints(dataset=RESTAURANTS)

    assert address
    assert place_order
    assert restaurant_filter


@pytest.mark.asyncio
async def test_quick_reorder_edit_review_and_priority(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen, "generate_add_to_cart_constraints", AsyncMock(return_value=[{"field": "item", "operator": ComparisonOperator.EQUALS, "value": "Margherita"}]))

    quick = await gen.generate_quick_reorder_constraints(dataset=RESTAURANTS)
    edit = await gen.generate_edit_cart_item_constraints(dataset=RESTAURANTS)
    review = await gen.generate_review_submitted_constraints(dataset=RESTAURANTS)
    priority = await gen.generate_delivery_priority_constraints(dataset=RESTAURANTS)

    assert quick
    assert edit
    assert review
    assert any(c["field"] == "priority" for c in priority)
