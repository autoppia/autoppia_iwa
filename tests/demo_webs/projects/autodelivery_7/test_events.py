"""Unit tests for autodelivery_7 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.p07_autodelivery.events import (
    BACKEND_EVENT_TYPES,
    AddressAddedEvent,
    DeliveryPrioritySelectedEvent,
    DropoffPreferenceEvent,
    OpenCheckoutPageEvent,
    PlaceOrderEvent,
    RestaurantFilterEvent,
    ReviewSubmittedEvent,
    SearchRestaurantEvent,
    ViewAllRestaurantsEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Minimal payloads: events that need only .get with defaults work with {}
# Events that need list of CheckoutItem use items=[]
CHECKOUT_ITEMS = []

AUTODELIVERY_PAYLOADS = [
    ("SEARCH_DELIVERY_RESTAURANT", {"query": "pizza"}),
    ("VIEW_DELIVERY_RESTAURANT", {"name": "R", "cuisine": "Italian", "rating": 4.5}),
    ("RESTAURANT_FILTER", {}),
    ("ADD_TO_CART_MODAL_OPEN", {"restaurantName": "R", "itemName": "I", "itemPrice": 10.0}),
    ("ITEM_INCREMENTED", {"itemName": "I", "newQuantity": 1}),
    ("ADD_TO_CART_MENU_ITEM", {"itemName": "I", "basePrice": 10.0, "restaurantName": "R"}),
    ("OPEN_CHECKOUT_PAGE", {"items": CHECKOUT_ITEMS}),
    ("DROPOFF_PREFERENCE", {"selectedPreference": "door", "restaurantName": "R", "items": CHECKOUT_ITEMS}),
    ("PLACE_ORDER", {"name": "U", "phone": "1", "address": "A", "dropoff": "door", "items": CHECKOUT_ITEMS, "mode": "", "total": 0.0}),
    ("EMPTY_CART", {"itemName": "I", "price": 0.0, "quantity": 0, "restaurantName": "R"}),
    ("DELETE_REVIEW", {"author": "A", "rating": 5, "comment": "c", "restaurantName": "R"}),
    ("BACK_TO_ALL_RESTAURANTS", {"fromRestaurantName": ""}),
    ("ADDRESS_ADDED", {"address": "A", "restaurantName": "R", "items": CHECKOUT_ITEMS, "mode": "", "totalPrice": 0.0}),
    ("QUICK_ORDER_STARTED", {}),
    ("QUICK_REORDER", {"itemName": "I", "restaurantName": "R"}),
    ("VIEW_ALL_RESTAURANTS", {}),
    ("EDIT_CART_ITEM", {"itemName": "I", "restaurantName": "R"}),
    ("RESTAURANT_NEXT_PAGE", {}),
    ("RESTAURANT_PREV_PAGE", {}),
    ("REVIEW_SUBMITTED", {"author": "A", "restaurantName": "R", "cuisine": "Italian", "restaurantRating": 4.5}),
    ("DELIVERY_PRIORITY_SELECTED", {"priority": "fast", "items": CHECKOUT_ITEMS}),
]


class TestParseAutodeliveryEvents:
    def test_search_restaurant_parse(self):
        e = SearchRestaurantEvent.parse(_be("SEARCH_DELIVERY_RESTAURANT", {"query": "pizza"}))
        assert e.query == "pizza"

    def test_view_all_restaurants_parse(self):
        e = ViewAllRestaurantsEvent.parse(_be("VIEW_ALL_RESTAURANTS", {}))
        assert e.event_name == "VIEW_ALL_RESTAURANTS"


@pytest.mark.parametrize("event_name,data", AUTODELIVERY_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


def test_restaurant_filter_validate_without_criteria():
    event = RestaurantFilterEvent.parse(_be("RESTAURANT_FILTER", {"cuisine": "Thai", "rating": 4.5}))
    assert event._validate_criteria(None) is True


def test_open_checkout_page_validate_matches_item():
    event = OpenCheckoutPageEvent.parse(_be("OPEN_CHECKOUT_PAGE", {"items": [{"name": "Pizza", "quantity": 2, "price": 15.0}]}))
    criteria = OpenCheckoutPageEvent.ValidationCriteria(item="Pizza", quantity=2, price=15.0)
    assert event._validate_criteria(criteria) is True


def test_open_checkout_page_validate_fails_for_empty_items():
    event = OpenCheckoutPageEvent.parse(_be("OPEN_CHECKOUT_PAGE", {"items": []}))
    criteria = OpenCheckoutPageEvent.ValidationCriteria(item="Pizza")
    assert event._validate_criteria(criteria) is False


def test_dropoff_preference_validate_base_only():
    event = DropoffPreferenceEvent.parse(
        _be(
            "DROPOFF_PREFERENCE",
            {"selectedPreference": "door", "restaurantName": "Roma", "items": [{"name": "Pasta", "quantity": 1, "price": 12.0}]},
        )
    )
    criteria = DropoffPreferenceEvent.ValidationCriteria(delivery_preference="door", restaurant="Roma")
    assert event._validate_criteria(criteria) is True


def test_dropoff_preference_validate_item_mismatch():
    event = DropoffPreferenceEvent.parse(
        _be(
            "DROPOFF_PREFERENCE",
            {"selectedPreference": "door", "restaurantName": "Roma", "items": [{"name": "Pasta", "quantity": 1, "price": 12.0}]},
        )
    )
    criteria = DropoffPreferenceEvent.ValidationCriteria(delivery_preference="door", restaurant="Roma", item="Burger")
    assert event._validate_criteria(criteria) is False


def test_place_order_validate_matches_all_fields():
    event = PlaceOrderEvent.parse(
        _be(
            "PLACE_ORDER",
            {
                "name": "Alice",
                "phone": "123",
                "address": "Main St",
                "dropoff": "door",
                "mode": "delivery",
                "total": 19.5,
                "items": [{"name": "Pizza", "quantity": 2, "price": 9.75}],
            },
        )
    )
    criteria = PlaceOrderEvent.ValidationCriteria(
        username="Alice",
        phone="123",
        address="Main St",
        delivery_preference="door",
        mode="delivery",
        total=19.5,
        item="Pizza",
        quantity=2,
        price=9.75,
    )
    assert event._validate_criteria(criteria) is True


def test_address_added_validate_matches_item_and_totals():
    event = AddressAddedEvent.parse(
        _be(
            "ADDRESS_ADDED",
            {
                "address": "Main St",
                "mode": "delivery",
                "restaurantName": "Roma",
                "totalPrice": 15.0,
                "items": [{"name": "Pizza", "quantity": 1, "price": 15.0}],
            },
        )
    )
    criteria = AddressAddedEvent.ValidationCriteria(
        address="Main St",
        mode="delivery",
        restaurant="Roma",
        total_price=15.0,
        item="Pizza",
        quantity=1,
        price=15.0,
    )
    assert event._validate_criteria(criteria) is True


def test_review_submitted_validate_criterion_value():
    event = ReviewSubmittedEvent.parse(
        _be(
            "REVIEW_SUBMITTED",
            {
                "author": "Bob",
                "rating": 5,
                "comment": "Great",
                "restaurantName": "Roma",
                "restaurantRating": 4.5,
                "cuisine": "Italian",
            },
        )
    )
    criteria = ReviewSubmittedEvent.ValidationCriteria(
        author=CriterionValue(operator="equals", value="Bob"),
        rating=5,
        restaurant_name="Roma",
        cuisine="Italian",
        comment="Great",
        restaurant_rating=4.5,
    )
    assert event._validate_criteria(criteria) is True


def test_delivery_priority_selected_validate_and_parse():
    event = DeliveryPrioritySelectedEvent.parse(_be("DELIVERY_PRIORITY_SELECTED", {"priority": "fast", "items": [{"name": "Pizza", "quantity": 1, "price": 10.0}]}))
    criteria = DeliveryPrioritySelectedEvent.ValidationCriteria(priority="fast", item="Pizza", quantity=1, price=10.0)
    assert event._validate_criteria(criteria) is True
