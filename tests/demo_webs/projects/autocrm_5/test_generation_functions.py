"""Tests for autocrm generation_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p05_autocrm import generation_functions as gen

CLIENTS = [
    {"name": "Alice", "email": "alice@example.com", "status": "Active", "matters": 2, "last": "Today"},
    {"name": "Bob", "email": "bob@example.com", "status": "Archived", "matters": 5, "last": "Yesterday"},
]
MATTERS = [
    {"name": "Case A", "client": "Alice", "status": "Open", "updated": "2026-01-01"},
    {"name": "Case B", "client": "Bob", "status": "Closed", "updated": "2026-02-01"},
]
FILES = [
    {"name": "Report.pdf", "size": "25 KB", "version": "1.0", "status": "Ready"},
    {"name": "Invoice.docx", "size": "1.5 MB", "version": "2.0", "status": "Draft"},
]
LOGS = [
    {"matter": "Case A", "hours": 2.5, "description": "Review", "client": "Alice", "status": "Billed"},
    {"matter": "Case B", "hours": 1.0, "description": "Call", "client": "Bob", "status": "Pending"},
]
EVENTS = [
    {"date": "2026-03-01"},
    {"date": "2026-02-01"},
]


def test_extract_entity_dataset_supports_list_and_dict():
    assert gen._extract_entity_dataset(CLIENTS, "clients") == CLIENTS
    assert gen._extract_entity_dataset({"clients": CLIENTS}, "clients") == CLIENTS
    assert gen._extract_entity_dataset({"other": []}, "clients") is None


@pytest.mark.asyncio
async def test_ensure_crm_dataset_fetches_requested_entity(monkeypatch):
    monkeypatch.setattr(
        "autoppia_iwa.src.demo_webs.projects.p05_autocrm.data_utils.fetch_data",
        AsyncMock(return_value=CLIENTS),
    )

    result = await gen._ensure_crm_dataset("http://localhost:8000/?seed=4", None, entity_type="clients", method="distribute", filter_key="status")

    assert result == {"clients": CLIENTS}


@pytest.mark.asyncio
async def test_get_crm_entity_list_returns_entity_list(monkeypatch):
    monkeypatch.setattr(gen, "_ensure_crm_dataset", AsyncMock(return_value={"matters": MATTERS}))
    result = await gen._get_crm_entity_list(None, None, "matters")
    assert result == MATTERS


def test_collect_field_values_and_to_float_safe():
    assert set(gen._collect_field_values_from_dataset(CLIENTS, "status")) == {"Active", "Archived"}
    assert gen._to_float_safe("1,234.5") == 1234.5
    assert gen._to_float_safe("bad") is None


def test_generate_constraint_value_covers_string_list_and_numeric(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 1.5)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "shuffle", lambda seq: None)

    assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Alice", "name", CLIENTS) == "Bob"
    assert gen._generate_constraint_value(ComparisonOperator.CONTAINS, "Alice", "name", CLIENTS) in "Alice"
    assert "Alice" in gen._generate_constraint_value(ComparisonOperator.IN_LIST, "Alice", "name", CLIENTS)
    assert gen._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, "Alice", "name", CLIENTS) == ["Bob"]
    assert isinstance(gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 5, "matters", CLIENTS), float)


def test_generate_constraints_from_sample_skips_fields_without_ops(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    result = gen._generate_constraints_from_sample(CLIENTS, ["name", "missing"], {"name": [ComparisonOperator.EQUALS]})

    assert result == [{"field": "name", "operator": ComparisonOperator.EQUALS, "value": "Alice"}]


@pytest.mark.asyncio
async def test_view_and_search_constraints_use_expected_field_names(monkeypatch):
    monkeypatch.setattr(gen, "_get_crm_entity_list", AsyncMock(side_effect=[MATTERS, CLIENTS, CLIENTS, MATTERS]))
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    view_matter = await gen.generate_view_matter_constraints()
    view_client = await gen.generate_view_client_constraints()
    search_client = await gen.generate_search_client_constraints()
    search_matter = await gen.generate_search_matter_constraints()

    assert any(c["field"] == "name" for c in view_matter)
    assert any(c["field"] == "name" for c in view_client)
    assert search_client[0]["field"] == "query"
    assert search_matter[0]["field"] == "query"


def test_generate_value_for_document_field_handles_sizes(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 5)
    assert gen._generate_value_for_document_field("size", "25 KB", ComparisonOperator.GREATER_THAN, FILES) == "20 KB"
    assert gen._generate_value_for_document_field("size", "1.5 MB", ComparisonOperator.LESS_EQUAL, FILES) == "1.5 MB"


@pytest.mark.asyncio
async def test_document_constraints_and_rename(monkeypatch):
    monkeypatch.setattr(gen, "_get_crm_entity_list", AsyncMock(side_effect=[FILES, FILES]))
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    deleted = await gen.generate_document_deleted_constraints()
    renamed = await gen.generate_document_renamed_constraints()

    assert deleted
    assert [c["field"] for c in renamed] == ["new_name", "previous_name"]


@pytest.mark.asyncio
async def test_billing_and_client_generators(monkeypatch):
    monkeypatch.setattr(gen, "_get_crm_entity_list", AsyncMock(side_effect=[LOGS, CLIENTS, CLIENTS]))
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    billing = await gen.generate_billing_search_constraints()
    add_client = await gen.generate_add_client_constraints()
    filter_clients = await gen.generate_filter_clients_constraints()

    assert [c["field"] for c in billing] == ["query", "date_filter"]
    assert len(add_client) == 5
    assert [c["field"] for c in filter_clients] == ["status", "matters"]


def test_generate_new_calendar_event_constraints_and_sort_direction(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)

    calendar_constraints = gen.generate_new_calendar_event_constraints()
    sort_constraints = gen.generate_sort_matter_constraints()

    assert [c["field"] for c in calendar_constraints] == ["label", "time", "date", "event_type"]
    assert sort_constraints == [{"field": "direction", "operator": ComparisonOperator.EQUALS, "value": "asc"}]


@pytest.mark.asyncio
async def test_log_and_matter_generators(monkeypatch):
    monkeypatch.setattr(gen, "_get_crm_entity_list", AsyncMock(side_effect=[LOGS, LOGS, LOGS, MATTERS, MATTERS, EVENTS]))
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    new_log = await gen.generate_new_log_added_constraints()
    edit_log = await gen.generate_log_edited_constraints()
    delete_log = await gen.generate_delete_log_constraints()
    filter_status = await gen.generate_filter_matter_status_constraints()
    update_matter = await gen.generate_update_matter_constraints()
    pending = await gen.generate_view_pending_events_constraints()

    assert new_log
    assert edit_log
    assert delete_log
    assert filter_status[0]["field"] == "status"
    assert update_matter
    assert pending[0]["field"] == "earliest"


def test_generate_change_user_name_constraints(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    result = gen.generate_change_user_name_constraints()
    assert result[0]["field"] == "name"
