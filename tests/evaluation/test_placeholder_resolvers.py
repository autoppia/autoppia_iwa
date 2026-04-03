from unittest.mock import AsyncMock

import pytest

import autoppia_iwa.src.evaluation.shared.utils as eval_utils
from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import CheckEventTest


def _make_books(count: int = 50) -> list[dict]:
    return [
        {
            "name": f"Book-{i}",
            "id": str(i),
            "author": f"Author-{i}",
        }
        for i in range(count)
    ]


def _make_movies(count: int = 50) -> list[dict]:
    # Note: autocinema placeholder resolver parses film_id as the last '-' segment (int()).
    return [
        {
            "name": f"Film-{i}",
            "id": f"cinema-{i}",
            "director": f"Director-{i}",
        }
        for i in range(count)
    ]


def test_get_deterministic_user_index_web_agent_id_1():
    # username = "user{web_agent_id}" where web_agent_id="1" => "user1"
    # regex match => parsed=1 => returns parsed-1 => 0
    assert eval_utils._get_deterministic_user_index("user1") == 0


def test_resolve_assigned_book_for_agent_web_agent_id_1():
    books = _make_books(50)
    # For web_agent_id="1": user_index=0 => book_index=0 (for any len(books)>0)
    assert eval_utils._resolve_assigned_book_for_agent(books, "1") == books[0]

    # Also sanity check empty dataset behavior
    assert eval_utils._resolve_assigned_book_for_agent([], "1") is None


@pytest.mark.asyncio
async def test_resolve_autobooks_book_placeholders_in_tests_replaces_only_target_events(monkeypatch):
    # For web_agent_id="1": username="user1" -> user_index=0 -> assigned_index=0.
    expected_index = 0
    books = _make_books(50)

    monkeypatch.setattr(eval_utils, "fetch_books_data", AsyncMock(return_value=books))

    task = Task(
        url="http://example.test/?seed=7",
        prompt="p",
        web_project_id="autobooks",
        tests=[
            CheckEventTest(
                type="CheckEventTest",
                event_name="DELETE_BOOK",
                event_criteria={
                    "book_name": {"value": "<book_name>", "operator": "equals"},
                    "book_id": {"value": "<book_id>", "operator": "equals"},
                    "book_author": {"value": "<book_author>", "operator": "equals"},
                    "assigned_book_name": {"value": "<assigned_book_name>", "operator": "equals"},
                    "assigned_book_author": {"value": "<assigned_book_author>", "operator": "equals"},
                    "assigned_book_id": {"value": "<assigned_book_id>", "operator": "equals"},
                    # Ensure recursive replacement works for lists too.
                    "tag_values": ["<book_name>", "<book_author>"],
                },
            ),
            CheckEventTest(
                type="CheckEventTest",
                event_name="EDIT_BOOK",
                event_criteria={
                    "book_name": {"value": "<book_name>", "operator": "equals"},
                    "book_id": {"value": "<book_id>", "operator": "equals"},
                    "book_author": {"value": "<book_author>", "operator": "equals"},
                    "assigned_book_name": {"value": "<assigned_book_name>", "operator": "equals"},
                    "assigned_book_author": {"value": "<assigned_book_author>", "operator": "equals"},
                    "assigned_book_id": {"value": "<assigned_book_id>", "operator": "equals"},
                },
            ),
        ],
    )

    resolved_tests = await eval_utils._resolve_autobooks_book_placeholders_in_tests(task, web_agent_id="1")

    delete_test = next(t for t in resolved_tests if getattr(t, "event_name", None) == "DELETE_BOOK")
    edit_test = next(t for t in resolved_tests if getattr(t, "event_name", None) == "EDIT_BOOK")

    expected_book = books[expected_index]

    for test in (delete_test, edit_test):
        assert test.event_criteria["book_name"]["value"] == expected_book["name"]
        assert test.event_criteria["book_id"]["value"] == expected_book["id"]
        assert test.event_criteria["book_author"]["value"] == expected_book["author"]

        assert test.event_criteria["assigned_book_name"]["value"] == expected_book["name"]
        assert test.event_criteria["assigned_book_author"]["value"] == expected_book["author"]
        assert test.event_criteria["assigned_book_id"]["value"] == expected_book["id"]

    # autobooks resolver deepcopy()s task.tests before replacement, so original placeholders must remain.
    original_delete = next(t for t in task.tests if getattr(t, "event_name", None) == "DELETE_BOOK")
    assert original_delete.event_criteria["book_name"]["value"] == "<book_name>"
    assert original_delete.event_criteria["tag_values"] == ["<book_name>", "<book_author>"]


@pytest.mark.asyncio
async def test_resolve_autocinema_film_placeholders_in_tests_replaces_only_target_events(monkeypatch):
    # For web_agent_id="1": username="user1" -> user_index=0 -> assigned_index=0.
    expected_index = 0
    movies = _make_movies(50)

    monkeypatch.setattr(eval_utils, "fetch_movies_data", AsyncMock(return_value=movies))

    tests_for_run = [
        CheckEventTest(
            type="CheckEventTest",
            event_name="DELETE_FILM",
            event_criteria={
                "film_name": {"value": "<film_name>", "operator": "equals"},
                "film_director": {"value": "<film_director>", "operator": "equals"},
                "film_id": {"value": "<film_id>", "operator": "equals"},
                "assigned_film_name": {"value": "<assigned_film_name>", "operator": "equals"},
                "assigned_film_director": {"value": "<assigned_film_director>", "operator": "equals"},
                "assigned_film_id": {"value": "<assigned_film_id>", "operator": "equals"},
                "tag_values": ["<film_name>", "<film_director>"],
            },
        ),
        CheckEventTest(
            type="CheckEventTest",
            event_name="EDIT_FILM",
            event_criteria={
                "film_name": {"value": "<film_name>", "operator": "equals"},
                "film_director": {"value": "<film_director>", "operator": "equals"},
                "film_id": {"value": "<film_id>", "operator": "equals"},
                "assigned_film_name": {"value": "<assigned_film_name>", "operator": "equals"},
                "assigned_film_director": {"value": "<assigned_film_director>", "operator": "equals"},
                "assigned_film_id": {"value": "<assigned_film_id>", "operator": "equals"},
            },
        ),
    ]

    task = Task(
        url="http://example.test/?seed=7",
        prompt="p",
        web_project_id="autocinema",
        tests=[],
    )

    resolved_tests = await eval_utils._resolve_autocinema_film_placeholders_in_tests(task, tests_for_run, web_agent_id="1")

    delete_test = next(t for t in resolved_tests if getattr(t, "event_name", None) == "DELETE_FILM")
    edit_test = next(t for t in resolved_tests if getattr(t, "event_name", None) == "EDIT_FILM")

    expected_movie = movies[expected_index]
    expected_film_id = str(int(expected_movie["id"].rsplit("-", 1)[-1]))

    for test in (delete_test, edit_test):
        assert test.event_criteria["film_name"]["value"] == expected_movie["name"]
        assert test.event_criteria["film_director"]["value"] == expected_movie["director"]
        assert test.event_criteria["film_id"]["value"] == expected_film_id

        assert test.event_criteria["assigned_film_name"]["value"] == expected_movie["name"]
        assert test.event_criteria["assigned_film_director"]["value"] == expected_movie["director"]
        assert test.event_criteria["assigned_film_id"]["value"] == expected_film_id

    # autocinema resolver mutates tests_for_run in place (does not deepcopy()).
    assert tests_for_run[0].event_criteria["film_name"]["value"] == expected_movie["name"]
