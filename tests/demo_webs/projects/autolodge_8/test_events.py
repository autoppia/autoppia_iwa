"""Unit tests for autolodge_8 events (parse) to improve coverage."""

from datetime import datetime

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.p08_autolodge.events import (
    BACKEND_EVENT_TYPES,
    AddToWishlistEvent,
    ApplyFilterEvent,
    BackToAllHotelsEvent,
    BookFromWishlistEvent,
    ConfirmAndPayEvent,
    EditCheckInOutDatesEvent,
    EditNumberOfGuestsEvent,
    FaqOpenedEvent,
    HelpViewedEvent,
    HotelInfo,
    MessageHostEvent,
    PaymentMethodSelectedEvent,
    PopularHotelsViewedEvent,
    RemoveFromWishlistEvent,
    ReserveHotelEvent,
    SearchHotelEvent,
    ShareHotelEvent,
    SubmitHotelReviewEvent,
    ViewHotelEvent,
    WishlistOpenedEvent,
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
    "amenities": [{"title": "Wifi"}, "Pool"],
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

    def test_search_hotel_event_dates_and_guests(self):
        event = SearchHotelEvent.parse(
            _be(
                "SEARCH_HOTEL",
                {
                    "searchTerm": "Paris",
                    "dateRange": {"from": "2025-03-01", "to": "2025-03-02"},
                    "guests": {"adults": 2, "children": 1, "infants": 0, "pets": 1},
                },
            )
        )
        criteria = SearchHotelEvent.ValidationCriteria(
            search_term="Paris",
            datesFrom=datetime(2025, 3, 1),
            datesTo=datetime(2025, 3, 2),
            adults=2,
            children=1,
            pets=1,
        )
        assert event.validate_criteria(criteria) is True

    def test_view_hotel_event_amenities_criterion_value(self):
        event = ViewHotelEvent.parse(_be("VIEW_HOTEL", _HOTEL))
        criteria = ViewHotelEvent.ValidationCriteria(
            amenities=CriterionValue(operator=ComparisonOperator.CONTAINS, value="wi"),
            host_name="Host",
        )
        assert event.validate_criteria(criteria) is True

    def test_hotel_info_list_amenities_validation(self):
        hotel = HotelInfo.parse({"hotel": _HOTEL})
        criteria = HotelInfo.ValidationCriteria(amenities=["Wifi", "Pool"])
        assert hotel._validate_criteria(criteria) is True

    def test_submit_hotel_review_parse_and_validate(self):
        payload = {
            **_HOTEL,
            "comment": "Great stay",
            "name": "Alice",
            "host_name": "Host",
        }
        event = SubmitHotelReviewEvent.parse(_be("SUBMIT_HOTEL_REVIEW", payload))
        criteria = SubmitHotelReviewEvent.ValidationCriteria(comment="Great stay", name="Alice", title="H")
        assert event.validate_criteria(criteria) is True

    def test_reserve_hotel_validate(self):
        event = ReserveHotelEvent.parse(_be("RESERVE_HOTEL", {"hotel": _HOTEL, "guests_set": 2}))
        criteria = ReserveHotelEvent.ValidationCriteria(title="H", guests_set=2)
        assert event.validate_criteria(criteria) is True

    def test_edit_number_of_guests_validate(self):
        event = EditNumberOfGuestsEvent.parse(_be("EDIT_NUMBER_OF_GUESTS", {"hotel": _HOTEL, "to": 3}))
        criteria = EditNumberOfGuestsEvent.ValidationCriteria(title="H", guests_to=3)
        assert event.validate_criteria(criteria) is True

    def test_edit_checkin_checkout_dates_validate(self):
        event = EditCheckInOutDatesEvent.parse(
            _be(
                "EDIT_CHECK_IN_OUT_DATES",
                {"hotel": _HOTEL, "dateRange": {"from": "2025-04-01", "to": "2025-04-03"}},
            )
        )
        criteria = EditCheckInOutDatesEvent.ValidationCriteria(
            title="H",
            checkin=datetime(2025, 4, 1),
            checkout=datetime(2025, 4, 3),
        )
        assert event.validate_criteria(criteria) is True

    def test_confirm_and_pay_parse_and_validate(self):
        payload = {
            **_HOTEL,
            "nights": 2,
            "priceSubtotal": 200,
            "total": 220,
            "cardNumber": "4242",
            "expiration": "12/30",
            "cvv": "123",
            "country": "ES",
            "guests_set": 2,
            "zipcode": "28001",
            "host_name": "Host",
        }
        event = ConfirmAndPayEvent.parse(_be("CONFIRM_AND_PAY", payload))
        criteria = ConfirmAndPayEvent.ValidationCriteria(
            title="H",
            nights=2,
            priceSubtotal=200,
            total=220,
            cardNumber="4242",
            expiration="12/30",
            cvv="123",
            country="ES",
            guests_set=2,
            zipcode="28001",
        )
        assert event._validate_criteria(criteria) is True

    def test_payment_method_selected_parse_and_validate(self):
        payload = {**_HOTEL, "method": "visa", "host_name": "Host"}
        event = PaymentMethodSelectedEvent.parse(_be("PAYMENT_METHOD_SELECTED", payload))
        criteria = PaymentMethodSelectedEvent.ValidationCriteria(title="H", method="visa")
        assert event._validate_criteria(criteria) is True

    def test_message_host_parse_and_validate(self):
        event = MessageHostEvent.parse(_be("MESSAGE_HOST", {"hotel": _HOTEL, "message": "Hello host"}))
        criteria = MessageHostEvent.ValidationCriteria(title="H", message="Hello host")
        assert event.validate_criteria(criteria) is True

    def test_wishlist_popular_and_help_validate_none(self):
        assert WishlistOpenedEvent.parse(_be("WISHLIST_OPENED", {})).validate_criteria(None) is True
        assert PopularHotelsViewedEvent.parse(_be("POPULAR_HOTELS_VIEWED", {})).validate_criteria(None) is True
        assert HelpViewedEvent.parse(_be("HELP_VIEWED", {})).validate_criteria(None) is True

    def test_book_from_wishlist_uses_hotel_id(self):
        event = BookFromWishlistEvent.parse(_be("BOOK_FROM_WISHLIST", {"hotelId": 9, "title": "H"}))
        criteria = BookFromWishlistEvent.ValidationCriteria(hotel_id=9, title="H")
        assert event.validate_criteria(criteria) is True
