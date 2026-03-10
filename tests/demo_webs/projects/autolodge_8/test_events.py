"""Unit tests for autolodge_8 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autolodge_8.events import (
    BACKEND_EVENT_TYPES,
    AddToWishlistEvent,
    ApplyFilterEvent,
    BackToAllHotelsEvent,
    BookFromWishlistEvent,
    FaqOpenedEvent,
    RemoveFromWishlistEvent,
    SearchHotelEvent,
    ShareHotelEvent,
    ViewHotelEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Minimal hotel for events that require HotelInfo
_HOTEL = {
    "title": "H",
    "location": "L",
    "price": 100,
    "rating": 4.0,
    "reviews": 0,
    "guests": 1,
    "maxGuests": 2,
    "datesFrom": "2025-03-01",
    "datesTo": "2025-03-02",
    "baths": 1,
    "bedrooms": 1,
    "beds": 1,
    "host": {"name": "Host"},
}

AUTOLODGE_PAYLOADS = [
    ("SEARCH_HOTEL", {"searchTerm": "Paris"}),
    ("VIEW_HOTEL", _HOTEL),
    ("APPLY_FILTERS", {}),
    ("ADD_TO_WISHLIST", _HOTEL),
    ("REMOVE_FROM_WISHLIST", _HOTEL),
    ("SHARE_HOTEL", {"email": "e@e.com", **_HOTEL}),
    ("BACK_TO_ALL_HOTELS", {"hotel": _HOTEL}),
    ("WISHLIST_OPENED", {}),
    ("BOOK_FROM_WISHLIST", {}),
    ("POPULAR_HOTELS_VIEWED", {}),
    ("HELP_VIEWED", {}),
    ("FAQ_OPENED", {}),
]
# Events that need complex HotelInfo or payment payloads (covered by other tests):
# RESERVE_HOTEL, EDIT_NUMBER_OF_GUESTS, EDIT_CHECK_IN_OUT_DATES, PAYMENT_METHOD_SELECTED,
# CONFIRM_AND_PAY, MESSAGE_HOST


@pytest.mark.parametrize("event_name,data", AUTOLODGE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


def test_search_hotel_parse():
    e = SearchHotelEvent.parse(_be("SEARCH_HOTEL", {"searchTerm": "Paris"}))
    assert e.search_term == "Paris"


class TestValidateAutolodgeEventsCriteria:
    """Validate_criteria tests for autolodge_8 events that have ValidationCriteria."""

    def test_search_hotel_event_validate_criteria(self):
        e = SearchHotelEvent.parse(_be("SEARCH_HOTEL", {"searchTerm": "Paris"}))
        criteria = SearchHotelEvent.ValidationCriteria(search_term="Paris")
        assert e.validate_criteria(criteria) is True

    def test_view_hotel_event_validate_criteria(self):
        e = ViewHotelEvent.parse(_be("VIEW_HOTEL", _HOTEL))
        criteria = ViewHotelEvent.ValidationCriteria(title="H", location="L", rating=4.0)
        assert e.validate_criteria(criteria) is True

    def test_add_to_wishlist_event_validate_criteria(self):
        e = AddToWishlistEvent.parse(_be("ADD_TO_WISHLIST", _HOTEL))
        criteria = AddToWishlistEvent.ValidationCriteria(title="H", location="L")
        assert e.validate_criteria(criteria) is True

    def test_remove_from_wishlist_event_validate_criteria(self):
        e = RemoveFromWishlistEvent.parse(_be("REMOVE_FROM_WISHLIST", _HOTEL))
        criteria = RemoveFromWishlistEvent.ValidationCriteria(title="H")
        assert e.validate_criteria(criteria) is True

    def test_share_hotel_event_validate_criteria(self):
        e = ShareHotelEvent.parse(_be("SHARE_HOTEL", {"email": "e@e.com", **_HOTEL}))
        criteria = ShareHotelEvent.ValidationCriteria(title="H", email="e@e.com")
        assert e.validate_criteria(criteria) is True

    def test_apply_filter_event_validate_criteria(self):
        e = ApplyFilterEvent.parse(_be("APPLY_FILTERS", {"rating": 4.0, "region": "Paris"}))
        criteria = ApplyFilterEvent.ValidationCriteria(rating=4.0, region="Paris")
        assert e.validate_criteria(criteria) is True

    def test_back_to_all_hotels_event_validate_criteria(self):
        e = BackToAllHotelsEvent.parse(_be("BACK_TO_ALL_HOTELS", {"hotel": _HOTEL}))
        criteria = BackToAllHotelsEvent.ValidationCriteria(title="H", location="L")
        assert e.validate_criteria(criteria) is True

    def test_book_from_wishlist_event_validate_none(self):
        e = BookFromWishlistEvent.parse(_be("BOOK_FROM_WISHLIST", {}))
        assert e.validate_criteria(None) is True

    def test_faq_opened_event_validate_criteria(self):
        e = FaqOpenedEvent.parse(_be("FAQ_OPENED", {"question": "How to cancel?"}))
        criteria = FaqOpenedEvent.ValidationCriteria(question="How to cancel?")
        assert e.validate_criteria(criteria) is True
