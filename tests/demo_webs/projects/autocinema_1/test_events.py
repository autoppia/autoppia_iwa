"""Unit tests for autocinema_1 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.p01_autocinema.events import (
    BACKEND_EVENT_TYPES,
    AddCommentEvent,
    AddFilmEvent,
    AddToWatchlistEvent,
    ContactEvent,
    DeleteFilmEvent,
    EditFilmEvent,
    EditUserEvent,
    FilmDetailEvent,
    FilterFilmEvent,
    LoginEvent,
    LogoutEvent,
    RegistrationEvent,
    RemoveFromWatchlistEvent,
    SearchFilmEvent,
    ShareFilmEvent,
    WatchTrailer,
    parse_genres_from_data,
    validate_genre_criteria,
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
    ("EDIT_FILM", {"name": "X", "year": 2000, "duration": 120, "rating": 4.0, "genres": [], "previous_values": {}, "changed_fields": []}),
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

    def test_registration_logout_and_edit_user_parse(self):
        registration = RegistrationEvent.parse(_be("REGISTRATION", {"username": "alice", "email": "a@a.com", "password": "secret"}))
        logout = LogoutEvent.parse(_be("LOGOUT", {"username": "alice"}))
        edit_user = EditUserEvent.parse(
            _be(
                "EDIT_USER",
                {
                    "username": "alice",
                    "email": "a@a.com",
                    "first_name": "Alice",
                    "favorite_genres": [{"name": "Drama"}],
                    "previous_values": {"favorite_genres": [{"name": "Action"}]},
                },
            )
        )
        assert registration.email == "a@a.com"
        assert logout.username == "alice"
        assert edit_user.favorite_genres == ["Drama"]

    def test_parse_various_film_related_events(self):
        add = AddFilmEvent.parse(_be("ADD_FILM", {"name": "X", "year": 2001, "genres": [{"name": "Drama"}]}))
        edit = EditFilmEvent.parse(_be("EDIT_FILM", {"name": "X", "year": 2002, "genres": [], "rating": 4.0, "duration": 120}))
        delete = DeleteFilmEvent.parse(_be("DELETE_FILM", {"name": "X", "year": 2002, "genres": ["Drama"]}))
        watchlist = AddToWatchlistEvent.parse(_be("ADD_TO_WATCHLIST", {"name": "X", "genres": ["Drama"]}))
        removed = RemoveFromWatchlistEvent.parse(_be("REMOVE_FROM_WATCHLIST", {"name": "X", "genres": ["Drama"]}))
        shared = ShareFilmEvent.parse(_be("SHARE_MOVIE", {"name": "X", "genres": ["Drama"]}))
        trailer = WatchTrailer.parse(_be("WATCH_TRAILER", {"name": "X", "genres": ["Drama"]}))
        assert add.movie_name == "X"
        assert edit.movie_year == 2002
        assert delete.movie_genres == ["Drama"]
        assert watchlist.movie_name == "X"
        assert removed.movie_name == "X"
        assert shared.movie_name == "X"
        assert trailer.movie_name == "X"

    def test_parse_add_comment_and_contact(self):
        comment = AddCommentEvent.parse(_be("ADD_COMMENT", {"name": "Alice", "content": "Nice", "movie": {"id": 3, "name": "Dune"}}))
        contact = ContactEvent.parse(_be("CONTACT", {"name": "Alice", "email": "a@a.com", "subject": "Hi", "message": "Hello"}))
        assert comment.commenter_name == "Alice"
        assert comment.movie_name == "Dune"
        assert contact.email == "a@a.com"


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

    def test_validate_genre_criteria_variants(self):
        assert validate_genre_criteria(["Sci-Fi", "Drama"], None) is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], "sci") is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], CriterionValue(value="Drama", operator="equals")) is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], CriterionValue(value="ram", operator="contains")) is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], CriterionValue(value="Horror", operator="not_contains")) is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], CriterionValue(value=["Drama", "Comedy"], operator="in_list")) is True
        assert validate_genre_criteria(["Sci-Fi", "Drama"], CriterionValue(value=["Comedy"], operator="not_in_list")) is True

    def test_edit_user_validate_criteria(self):
        event = EditUserEvent.parse(
            _be(
                "EDIT_USER",
                {
                    "username": "alice",
                    "email": "a@a.com",
                    "first_name": "Alice",
                    "bio": "Movie fan",
                    "location": "Madrid",
                    "website": "https://alice.dev",
                    "favorite_genres": ["Drama"],
                },
            )
        )
        criteria = EditUserEvent.ValidationCriteria(username="alice", email="a@a.com", first_name="Alice", favorite_genres="Drama")
        assert event.validate_criteria(criteria) is True

    def test_registration_and_logout_validate_criteria(self):
        registration = RegistrationEvent.parse(_be("REGISTRATION", {"username": "alice", "email": "a@a.com", "password": "secret"}))
        logout = LogoutEvent.parse(_be("LOGOUT", {"username": "alice"}))
        assert registration.validate_criteria(RegistrationEvent.ValidationCriteria(username="alice", email="a@a.com", password="secret")) is True
        assert logout.validate_criteria(LogoutEvent.ValidationCriteria(username="alice")) is True

    def test_edit_and_delete_film_validate_criteria(self):
        edit = EditFilmEvent.parse(_be("EDIT_FILM", {"name": "Inception", "director": "Nolan", "year": 2010, "rating": 4.5, "duration": 148, "genres": ["Sci-Fi"]}))
        delete = DeleteFilmEvent.parse(_be("DELETE_FILM", {"name": "Inception", "director": "Nolan", "year": 2010, "genres": ["Sci-Fi"]}))
        edit_criteria = EditFilmEvent.ValidationCriteria(name="Inception", director="Nolan", movie_year=2010, movie_rating=4.5, movie_duration=148)
        delete_criteria = DeleteFilmEvent.ValidationCriteria(name="Inception", director="Nolan", year=2010, genre="Sci-Fi")
        assert edit.validate_criteria(edit_criteria) is True
        assert delete.validate_criteria(delete_criteria) is True

    def test_parse_genres_from_data_supports_mixed_values(self):
        assert parse_genres_from_data({"genres": [{"name": "Drama"}, "Sci-Fi"]}) == ["Drama", "Sci-Fi"]


@pytest.mark.parametrize("event_name,data", AUTOCINEMA_PARSE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
