"""Tests for autobooks replace_functions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from autoppia_iwa.src.demo_webs.projects.p02_autobooks import replace_functions as repl

BOOKS = [
    {"name": "Dune", "author": "Frank Herbert, Brian Herbert", "genres": ["Sci-Fi", "Adventure"], "page_count": 412, "year": 1965},
    {"name": "It", "author": "Stephen King", "genres": ["Horror"], "page_count": 900, "year": 1986},
]


def test_extract_decades_builds_unique_set():
    assert repl._extract_decades(BOOKS) == {1960, 1980}


def test_filter_books_by_decade_limits_range():
    result = repl._filter_books_by_decade(BOOKS, 1960)
    assert result == [BOOKS[0]]


def test_process_decade_placeholder_returns_original_when_missing():
    text, books, placeholders = repl._process_decade_placeholder("Read <book>", BOOKS)
    assert text == "Read <book>"
    assert books == BOOKS
    assert placeholders == {}


def test_process_decade_placeholder_filters_dataset(monkeypatch):
    monkeypatch.setattr(repl.random, "choice", lambda seq: 1980)
    text, books, placeholders = repl._process_decade_placeholder("Find <decade>s horror", BOOKS)
    assert text == "Find <decade>s horror"
    assert books == [BOOKS[1]]
    assert placeholders == {"<decade>": "198"}


def test_replace_book_field_placeholders_uses_list_choice(monkeypatch):
    monkeypatch.setattr(repl.random, "choice", lambda seq: seq[-1])
    result = repl._replace_book_field_placeholders("Genre <genres>", BOOKS[0])
    assert result == "Genre Adventure"


def test_replace_author_placeholder_cycles_authors():
    result = repl._replace_author_placeholder("By <author> with <author>", BOOKS[0])
    assert result == "By Frank Herbert with Brian Herbert"


def test_replace_author_placeholder_ignores_non_string_author():
    result = repl._replace_author_placeholder("By <author>", {"author": ["bad"]})
    assert result == "By <author>"


def test_replace_specialized_placeholders_cover_book_genre_pages_and_authors(monkeypatch):
    monkeypatch.setattr(repl.random, "choice", lambda seq: seq[0])
    text = "<book> / <genre> / <page_count> / <authors>"
    text = repl._replace_genre_placeholder(text, BOOKS[0])
    text = repl._replace_book_placeholder(text, BOOKS[0])
    text = repl._replace_page_count_placeholder(text, BOOKS[0])
    text = repl._replace_authors_placeholder(text, BOOKS[0])
    assert text == "Dune / Sci-Fi / 412 / Frank Herbert, Brian Herbert"


@pytest.mark.asyncio
async def test_replace_book_placeholders_returns_non_string_unchanged():
    assert await repl.replace_book_placeholders(123) == 123


@pytest.mark.asyncio
async def test_replace_book_placeholders_uses_fetched_dataset(monkeypatch):
    monkeypatch.setattr(repl, "fetch_data", AsyncMock(return_value=BOOKS))
    monkeypatch.setattr(repl.random, "choice", lambda seq: seq[0])

    result = await repl.replace_book_placeholders("Read <book> by <author> in <genre>", seed_value=5)

    assert result == "Read Dune by Frank Herbert, Brian Herbert in Sci-Fi"


@pytest.mark.asyncio
async def test_replace_book_placeholders_returns_original_when_dataset_empty(monkeypatch):
    monkeypatch.setattr(repl, "fetch_data", AsyncMock(return_value=[]))
    assert await repl.replace_book_placeholders("Read <book>", seed_value=5) == "Read <book>"
