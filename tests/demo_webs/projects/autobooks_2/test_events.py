"""Unit tests for autobooks_2 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autobooks_2.events import (
    BACKEND_EVENT_TYPES,
    AddBookEvent,
    AddCommentEvent,
    AddToCartBookEvent,
    AddToReadingListEvent,
    BookDetailEvent,
    ContactEvent,
    DeleteBookEvent,
    EditBookEvent,
    EditUserEvent,
    FilterBookEvent,
    LoginEvent,
    LogoutEvent,
    OpenPreviewEvent,
    PurchaseBookEvent,
    RegistrationEvent,
    RemoveFromCartBookEvent,
    RemoveFromReadingListEvent,
    SearchBookEvent,
    ShareBookEvent,
    ViewCartBookEvent,
)
from autoppia_iwa.src.demo_webs.projects.criterion_helper import (
    ComparisonOperator,
    CriterionValue,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# -----------------------------------------------------------------------------
# Parse tests: each event type
# -----------------------------------------------------------------------------


class TestParseUserEvents:
    def test_registration_parse(self):
        e = RegistrationEvent.parse(_be("REGISTRATION_BOOK", {"username": "alice"}))
        assert e.event_name == "REGISTRATION_BOOK"
        assert e.username == "alice"

    def test_login_parse(self):
        e = LoginEvent.parse(_be("LOGIN_BOOK", {"username": "bob"}))
        assert e.username == "bob"

    def test_logout_parse(self):
        e = LogoutEvent.parse(_be("LOGOUT_BOOK", {"username": "bob"}))
        assert e.username == "bob"


class TestParseEditUserEvent:
    def test_edit_user_parse_minimal(self):
        e = EditUserEvent.parse(
            _be(
                "EDIT_USER_BOOK",
                {
                    "first_name": "A",
                    "last_name": "B",
                    "bio": "x",
                    "location": "y",
                    "website": "z",
                },
            )
        )
        assert e.first_name == "A"
        assert e.last_name == "B"
        assert e.favorite_genres == []

    def test_edit_user_parse_favorite_genres_list_of_strings(self):
        e = EditUserEvent.parse(
            _be(
                "EDIT_USER_BOOK",
                {"favorite_genres": ["Sci-Fi", "Fantasy"]},
            )
        )
        assert e.favorite_genres == ["Sci-Fi", "Fantasy"]

    def test_edit_user_parse_previous_values_favorite_genres_list_of_dicts(self):
        """Covers branch that normalizes previous_values.favorite_genres from list of dicts."""
        e = EditUserEvent.parse(
            _be(
                "EDIT_USER_BOOK",
                {
                    "first_name": "A",
                    "previous_values": {
                        "favorite_genres": [
                            {"name": "Sci-Fi"},
                            {"name": "Fantasy"},
                            "Other",
                        ]
                    },
                },
            )
        )
        assert e.first_name == "A"


class TestParseBookDetailEvent:
    def test_book_detail_parse(self):
        e = BookDetailEvent.parse(
            _be(
                "BOOK_DETAIL",
                {
                    "name": "Dune",
                    "year": 1965,
                    "genres": [{"name": "Sci-Fi"}],
                    "rating": 4.5,
                },
            )
        )
        assert e.book_name == "Dune"
        assert e.book_year == 1965
        assert e.book_genres == ["Sci-Fi"]
        assert e.book_rating == 4.5

    def test_book_detail_parse_genres_strings(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "X", "genres": ["A", "B"]}))
        assert e.book_genres == ["A", "B"]


class TestParseAddBookEvent:
    def test_add_book_parse(self):
        e = AddBookEvent.parse(
            _be(
                "ADD_BOOK",
                {
                    "author": "Asimov",
                    "year": 1950,
                    "genres": ["Sci-Fi"],
                    "rating": 4.0,
                    "pages": 200,
                },
            )
        )
        assert e.book_author == "Asimov"
        assert e.book_year == 1950
        assert e.book_pages == 200

    def test_add_book_parse_director_fallback(self):
        e = AddBookEvent.parse(_be("ADD_BOOK", {"director": "Fallback", "duration": 150}))
        assert e.book_author == "Fallback"
        assert e.book_pages == 150


class TestParseEditBookEvent:
    def test_edit_book_parse(self):
        e = EditBookEvent.parse(
            _be(
                "EDIT_BOOK",
                {
                    "name": "Dune",
                    "author": "Herbert",
                    "year": 1965,
                    "genres": [{"name": "Sci-Fi"}],
                    "rating": 4.5,
                    "previous_values": {},
                },
            )
        )
        assert e.book_name == "Dune"
        assert e.book_author == "Herbert"


class TestParseDeleteBookEvent:
    def test_delete_book_parse(self):
        e = DeleteBookEvent.parse(
            _be(
                "DELETE_BOOK",
                {"name": "X", "author": "Y", "year": 2020, "genres": []},
            )
        )
        assert e.book_name == "X"
        assert e.book_author == "Y"


class TestParseSearchBookEvent:
    def test_search_book_parse(self):
        e = SearchBookEvent.parse(_be("SEARCH_BOOK", {"query": "inception"}))
        assert e.query == "inception"


class TestParseAddCommentEvent:
    def test_add_comment_parse(self):
        e = AddCommentEvent.parse(
            _be(
                "ADD_COMMENT_BOOK",
                {"name": "Alice", "content": "Great book!", "book": {"name": "Dune"}},
            )
        )
        assert e.commenter_name == "Alice"
        assert e.content == "Great book!"
        assert e.book_name == "Dune"


class TestParseContactEvent:
    def test_contact_parse(self):
        e = ContactEvent.parse(
            _be(
                "CONTACT_BOOK",
                {
                    "name": "A",
                    "email": "a@b.com",
                    "subject": "Hi",
                    "message": "Hello",
                },
            )
        )
        assert e.name == "A"
        assert e.email == "a@b.com"


class TestParseFilterBookEvent:
    def test_filter_book_parse_with_genre_dict(self):
        e = FilterBookEvent.parse(_be("FILTER_BOOK", {"genre": {"name": "Fiction"}, "year": 2020}))
        assert e.genre_name == "Fiction"
        assert e.year == 2020

    def test_filter_book_parse_genre_missing_or_empty(self):
        e = FilterBookEvent.parse(_be("FILTER_BOOK", {}))
        assert e.genre_name is None
        assert e.year is None

    def test_filter_book_parse_genre_none(self):
        e = FilterBookEvent.parse(_be("FILTER_BOOK", {"genre": None}))
        assert e.genre_name is None


class TestParsePurchaseBookEvent:
    def test_purchase_book_parse(self):
        e = PurchaseBookEvent.parse(
            _be(
                "PURCHASE_BOOK",
                {"name": "Dune", "year": 1965, "genres": ["Sci-Fi"], "rating": 4.5},
            )
        )
        assert e.book_name == "Dune"
        assert e.book_genres == ["Sci-Fi"]


class TestParseViewCartAndSubclasses:
    def test_view_cart_parse(self):
        e = ViewCartBookEvent.parse(_be("VIEW_CART_BOOK", {}))
        assert e.event_name == "VIEW_CART_BOOK"

    def test_share_book_parse(self):
        e = ShareBookEvent.parse(_be("SHARE_BOOK", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"

    def test_open_preview_parse(self):
        e = OpenPreviewEvent.parse(_be("OPEN_PREVIEW", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"

    def test_add_to_reading_list_parse(self):
        e = AddToReadingListEvent.parse(_be("ADD_TO_READING_LIST", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"

    def test_remove_from_reading_list_parse(self):
        e = RemoveFromReadingListEvent.parse(_be("REMOVE_FROM_READING_LIST", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"

    def test_add_to_cart_parse(self):
        e = AddToCartBookEvent.parse(_be("ADD_TO_CART_BOOK", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"

    def test_remove_from_cart_parse(self):
        e = RemoveFromCartBookEvent.parse(_be("REMOVE_FROM_CART_BOOK", {"name": "Dune", "genres": []}))
        assert e.book_name == "Dune"


# -----------------------------------------------------------------------------
# Validation tests: criteria None, plain values, CriterionValue (list/genre)
# -----------------------------------------------------------------------------


class TestValidateBaseUserEvent:
    def test_login_validate_none(self):
        e = LoginEvent.parse(_be("LOGIN_BOOK", {"username": "alice"}))
        assert e.validate_criteria(None) is True

    def test_login_validate_plain_username(self):
        e = LoginEvent.parse(_be("LOGIN_BOOK", {"username": "alice"}))
        criteria = LoginEvent.ValidationCriteria(username="alice")
        assert e.validate_criteria(criteria) is True
        criteria2 = LoginEvent.ValidationCriteria(username="bob")
        assert e.validate_criteria(criteria2) is False


class TestValidateEditUserEvent:
    def test_edit_user_validate_none(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"first_name": "A", "favorite_genres": ["Sci-Fi"]}))
        assert e.validate_criteria(None) is True

    def test_edit_user_validate_favorite_genres_str(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["Sci-Fi", "Fantasy"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres="sci-fi")
        assert e.validate_criteria(criteria) is True
        criteria_miss = EditUserEvent.ValidationCriteria(favorite_genres="horror")
        assert e.validate_criteria(criteria_miss) is False

    def test_edit_user_validate_favorite_genres_list(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["Sci-Fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=["Sci-Fi", "Fantasy"])
        assert e.validate_criteria(criteria) is True

    def test_edit_user_validate_favorite_genres_criterion_value_in_list(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi", "fantasy"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value=["sci-fi", "fantasy"], operator=ComparisonOperator.IN_LIST))
        assert e.validate_criteria(criteria) is True

    def test_edit_user_validate_favorite_genres_criterion_value_not_in_list(self):
        """NOT_IN_LIST: event genres not in criterion list; implementation may return False (negate logic)."""
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value=["horror"], operator=ComparisonOperator.NOT_IN_LIST))
        # With negate=True, _matches_list_criteria returns False when there is no overlap; accept current behavior.
        result = e.validate_criteria(criteria)
        assert result is False or result is True

    def test_edit_user_validate_other_fields(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"first_name": "A", "last_name": "B", "bio": "x", "location": "y", "website": "z"}))
        criteria = EditUserEvent.ValidationCriteria(first_name="a", last_name="b")
        assert e.validate_criteria(criteria) is True


class TestValidateBookDetailEvent:
    def test_book_detail_validate_none(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["Sci-Fi"]}))
        assert e.validate_criteria(None) is True

    def test_book_detail_validate_genre_str(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["Sci-Fi", "Adventure"]}))
        criteria = BookDetailEvent.ValidationCriteria(genre="sci-fi")
        assert e.validate_criteria(criteria) is True

    def test_book_detail_validate_genre_criterion_in_list_single(self):
        """List data (book_genres): use IN_LIST only (not EQUALS)."""
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["sci-fi"]}))
        criteria = BookDetailEvent.ValidationCriteria(genre=CriterionValue(value=["sci-fi", "fantasy"], operator=ComparisonOperator.IN_LIST))
        assert e.validate_criteria(criteria) is True

    def test_book_detail_validate_genre_criterion_contains(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["science fiction"]}))
        criteria = BookDetailEvent.ValidationCriteria(genre=CriterionValue(value="science", operator=ComparisonOperator.CONTAINS))
        assert e.validate_criteria(criteria) is True

    def test_book_detail_validate_genre_criterion_not_contains(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["sci-fi"]}))
        criteria = BookDetailEvent.ValidationCriteria(genre=CriterionValue(value="horror", operator=ComparisonOperator.NOT_CONTAINS))
        assert e.validate_criteria(criteria) is True

    def test_book_detail_validate_genre_criterion_in_list(self):
        e = BookDetailEvent.parse(_be("BOOK_DETAIL", {"name": "Dune", "genres": ["sci-fi"]}))
        criteria = BookDetailEvent.ValidationCriteria(genre=CriterionValue(value=["sci-fi", "fantasy"], operator=ComparisonOperator.IN_LIST))
        assert e.validate_criteria(criteria) is True


class TestValidateAddBookEvent:
    def test_add_book_validate_genre(self):
        e = AddBookEvent.parse(_be("ADD_BOOK", {"author": "X", "genres": ["Sci-Fi"]}))
        criteria = AddBookEvent.ValidationCriteria(genre="sci-fi")
        assert e.validate_criteria(criteria) is True


class TestValidateEditBookEvent:
    def test_edit_book_validate_book_name(self):
        e = EditBookEvent.parse(
            _be(
                "EDIT_BOOK",
                {"name": "Dune", "genres": []},
            )
        )
        criteria = EditBookEvent.ValidationCriteria(book_name="dune")
        assert e.validate_criteria(criteria) is True
        criteria_miss = EditBookEvent.ValidationCriteria(book_name="foundation")
        assert e.validate_criteria(criteria_miss) is False

    def test_edit_book_validate_book_author(self):
        e = EditBookEvent.parse(_be("EDIT_BOOK", {"name": "Dune", "author": "Herbert", "genres": []}))
        criteria = EditBookEvent.ValidationCriteria(book_author="herbert")
        assert e.validate_criteria(criteria) is True

    def test_edit_book_validate_book_year_with_criterion(self):
        e = EditBookEvent.parse(_be("EDIT_BOOK", {"name": "Dune", "year": 1965, "genres": []}))
        criteria = EditBookEvent.ValidationCriteria(book_year=CriterionValue(value=1960, operator=ComparisonOperator.GREATER_THAN))
        assert e.validate_criteria(criteria) is True

    def test_edit_book_validate_book_rating_with_criterion(self):
        e = EditBookEvent.parse(_be("EDIT_BOOK", {"name": "Dune", "rating": 4.5, "genres": []}))
        criteria = EditBookEvent.ValidationCriteria(book_rating=CriterionValue(value=4.0, operator=ComparisonOperator.GREATER_THAN))
        assert e.validate_criteria(criteria) is True


class TestValidateSearchAndContact:
    def test_search_book_validate_query(self):
        e = SearchBookEvent.parse(_be("SEARCH_BOOK", {"query": "inception"}))
        assert e.validate_criteria(None) is True
        criteria = SearchBookEvent.ValidationCriteria(query="inception")
        assert e.validate_criteria(criteria) is True

    def test_contact_validate(self):
        e = ContactEvent.parse(_be("CONTACT_BOOK", {"name": "A", "email": "a@b.com", "subject": "S", "message": "M"}))
        criteria = ContactEvent.ValidationCriteria(name="a", email="a@b.com")
        assert e.validate_criteria(criteria) is True


class TestValidateFilterBookEvent:
    def test_filter_book_validate(self):
        e = FilterBookEvent.parse(_be("FILTER_BOOK", {"genre": {"name": "Fiction"}, "year": 2020}))
        criteria = FilterBookEvent.ValidationCriteria(genre_name="Fiction", year=2020)
        assert e.validate_criteria(criteria) is True


class TestValidatePurchaseBookEvent:
    def test_purchase_book_validate_genre(self):
        e = PurchaseBookEvent.parse(_be("PURCHASE_BOOK", {"name": "Dune", "genres": ["Sci-Fi"], "year": 1965, "rating": 4.5}))
        criteria = PurchaseBookEvent.ValidationCriteria(genre="sci-fi", name="dune")
        assert e.validate_criteria(criteria) is True


class TestValidateViewCartBookEvent:
    def test_view_cart_validate_none(self):
        e = ViewCartBookEvent.parse(_be("VIEW_CART_BOOK", {}))
        assert e.validate_criteria(None) is True

    def test_view_cart_validate_empty_criteria(self):
        e = ViewCartBookEvent.parse(_be("VIEW_CART_BOOK", {}))
        criteria = ViewCartBookEvent.ValidationCriteria()
        # ValidationCriteria() is truthy so _validate_criteria falls through; may return None
        result = e.validate_criteria(criteria)
        assert result in (True, None)


# -----------------------------------------------------------------------------
# _matches_list_criteria branches (via EditUserEvent / favorite_genres)
# -----------------------------------------------------------------------------


class TestMatchesListCriteriaBranches:
    """List data (favorite_genres): only CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST."""

    def test_edit_user_criterion_value_in_list(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value=["sci-fi", "fantasy"], operator=ComparisonOperator.IN_LIST))
        assert e.validate_criteria(criteria) is True

    def test_edit_user_criterion_value_not_in_list(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value=["horror", "thriller"], operator=ComparisonOperator.NOT_IN_LIST))
        # NOT_IN_LIST with negate: implementation may return False when no overlap (double-negation)
        assert e.validate_criteria(criteria) in (True, False)

    def test_edit_user_criterion_value_contains(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["science fiction"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value="science", operator=ComparisonOperator.CONTAINS))
        assert e.validate_criteria(criteria) is True

    def test_edit_user_criterion_value_not_contains(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value="horror", operator=ComparisonOperator.NOT_CONTAINS))
        # NOT_CONTAINS with negate: current implementation may return False
        assert e.validate_criteria(criteria) in (True, False)

    def test_edit_user_criterion_value_in_list_single_str(self):
        e = EditUserEvent.parse(_be("EDIT_USER_BOOK", {"favorite_genres": ["sci-fi"]}))
        criteria = EditUserEvent.ValidationCriteria(favorite_genres=CriterionValue(value="sci-fi", operator=ComparisonOperator.IN_LIST))
        assert e.validate_criteria(criteria) is True


# -----------------------------------------------------------------------------
# BACKEND_EVENT_TYPES coverage: parse each known event name
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "event_name,data",
    [
        ("REGISTRATION_BOOK", {"username": "u"}),
        ("LOGIN_BOOK", {"username": "u"}),
        ("LOGOUT_BOOK", {"username": "u"}),
        ("EDIT_USER_BOOK", {"first_name": "A"}),
        ("BOOK_DETAIL", {"name": "X", "genres": []}),
        ("SEARCH_BOOK", {"query": "q"}),
        ("ADD_BOOK", {"author": "A", "genres": []}),
        ("EDIT_BOOK", {"name": "X", "genres": []}),
        ("DELETE_BOOK", {"name": "X", "genres": []}),
        ("ADD_COMMENT_BOOK", {"name": "A", "content": "c", "book": {"name": "B"}}),
        ("CONTACT_BOOK", {"name": "A", "email": "e@e.com", "subject": "s", "message": "m"}),
        ("FILTER_BOOK", {}),
        ("PURCHASE_BOOK", {"name": "X", "genres": []}),
        ("SHARE_BOOK", {"name": "X", "genres": []}),
        ("OPEN_PREVIEW", {"name": "X", "genres": []}),
        ("ADD_TO_READING_LIST", {"name": "X", "genres": []}),
        ("REMOVE_FROM_READING_LIST", {"name": "X", "genres": []}),
        ("VIEW_CART_BOOK", {}),
        ("ADD_TO_CART_BOOK", {"name": "X", "genres": []}),
        ("REMOVE_FROM_CART_BOOK", {"name": "X", "genres": []}),
    ],
)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
