"""Unit tests for autocinema_1 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p01_autocinema.events import (
    BACKEND_EVENT_TYPES,
    FilmDetailEvent,
    FilterFilmEvent,
    LoginEvent,
    SearchFilmEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Minimal payloads so parse() runs without error
AUTOCINEMA_PARSE_PAYLOADS = [
    ("LOGIN", {"username": "u"}),
    ("LOGOUT", {"username": "u"}),
    ("REGISTRATION", {"username": "u", "email": "e@e.com", "password": "p"}),
    ("EDIT_USER", {"username": "u", "email": "e@e.com"}),
    ("FILM_DETAIL", {"name": "Inception", "genres": []}),
    ("SEARCH_FILM", {"query": "matrix"}),
    ("ADD_FILM", {"name": "X", "genres": []}),
    ("EDIT_FILM", {"name": "X", "genres": [], "previous_values": {}, "changed_fields": []}),
    ("DELETE_FILM", {"name": "X", "genres": []}),
    ("ADD_COMMENT", {"name": "A", "content": "c", "movie": {"id": 1, "name": "M"}}),
    ("CONTACT", {"name": "A", "email": "e@e.com", "subject": "s", "message": "m"}),
    ("FILTER_FILM", {"genre": {"name": "Sci-Fi"}, "year": 2020}),
    ("ADD_TO_WATCHLIST", {"name": "X", "genres": []}),
    ("REMOVE_FROM_WATCHLIST", {"name": "X", "genres": []}),
    ("SHARE_MOVIE", {"name": "X", "genres": []}),
    ("WATCH_TRAILER", {"name": "X", "genres": []}),
]


class TestParseAutocinemaEvents:
    def test_login_parse(self):
        e = LoginEvent.parse(_be("LOGIN", {"username": "alice"}))
        assert e.event_name == "LOGIN"
        assert e.username == "alice"

    def test_film_detail_parse(self):
        e = FilmDetailEvent.parse(_be("FILM_DETAIL", {"name": "Inception", "year": 2010, "genres": [{"name": "Sci-Fi"}]}))
        assert e.movie_name == "Inception"
        assert e.movie_year == 2010
        assert e.movie_genres == ["Sci-Fi"]

    def test_search_film_parse(self):
        e = SearchFilmEvent.parse(_be("SEARCH_FILM", {"query": "matrix"}))
        assert e.query == "matrix"

    def test_filter_film_parse(self):
        e = FilterFilmEvent.parse(_be("FILTER_FILM", {"genre": {"name": "Action"}, "year": 2020}))
        assert e.genre_name == "Action"
        assert e.year == 2020


class TestValidateAutocinemaEvents:
    def test_login_validate_none(self):
        e = LoginEvent.parse(_be("LOGIN", {"username": "alice"}))
        assert e.validate_criteria(None) is True

    def test_film_detail_validate_none(self):
        e = FilmDetailEvent.parse(_be("FILM_DETAIL", {"name": "X", "genres": []}))
        assert e.validate_criteria(None) is True

    def test_search_film_validate_query(self):
        e = SearchFilmEvent.parse(_be("SEARCH_FILM", {"query": "inception"}))
        criteria = SearchFilmEvent.ValidationCriteria(query="inception")
        assert e.validate_criteria(criteria) is True


@pytest.mark.parametrize("event_name,data", AUTOCINEMA_PARSE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
