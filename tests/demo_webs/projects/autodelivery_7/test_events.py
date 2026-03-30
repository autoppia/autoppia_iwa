"""Unit tests for autodelivery_7 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p07_autodelivery.events import (
    BACKEND_EVENT_TYPES,
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
