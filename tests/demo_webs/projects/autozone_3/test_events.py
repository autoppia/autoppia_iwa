"""Unit tests for autozone_3 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.p03_autozone.events import (
    BACKEND_EVENT_TYPES,
    AddToCartEvent,
    AutozoneReviewCreatedEvent,
    AutozoneReviewDeletedEvent,
    AutozoneReviewUpdatedEvent,
    CarouselScrollEvent,
    CategoryFilterEvent,
    ItemDetailEvent,
    OrderCompletedEvent,
    ProceedToCheckoutEvent,
    ProductSummary,
    QuantityChangedEvent,
    SearchProductEvent,
    ShareCompletedEvent,
)
from autoppia_iwa.src.demo_webs.projects.p04_autodining.events import (
    DiningReviewCreatedEvent,
    DiningReviewDeletedEvent,
    ReviewCreatedRouterEvent,
    ReviewDeletedRouterEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTOZONE_PAYLOADS = [
    ("AUTOZONE_LOGIN", {}),
    ("AUTOZONE_REGISTER", {}),
    ("AUTOZONE_LOGOUT", {}),
    ("CAROUSEL_SCROLL", {}),
    ("SEARCH_PRODUCT", {"query": "q"}),
    ("CATEGORY_FILTER", {}),
    ("VIEW_DETAIL", {}),
    ("DETAILS_TOGGLE", {}),
    ("ADD_TO_CART", {"price": 10.0, "quantity": 1}),
    ("ADD_TO_WISHLIST", {}),
    ("SHARE_PRODUCT", {}),
    (
        "SHARE_COMPLETED",
        {"productId": "p1", "productTitle": "Kettle", "title": "Kettle", "shareUrl": "http://x", "recipientName": "A", "recipientEmail": "a@b.com", "stage": "completed", "price": 10.0},
    ),
    (
        "REVIEW_CREATED",
        {
            "title": "Mug",
            "productId": "p-mug",
            "reviewId": "rv0",
            "rating": 5,
            "price": 9.0,
            "reviewerName": "Alex",
            "review": "Great mug.",
        },
    ),
    (
        "REVIEW_UPDATED",
        {
            "title": "Oil",
            "productId": "p-oil",
            "reviewId": "r1",
            "rating": 4,
            "price": 5.0,
            "reviewerName": "Sam",
            "review": "Updated text.",
        },
    ),
    (
        "REVIEW_DELETED",
        {
            "title": "Mug",
            "productId": "p-mug",
            "reviewId": "rv9",
            "rating": 5,
            "price": 9.0,
            "reviewerName": "Alex",
            "review": "Deleted review body.",
        },
    ),
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


def test_autozone_review_events_parse():
    created = AutozoneReviewCreatedEvent.parse(
        _be(
            "REVIEW_CREATED",
            {
                "title": "Mug",
                "productId": "m1",
                "reviewId": "rv1",
                "rating": 5,
                "price": 9.0,
                "reviewerName": "Jordan",
                "review": "Solid purchase.",
            },
        )
    )
    assert created.product_id == "m1"
    assert created.review_id == "rv1"
    assert created.review_rating == 5
    assert created.reviewer_name == "Jordan"
    assert created.review_body == "Solid purchase."
    updated = AutozoneReviewUpdatedEvent.parse(
        _be(
            "REVIEW_UPDATED",
            {
                "title": "Mug",
                "productId": "m1",
                "reviewId": "rv1",
                "rating": 3,
                "price": 9.0,
                "reviewerName": "Jordan",
                "review": "Edited comment.",
            },
        )
    )
    assert updated.review_rating == 3
    assert updated.reviewer_name == "Jordan"
    assert updated.review_body == "Edited comment."
    deleted = AutozoneReviewDeletedEvent.parse(
        _be(
            "REVIEW_DELETED",
            {
                "title": "Mug",
                "productId": "m1",
                "reviewId": "rv1",
                "rating": 3,
                "price": 9.0,
                "reviewerName": "Jordan",
                "review": "Edited comment.",
            },
        )
    )
    assert deleted.review_id == "rv1"
    assert deleted.review_rating == 3
    assert deleted.reviewer_name == "Jordan"
    assert deleted.review_body == "Edited comment."


def test_share_completed_parse():
    e = ShareCompletedEvent.parse(
        _be(
            "SHARE_COMPLETED",
            {
                "productId": "p1",
                "productTitle": "Mixer",
                "title": "Mixer",
                "shareUrl": "https://example.com/p1",
                "recipientName": "Sam",
                "recipientEmail": "sam@example.com",
                "stage": "completed",
                "price": 20.0,
            },
        )
    )
    assert e.stage == "completed"
    assert e.recipient_email == "sam@example.com"


def test_review_created_router_autozone_vs_dining():
    auto = ReviewCreatedRouterEvent.parse(
        _be(
            "REVIEW_CREATED",
            {
                "title": "X",
                "productId": "p",
                "reviewId": "r",
                "rating": 5,
                "price": 1.0,
                "reviewerName": "U",
                "review": "Hi",
            },
        )
    )
    assert isinstance(auto, AutozoneReviewCreatedEvent)
    dining = ReviewCreatedRouterEvent.parse(
        _be(
            "REVIEW_CREATED",
            {"review_id": "r2", "restaurant_id": "rest1", "username": "u", "rating": 4, "comment_length": 10},
        )
    )
    assert isinstance(dining, DiningReviewCreatedEvent)


def test_review_deleted_router_autozone_vs_dining():
    auto = ReviewDeletedRouterEvent.parse(
        _be(
            "REVIEW_DELETED",
            {
                "title": "X",
                "productId": "p",
                "reviewId": "r",
                "rating": 4,
                "price": 1.0,
                "reviewerName": "U",
                "review": "Bye",
            },
        )
    )
    assert isinstance(auto, AutozoneReviewDeletedEvent)
    dining = ReviewDeletedRouterEvent.parse(_be("REVIEW_DELETED", {"review_id": "r2", "restaurant_id": "rest1", "username": "u"}))
    assert isinstance(dining, DiningReviewDeletedEvent)


def test_product_summary_parse_from_data_valid_and_invalid(capsys):
    valid = ProductSummary.parse_from_data({"title": "Wheel", "price": "$19.99", "quantity": "2", "brand": "ACME"})
    invalid = ProductSummary.parse_from_data({"price": "bad"})
    broken = ProductSummary.parse_from_data({"title": "Wheel", "price": object()})
    assert valid.title == "Wheel"
    assert valid.quantity == 2
    assert invalid is None
    assert broken is None
    assert "Could not parse ProductSummary" in capsys.readouterr().out


def test_item_detail_event_validate_with_fallback_price_parse():
    event = ItemDetailEvent.parse(_be("VIEW_DETAIL", {"title": "Battery", "price": "$12.50", "brand": "ACME", "category": "Tools", "rating": 4.8}))
    criteria = ItemDetailEvent.ValidationCriteria(title="Battery", brand="ACME", category="Tools", price=12.5, rating=4.8)
    assert event.validate_criteria(criteria) is True


def test_category_filter_and_add_to_cart_validation():
    filter_event = CategoryFilterEvent.parse(_be("CATEGORY_FILTER", {"category": "Engine"}))
    cart_event = AddToCartEvent.parse(_be("ADD_TO_CART", {"title": "Oil", "price": "$7.50", "quantity": 2, "brand": "Mobil", "category": "Fluids", "rating": 4.0}))
    assert filter_event.validate_criteria(CategoryFilterEvent.ValidationCriteria(category="Engine")) is True
    assert cart_event.validate_criteria(AddToCartEvent.ValidationCriteria(title="Oil", price=7.5, quantity=2, brand="Mobil", category="Fluids", rating=4.0))


def test_proceed_to_checkout_product_titles_and_created_at():
    event = ProceedToCheckoutEvent.parse(
        _be(
            "PROCEED_TO_CHECKOUT",
            {
                "total_items": 2,
                "total_amount": 25.5,
                "created_at": "2025-03-01T10:00:00",
                "products": [{"title": "Brake", "price": "$25.50", "quantity": 2, "brand": "Brembo"}],
            },
        )
    )
    criteria = ProceedToCheckoutEvent.ValidationCriteria(total_items=2, total_amount=25.5, product_titles=["Brake"])
    assert event.validate_criteria(criteria) is True


def test_quantity_changed_and_carousel_scroll_validation():
    qty_event = QuantityChangedEvent.parse(_be("QUANTITY_CHANGED", {"product_name": "Wheel", "previous_quantity": 1, "new_quantity": 3, "price": "$9.99", "brand": "ACME", "category": "Tires"}))
    scroll = CarouselScrollEvent.parse(_be("CAROUSEL_SCROLL", {"direction": "LEFT"}))
    assert qty_event.validate_criteria(QuantityChangedEvent.ValidationCriteria(item_name="Wheel", previous_quantity=1, new_quantity=3, price=9.99, brand="ACME", category="Tires"))
    assert scroll.validate_criteria(CarouselScrollEvent.ValidationCriteria(direction="LEFT")) is True


def test_order_completed_validation_with_list_and_criterion_value():
    event = OrderCompletedEvent.parse(
        _be(
            "ORDER_COMPLETED",
            {
                "items": [
                    {"title": "Wheel", "price": "$10.00", "quantity": 2, "brand": "ACME"},
                    {"title": "Oil", "price": "$5.00", "quantity": 1, "brand": "Mobil"},
                ]
            },
        )
    )
    list_criteria = OrderCompletedEvent.ValidationCriteria(items=[ProductSummary(title="Wheel", price=10.0, quantity=2, brand="ACME")])
    flex_criteria = OrderCompletedEvent.ValidationCriteria(items=CriterionValue(operator=ComparisonOperator.CONTAINS, value={"title": "Wheel"}))
    assert event.validate_criteria(list_criteria) is True
    assert event.validate_criteria(flex_criteria) is True


def test_additional_negative_and_fallback_paths():
    assert ProductSummary.parse_from_data({"title": "Wheel", "price": "$10.00", "quantity": 0}) is None

    detail_fallback = ItemDetailEvent.parse(_be("VIEW_DETAIL", {"title": "Battery", "price": "$12.50", "brand": "ACME", "category": "Tools", "rating": 4.8}))
    detail_summary = ItemDetailEvent.parse(_be("VIEW_DETAIL", {"title": "Wheel", "price": "$19.99", "quantity": 2, "brand": "ACME", "category": "Tires", "rating": 4.5}))
    assert detail_fallback.validate_criteria(ItemDetailEvent.ValidationCriteria(title="Other")) is False
    assert detail_summary.validate_criteria(ItemDetailEvent.ValidationCriteria(brand="Other")) is False

    search = SearchProductEvent.parse(_be("SEARCH_PRODUCT", {"query": "tires"}))
    assert search.validate_criteria(SearchProductEvent.ValidationCriteria(query="oil")) is False

    category = CategoryFilterEvent.parse(_be("CATEGORY_FILTER", {"category": "Engine"}))
    assert category.validate_criteria(CategoryFilterEvent.ValidationCriteria(category="Brakes")) is False

    cart_fallback = AddToCartEvent.parse(_be("ADD_TO_CART", {"title": "Oil", "price": "$7.50", "quantity": 2, "brand": "Mobil", "category": "Fluids", "rating": 4.0}))
    cart_summary = AddToCartEvent.parse(_be("ADD_TO_CART", {"title": "Wheel", "price": "$19.99", "quantity": 2, "brand": "ACME", "category": "Tires", "rating": 4.5}))
    assert cart_fallback.validate_criteria(AddToCartEvent.ValidationCriteria(title="Other")) is False
    assert cart_summary.validate_criteria(AddToCartEvent.ValidationCriteria(quantity=3)) is False

    checkout = ProceedToCheckoutEvent.parse(
        _be(
            "PROCEED_TO_CHECKOUT",
            {
                "total_items": 2,
                "total_amount": 25.5,
                "products": [{"title": "Brake", "price": "$25.50", "quantity": 2, "brand": "Brembo"}],
            },
        )
    )
    assert checkout.validate_criteria(ProceedToCheckoutEvent.ValidationCriteria(product_titles=["Other"])) is False

    quantity = QuantityChangedEvent.parse(_be("QUANTITY_CHANGED", {"product_name": "Wheel", "previous_quantity": 1, "new_quantity": 3, "price": "$9.99", "brand": "ACME", "category": "Tires"}))
    assert quantity.validate_criteria(QuantityChangedEvent.ValidationCriteria(previous_quantity=2)) is False

    scroll = CarouselScrollEvent.parse(_be("CAROUSEL_SCROLL", {"direction": "LEFT"}))
    assert scroll.validate_criteria(CarouselScrollEvent.ValidationCriteria(direction="RIGHT")) is False

    order = OrderCompletedEvent.parse(
        _be(
            "ORDER_COMPLETED",
            {
                "items": [
                    {"title": "Wheel", "price": "$10.00", "quantity": 2, "brand": "ACME"},
                    {"title": "Oil", "price": "$5.00", "quantity": 1, "brand": "Mobil"},
                ]
            },
        )
    )
    mismatch_list = OrderCompletedEvent.ValidationCriteria(items=[ProductSummary(title="Battery", price=10.0, quantity=1, brand="ACME")])
    mismatch_flex = OrderCompletedEvent.ValidationCriteria(items=CriterionValue(operator=ComparisonOperator.CONTAINS, value={"title": "Battery"}))
    assert order.validate_criteria(mismatch_list) is False
    assert order.validate_criteria(mismatch_flex) is False
