"""Tests for automail generation_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p06_automail import generation_functions as gen

EMAILS = [
    {
        "subject": "Project Update",
        "body": "Hi team,\nThis is the longest useful line in the body.\nRegards",
        "to": "alice@example.com",
        "is_starred": False,
        "is_read": True,
        "is_important": False,
        "is_spam": True,
        "labels": [{"name": "Work", "color": "blue"}],
    },
    {
        "subject": "Dinner Plans",
        "body": "Let's meet at 8pm",
        "to": "bob@example.com",
        "is_starred": False,
        "is_read": False,
        "is_important": True,
        "is_spam": False,
        "labels": [{"name": "Personal", "color": "green"}],
    },
]


def test_body_safe_helpers_strip_name_and_newlines():
    body = "Hi <name>,\n\nLongest useful sentence here.\nThanks"
    assert gen._body_safe_substring_for_contains(body) == "Longest useful sentence here."
    assert gen._email_body_safe_for_constraint("a\nvery long line here\nb") == "very long line here"


@pytest.mark.asyncio
async def test_ensure_email_dataset_fetches(monkeypatch):
    fetch = AsyncMock(return_value=EMAILS)
    monkeypatch.setattr(gen, "fetch_data", fetch)

    result = await gen._ensure_email_dataset("http://localhost:8000/?seed=8", None)

    assert result == EMAILS
    fetch.assert_awaited_once_with(seed_value=8)


def test_dataset_helpers_and_constraint_value(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
    monkeypatch.setattr(gen.random, "uniform", lambda a, b: 1.5)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "shuffle", lambda seq: None)

    assert set(gen._collect_field_values_from_dataset(EMAILS, "subject")) == {"Project Update", "Dinner Plans"}
    assert gen._pick_different_value_from_dataset(EMAILS, "subject", "Project Update") == "Dinner Plans"
    assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Project Update", "subject", EMAILS) == "Dinner Plans"
    assert gen._generate_constraint_value(ComparisonOperator.CONTAINS, "Project Update", "subject", EMAILS) in "Project Update"
    assert "Project Update" in gen._generate_constraint_value(ComparisonOperator.IN_LIST, "Project Update", "subject", EMAILS)
    assert isinstance(gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 4.0, "score", [{"score": 4.0}]), float)


@pytest.mark.asyncio
async def test_view_email_constraints_build_from_dataset(monkeypatch):
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 2)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])

    result = await gen.generate_view_email_constraints(dataset=EMAILS)

    assert len(result) == 2
    assert all("field" in c for c in result)


def test_boolean_constraints_value():
    assert gen._boolean_constraints_value(True, ComparisonOperator.EQUALS) is True
    assert gen._boolean_constraints_value(True, ComparisonOperator.NOT_EQUALS) is False


@pytest.mark.asyncio
async def test_flag_generators_and_search(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    starred = await gen.generate_is_starred_constraints(dataset=EMAILS)
    read = await gen.generate_is_read_constraints(dataset=EMAILS)
    important = await gen.generate_is_important_constraints(dataset=EMAILS)
    spam = await gen.generate_is_spam_constraints(dataset=EMAILS)
    search = await gen.generate_search_email_constraints(dataset=EMAILS)

    assert starred[0]["field"] == "is_starred"
    assert read[0]["field"] == "is_read"
    assert important[0]["field"] == "is_important"
    assert spam[0]["field"] == "is_spam"
    assert search


@pytest.mark.asyncio
async def test_draft_archive_and_labels(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen.random, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

    draft = await gen.generate_save_as_draft_send_email_constraints(dataset=EMAILS)
    archive = await gen.generate_archive_email_constraints(dataset=EMAILS)
    create_label = await gen.generate_create_label_constraints(dataset=EMAILS)
    add_label = await gen.generate_add_label_constraints(dataset=EMAILS)

    assert draft
    assert archive
    assert create_label[0]["field"] == "label_name"
    assert add_label


def test_theme_and_template_generators(monkeypatch):
    monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
    monkeypatch.setattr(gen, "randint", lambda a, b: 1)
    monkeypatch.setattr(gen, "sample", lambda seq, n: seq[:n])

    theme = gen.generate_theme_changed_constraints()
    selection = gen.generate_template_selection_constraints()
    body = gen.generate_template_body_constraints()
    sent = gen.generate_sent_template_constraints()

    assert theme[0]["field"] == "theme"
    assert selection
    assert body
    assert sent
