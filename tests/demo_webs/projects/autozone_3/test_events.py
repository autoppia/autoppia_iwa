"""Unit tests for autozone_3 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p03_autozone.events import (
    BACKEND_EVENT_TYPES,
    SearchProductEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTOZONE_PAYLOADS = [
    ("CAROUSEL_SCROLL", {}),
    ("SEARCH_PRODUCT", {"query": "q"}),
    ("CATEGORY_FILTER", {}),
    ("VIEW_DETAIL", {}),
    ("DETAILS_TOGGLE", {}),
    ("ADD_TO_CART", {"price": 10.0, "quantity": 1}),
    ("ADD_TO_WISHLIST", {}),
    ("SHARE_PRODUCT", {}),
    ("VIEW_CART", {}),
    ("VIEW_WISHLIST", {}),
    ("QUANTITY_CHANGED", {}),
    ("PROCEED_TO_CHECKOUT", {}),
    ("CHECKOUT_STARTED", {}),
    ("ORDER_COMPLETED", {}),
]


@pytest.mark.parametrize("event_name,data", AUTOZONE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


def test_search_product_parse():
    e = SearchProductEvent.parse(_be("SEARCH_PRODUCT", {"query": "tires"}))
    assert e.query == "tires"
