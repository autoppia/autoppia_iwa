from __future__ import annotations

from datetime import date, datetime, time

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p11_autocalendar import generation_functions as gf

EVENTS = [
    {"label": "Sprint Planning", "date": "2026-04-10T09:00:00.000Z", "calendar": "Work"},
    {"label": "Doctor Visit", "date": "2026-04-11T11:00:00.000Z", "calendar": "Personal"},
]


@pytest.fixture
def deterministic_random(monkeypatch: pytest.MonkeyPatch) -> None:
    def _choice(seq):
        if isinstance(seq, str):
            return seq[-1]
        seq_list = list(seq)
        return seq_list[0]

    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)


@pytest.fixture
def patched_events(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_events(task_url=None, dataset=None):
        return EVENTS

    monkeypatch.setattr(gf, "_ensure_event_dataset", _fake_events)


def test_generate_constraint_value_for_strings_dates_times_and_numbers(deterministic_random):
    dataset = [{"value": "Sprint Planning", "count": 4}, {"value": "Doctor Visit", "count": 8}]
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Sprint Planning", "value", dataset) == "Sprint Planning"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Sprint Planning", "value", dataset)
    assert contains_value in "Sprint Planning"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Sprint Planning", "value", dataset) == "Doctor Visit"
    assert gf._generate_constraint_value(ComparisonOperator.LESS_EQUAL, 4, "count", dataset) == 4
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, date(2026, 4, 10), "day", [{"day": date(2026, 4, 10)}]) == date(2026, 4, 10)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, time(9, 0), "start_time", [{"start_time": time(9, 0)}]) == time(9, 0)
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, datetime(2026, 4, 10), "at", [{"at": datetime(2026, 4, 10)}]) == datetime(2026, 4, 10)


def test_generate_constraints_from_single_field_and_create_calendar(deterministic_random):
    search_constraints = gf.generate_search_submit_constraints()
    reminder_constraints = gf.generate_event_reminder_constraints()
    attendee_constraints = gf.generate_event_attendee_constraints()
    calendar_constraints = gf.generate_create_calendar_constraints()
    unselect_constraints = gf.generate_unselect_calendar_constraints()
    assert search_constraints[0]["field"] == "query"
    assert reminder_constraints[0]["field"] == "minutes"
    assert attendee_constraints[0]["field"] == "email"
    assert {c["field"] for c in calendar_constraints} == {"name", "description"}
    assert unselect_constraints[0]["field"] == "calendar_name"


def test_generate_constraints_for_event_uses_special_handlers(deterministic_random):
    field_map = {
        "title": {"values": ["Sprint Planning"]},
        "time": {},
    }
    constraints = gf._generate_constraints_for_event(field_map, gf.FIELD_OPERATORS_ADD_EVENT_MAP, {"time": gf._handle_time_constraints})
    assert {c["field"] for c in constraints} >= {"title", "start_time", "end_time"}


def test_handle_time_constraints_produces_consistent_range(deterministic_random):
    constraints = gf._handle_time_constraints({})
    start_constraint = next(c for c in constraints if c["field"] == "start_time")
    end_constraint = next(c for c in constraints if c["field"] == "end_time")
    assert end_constraint["value"] >= start_constraint["value"]


def test_generate_cell_clicked_constraints_month_view(deterministic_random):
    constraints = gf.generate_cell_clicked_constraints()
    assert {c["field"] for c in constraints} == {"view", "date"}


def test_generate_cell_clicked_constraints_non_month_view_includes_hour(monkeypatch: pytest.MonkeyPatch):
    original_choice = gf.random.choice

    def _choice(seq):
        seq_list = list(seq)
        if seq_list == ["Month", "Week", "Day", "5 days"]:
            return "Week"
        if isinstance(seq, str):
            return seq[-1]
        return seq_list[0]

    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)
    constraints = gf.generate_cell_clicked_constraints()
    assert {c["field"] for c in constraints} == {"view", "date", "hour"}
    monkeypatch.setattr(gf.random, "choice", original_choice)


def test_generate_add_event_constraints(deterministic_random):
    constraints = gf.generate_add_event_constraints()
    fields = {c["field"] for c in constraints}
    assert "title" in fields
    assert "date" in fields
    assert "time" not in fields or "all_day" not in fields


@pytest.mark.asyncio
async def test_generate_event_wizard_open_constraints(deterministic_random, patched_events):
    constraints = await gf.generate_event_wizard_open_constraints("http://localhost:8000/?seed=1")
    assert {c["field"] for c in constraints}


@pytest.mark.asyncio
async def test_generate_event_wizard_open_constraints_empty_dataset(monkeypatch: pytest.MonkeyPatch):
    async def _empty_events(task_url=None, dataset=None):
        return []

    monkeypatch.setattr(gf, "_ensure_event_dataset", _empty_events)
    assert await gf.generate_event_wizard_open_constraints("http://localhost:8000/?seed=1") == []
