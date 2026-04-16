from __future__ import annotations

from datetime import date, datetime

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p12_autolist import generation_functions as gf
from autoppia_iwa.src.demo_webs.projects.p12_autolist.data import PRIORITIES

TASKS = [
    {"name": "Write report", "description": "Finish quarterly report", "date": datetime(2026, 4, 1), "priority": "high"},
    {"name": "Plan roadmap", "description": "Plan product roadmap", "date": datetime(2026, 4, 2), "priority": "medium"},
]


@pytest.fixture
def deterministic_random(monkeypatch: pytest.MonkeyPatch) -> None:
    def _choice(seq):
        if isinstance(seq, str):
            return seq[-1]
        return next(iter(seq))

    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "shuffle", lambda population: None)
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)
    monkeypatch.setattr(gf.random, "uniform", lambda a, b: b)


@pytest.fixture
def patched_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_fetch_data(seed_value=None):
        return TASKS

    monkeypatch.setattr(gf, "fetch_data", _fake_fetch_data)


@pytest.mark.asyncio
async def test_ensure_task_dataset_uses_dataset_or_fetches(patched_tasks):
    assert await gf._ensure_task_dataset("http://localhost", {"tasks": TASKS}) == TASKS
    assert await gf._ensure_task_dataset("http://localhost/?seed=1", None) == TASKS


def test_task_priority_to_label():
    assert gf._task_priority_to_label(1) == "Highest"
    assert gf._task_priority_to_label(4) == "Low"
    assert gf._task_priority_to_label("3") == "Medium"
    assert gf._task_priority_to_label("High") == "High"
    assert gf._task_priority_to_label("high") == "High"
    assert gf._task_priority_to_label(99) is None


def test_collection_and_pick_helpers():
    dataset = [{"priority": "high"}, {"priority": "high"}, {"priority": "medium"}, {"priority": None}]
    assert set(gf._collect_field_values_from_dataset_flat(dataset, "priority")) == {"high", "medium"}
    assert gf._pick_different_value_from_dataset(dataset, "priority", "high") == "medium"
    assert gf._pick_different_value_from_dataset([{"priority": "high"}], "priority", "high", "fallback") == "fallback"


def test_generate_constraint_value_for_core_types(deterministic_random):
    dataset = [{"priority": "high", "score": 5}, {"priority": "medium", "score": 8}]
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "high", "priority", dataset) == "high"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "high", "priority", dataset) == "medium"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "high priority", "priority", dataset)
    assert isinstance(contains_value, str)
    assert contains_value in "priority"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "high", "priority", dataset) == "zzz"
    assert set(gf._generate_constraint_value(ComparisonOperator.IN_LIST, "high", "priority", dataset)) == {"high", "medium"}
    assert gf._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "high", "priority", dataset) == ["medium"]
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 5, "score", dataset) < 5
    assert gf._generate_constraint_value(ComparisonOperator.LESS_EQUAL, 5, "score", dataset) == 5
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, date(2026, 4, 1), "date", [{"date": date(2026, 4, 1)}]) == date(2026, 4, 1)


def test_generate_constraints_for_event(deterministic_random):
    field_map = {
        "_dataset": TASKS,
        "name": {"dataset": TASKS},
        "priority": {"dataset": ["high", "medium"]},
    }
    constraints = gf._generate_constraints_for_event(field_map, {"name": ["equals"], "priority": ["equals"]})
    assert {c["field"] for c in constraints} == {"name", "priority"}


@pytest.mark.asyncio
async def test_generate_select_date_for_task_constraints(deterministic_random, patched_tasks):
    date_constraints = await gf.generate_select_date_for_task_constraints("http://localhost/?seed=1")
    assert date_constraints[0]["field"] in {"date", "quick_option"}


def test_generate_select_task_priority_constraints(deterministic_random):
    constraints = gf.generate_select_task_priority_constraints()
    assert constraints[0]["field"] == "priority"


@pytest.mark.asyncio
async def test_generate_task_constraints(deterministic_random, patched_tasks):
    constraints = await gf.generate_task_constraints("http://localhost/?seed=1")
    assert {c["field"] for c in constraints} >= {"name", "description", "priority"}
    priority_c = next(c for c in constraints if c["field"] == "priority")
    assert priority_c["value"] in PRIORITIES


def test_generate_constraints_maps_numeric_task_priority_to_label():
    field_map = {
        "_dataset": [{"name": "N", "description": "D", "date": datetime(2026, 4, 1), "priority": 2}],
        "priority": {"dataset": PRIORITIES},
    }
    constraints = gf._generate_constraints_for_event(field_map, {"priority": ["equals"]})
    assert len(constraints) == 1
    assert constraints[0]["field"] == "priority"
    assert constraints[0]["value"] == "High"


def test_generate_team_members_added_constraints(deterministic_random):
    constraints = gf.generate_team_members_added_constraints()
    assert {c["field"] for c in constraints} == {"members", "member_count"}


def test_generate_team_role_assigned_and_team_created_constraints(deterministic_random):
    role_constraints = gf.generate_team_role_assigned_constraints()
    created_constraints = gf.generate_team_created_constraints()
    assert {c["field"] for c in role_constraints} == {"member", "role"}
    assert {c["field"] for c in created_constraints} >= {"name", "description", "member", "role"}
