"""Tests for autolodge generation_functions."""

from __future__ import annotations

import datetime
from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p08_autolodge import generation_functions as gen

HOTELS = [
    {
        "id": 1,
        "title": "Lake House",
        "location": "Scotland",
        "amenities": ["wifi", "parking"],
        "guests": 2,
        "maxGuests": 4,
        "datesFrom": datetime.datetime(2026, 4, 1),
        "datesTo": datetime.datetime(2026, 4, 5),
        "price": 100,
        "host_name": "Emily",
    },
    {
        "id": 2,
        "title": "City Loft",
        "location": "France",
        "amenities": ["pool"],
        "guests": 1,
        "maxGuests": 2,
        "datesFrom": datetime.datetime(2026, 5, 1),
        "datesTo": datetime.datetime(2026, 5, 8),
        "price": 120,
        "host_name": "John",
    },
]


def test_dataset_helpers_and_date_pair(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    assert set(gen._collect_field_values_from_dataset_flat(HOTELS, "amenities")) == {"wifi", "parking", "pool"}
    assert gen._pick_different_value_from_dataset(HOTELS, "title", "Lake House") == "City Loft"
    fields = ["datesFrom"]
    gen._ensure_dates_pair_in_selected(fields)
    assert fields == ["datesFrom", "datesTo"]


@pytest.mark.asyncio
async def test_ensure_hotel_dataset_fetches_or_returns_list(monkeypatch):
    fetch = AsyncMock(return_value=HOTELS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    fetched = await gen._ensure_hotel_dataset("http://localhost:8000/?seed=6", None)
    direct = await gen._ensure_hotel_dataset(dataset=HOTELS)

    assert fetched == HOTELS
    assert direct == HOTELS
    fetch.assert_awaited_once_with(seed_value=6)


def test_generate_constraint_value_handles_datetime_strings_lists_and_numeric(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 0.5)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "shuffle", lambda seq: None)

    dt = HOTELS[0]["datesFrom"]
    assert gen._generate_constraint_value(ComparisonOperator.LESS_THAN, dt, "datesFrom", HOTELS) > dt
    assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Lake House", "title", HOTELS) == "City Loft"
    assert "wifi" in gen._generate_constraint_value(ComparisonOperator.IN_LIST, "wifi", "amenities", HOTELS)
    assert isinstance(gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 4, "guests", HOTELS), int)


@pytest.mark.asyncio
async def test_search_hotel_constraints_generates_supported_fields(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: ["search_term"])
    monkeypatch.setattr(gen, "_generate_constraint_value", lambda operator, field_value, field, dataset: field_value)

    result = await gen.generate_search_hotel_constraints(dataset=HOTELS)

    assert result
    assert result[0]["field"] == "search_term"


def test_generate_num_of_guests_field_value_is_bounded(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    assert gen._generate_num_of_guests_field_value(ComparisonOperator.EQUALS, 2, 4) == 2
    assert 1 <= gen._generate_num_of_guests_field_value(ComparisonOperator.NOT_EQUALS, 2, 4) <= 4


@pytest.mark.asyncio
async def test_view_and_reserve_hotel_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    view = await gen.generate_view_hotel_constraints(dataset=HOTELS)
    reserve = await gen.generate_reserve_hotel_constraints(dataset=HOTELS)

    assert view
    assert reserve


@pytest.mark.asyncio
async def test_edit_guests_and_checkin_checkout_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a + 1 if a < b else a)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    guests = await gen.generate_edit_guests_constraints(dataset=HOTELS)
    dates = await gen.generate_edit_checkin_checkout_constraints(dataset=HOTELS)

    assert guests
    assert any(c["field"] == "checkin" for c in dates)
    assert any(c["field"] == "checkout" for c in dates)


@pytest.mark.asyncio
async def test_confirm_pay_message_share_and_filters(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    confirm = await gen.generate_confirm_and_pay_constraints(dataset=HOTELS)
    message = await gen.generate_message_host_constraints(dataset=HOTELS)
    share = await gen.generate_share_hotel_constraints(dataset=HOTELS)
    filters = await gen.generate_apply_filter_constraints(dataset=HOTELS)

    assert confirm
    assert message
    assert share
    assert len(filters) == 2


@pytest.mark.asyncio
async def test_review_and_payment_method_generators(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    review = await gen.generate_submit_hotel_review_constraints(dataset=HOTELS)
    payment = await gen.generate_payment_method_selected_constraints(dataset=HOTELS)

    assert review
    assert payment
