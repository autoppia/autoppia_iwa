from __future__ import annotations

from datetime import UTC, date, datetime, time

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p13_autodrive import generation_functions as gf

PLACES = [
    {"label": "Madrid - Barajas Airport"},
    {"label": "Atocha Station"},
]

RIDES = [
    {"name": "Standard"},
    {"name": "Comfort"},
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
    monkeypatch.setattr(gf, "randint", lambda a, b: b)
    monkeypatch.setattr(gf, "randrange", lambda start, stop=None, step=1: start)


@pytest.fixture
def patched_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_get_drive_entity_list(task_url, dataset, entity_type, *, method=None):
        mapping = {
            "places": PLACES,
            "rides": RIDES,
        }
        return mapping[entity_type]

    monkeypatch.setattr(gf, "_get_drive_entity_list", _fake_get_drive_entity_list)


def test_normalize_contain_value():
    assert gf.normalize_contain_value("Madrid - Barajas Airport") == "Barajas Airport"
    assert gf.normalize_contain_value("Atocha Station") == "Atocha Station"
    assert gf.normalize_contain_value("") == ""


def test_collect_and_constraint_value_helpers(deterministic_random):
    dataset = [{"label": "Madrid - Barajas Airport", "price": 12}, {"label": "Atocha Station", "price": 20}]
    assert set(gf._collect_field_values_from_dataset(dataset, "label")) == {"Madrid - Barajas Airport", "Atocha Station"}
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Madrid", "label", dataset) == "Madrid"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Madrid - Barajas Airport", "label", dataset) == "Atocha Station"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Madrid - Barajas Airport", "label", dataset)
    assert isinstance(contains_value, str)
    assert contains_value
    assert gf._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "Madrid", "label", dataset) == "zzz"
    assert set(gf._generate_constraint_value(ComparisonOperator.IN_LIST, "Madrid - Barajas Airport", "label", dataset)) == {"Madrid - Barajas Airport", "Atocha Station"}
    assert gf._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Madrid - Barajas Airport", "label", dataset) == ["Atocha Station"]
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 12, "price", dataset) < 12
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, date(2026, 4, 1), "pickup_date", [{"pickup_date": date(2026, 4, 1)}]) == date(2026, 4, 1)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, time(12, 0), "pickup_time", [{"pickup_time": time(12, 0)}]) == time(12, 0)


def test_random_datetime_and_date_helpers(deterministic_random):
    start = datetime(2026, 4, 1, 10, 0)
    end = datetime(2026, 4, 2, 10, 0)
    generated = gf.random_datetime(start=start, end=end)
    assert start <= generated <= end
    new_date, parsed = gf._random_future_date(start, min_days=1, max_days=7)
    assert new_date > start.date()
    assert gf._apply_less_than_date_guard(parsed, start) > start + gf.timedelta(days=1)


def test_build_date_time_and_now_helpers(deterministic_random):
    date_constraint = gf._build_date_constraint("date", ["equals"])
    time_constraint = gf._build_time_constraint("time", ["equals"], datetime(2026, 4, 1, 11, 15))
    future_time = gf._random_future_time_from_now(datetime(2026, 4, 1, 11, 15))
    assert date_constraint["field"] == "date"
    assert time_constraint["field"] == "time"
    assert isinstance(future_time, time)
    assert gf._now_optional_utc(True).tzinfo == UTC
    assert gf._now_optional_utc(False).tzinfo is None


def test_resolve_special_datetime_field(deterministic_random):
    datetime_result = gf._resolve_special_datetime_field({"field": "scheduled", "is_datetime": True, "days": 2})
    date_result = gf._resolve_special_datetime_field({"field": "scheduled_date", "is_date": True})
    time_result = gf._resolve_special_datetime_field({"field": "scheduled_time", "is_time": True})
    assert datetime_result is not None
    assert date_result is not None
    assert time_result is not None


def test_generate_constraints_with_custom_field_map(deterministic_random):
    constraints = gf._generate_constraints(
        PLACES,
        {"location": ["equals"], "scheduled": ["equals"]},
        field_map={
            "location": "label",
            "scheduled": {"field": "scheduled", "is_datetime": True, "days": 2},
        },
        selected_fields=["location", "scheduled"],
    )
    assert {c["field"] for c in constraints} == {"location", "scheduled"}


@pytest.mark.asyncio
async def test_generate_location_destination_and_prices(deterministic_random, patched_entities):
    location = await gf.generate_enter_location_constraints("http://localhost/?seed=1")
    destination = await gf.generate_enter_destination_constraints("http://localhost/?seed=1")
    prices = await gf.generate_see_prices_constraints("http://localhost/?seed=1")
    assert location[0]["field"] == "location"
    assert destination[0]["field"] == "destination"
    assert {c["field"] for c in prices} == {"location", "destination"}


def test_generate_date_time_and_next_pickup(deterministic_random):
    date_constraints = gf.generate_select_date_constraints()
    time_constraints = gf.generate_select_time_constraints()
    pickup_constraints = gf.generate_next_pickup_constraints()
    assert date_constraints[0]["field"] == "date"
    assert time_constraints[0]["field"] == "time"
    assert {c["field"] for c in pickup_constraints} == {"date", "time"}


def test_create_scheduled_constraint(deterministic_random):
    constraint = gf._create_scheduled_constraint("scheduled", ["equals"])
    assert constraint["field"] == "scheduled"


@pytest.mark.asyncio
async def test_generate_search_select_and_reserve_ride_constraints(deterministic_random, patched_entities):
    search = await gf.generate_search_ride_constraints("http://localhost/?seed=1")
    selected = await gf.generate_select_car_constraints("http://localhost/?seed=1", {"places": PLACES, "rides": RIDES})
    reserved = await gf.generate_reserve_ride_constraints("http://localhost/?seed=1", {"places": PLACES, "rides": RIDES})
    assert {c["field"] for c in search} >= {"location", "destination", "scheduled"}
    assert {c["field"] for c in selected} >= {"location", "destination", "ride_name", "scheduled"}
    assert reserved == selected
