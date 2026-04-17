from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from autoppia_iwa.src.demo_webs.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

from ...shared_utils import parse_price


class ProductSummary(BaseModel):
    """Summary of a single product, used in lists within other events."""

    title: str
    price: float
    quantity: int = Field(default=1, ge=1)
    brand: str = Field(default="")
    category: str | None = None
    rating: float | None = None

    model_config = ConfigDict(frozen=True)

    @classmethod
    def parse_from_data(cls, data: dict[str, Any]) -> Optional["ProductSummary"]:
        """Parses a dictionary into a ProductSummary instance."""
        if not isinstance(data, dict) or not data.get("title"):
            return None

        try:
            price = parse_price(data.get("price"))

            return cls(
                title=str(data.get("title", "")),
                price=price,
                quantity=int(data.get("quantity", 1)),
                brand=str(data.get("brand", "")),
                category=data.get("category"),
                rating=data.get("rating"),
            )
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not parse ProductSummary data: {data}. Error: {e}")
            return None


class ItemDetailEvent(Event, BaseEventValidator):
    """Event triggered when an item detail page is viewed"""

    event_name: str = "VIEW_DETAIL"

    item_name: str
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None
    item_price: float | None = None

    class ValidationCriteria(BaseModel):
        """Validation criteria for ItemDetailEvent."""

        title: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        price: float | CriterionValue | None = None

        model_config = ConfigDict(
            title="Item Detail Validation",
            description="Validates that an item detail page was viewed with specific attributes",
        )

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.item_name, criteria.title),
                self._validate_field(self.item_category, criteria.category),
                self._validate_field(self.item_brand, criteria.brand),
                self._validate_field(self.item_rating, criteria.rating),
                self._validate_field(self.item_price, criteria.price),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ItemDetailEvent":
        """Parse an item detail event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data

        product_summary = ProductSummary.parse_from_data(data)

        if not product_summary:
            parsed_price = parse_price(data.get("price"))

            return cls(
                event_name=base_event.event_name,
                timestamp=base_event.timestamp,
                web_agent_id=base_event.web_agent_id,
                user_id=base_event.user_id,
                item_name=data.get("title", ""),
                item_category=data.get("category"),
                item_brand=data.get("brand"),
                item_rating=data.get("rating"),
                item_price=parsed_price,
            )
        else:
            # Use parsed ProductSummary data
            return cls(
                event_name=base_event.event_name,
                timestamp=base_event.timestamp,
                web_agent_id=base_event.web_agent_id,
                user_id=base_event.user_id,
                item_name=product_summary.title,
                item_category=product_summary.category,
                item_brand=product_summary.brand,
                item_rating=product_summary.rating,
                item_price=product_summary.price,
            )


class DetailsToggleEvent(ItemDetailEvent):
    """Event triggered when a detail section is toggled."""

    event_name: str = "DETAILS_TOGGLE"


class AddToWishlistEvent(ItemDetailEvent):
    """Event triggered when a user manages wishlist items."""

    event_name: str = "ADD_TO_WISHLIST"


class ShareProductEvent(ItemDetailEvent):
    """Event triggered when a user shares a product."""

    event_name: str = "SHARE_PRODUCT"


class ShareCompletedEvent(ItemDetailEvent):
    """Share flow completed (same payload as SHARE_PRODUCT with stage completed)."""

    event_name: str = "SHARE_COMPLETED"
    product_id: str | None = None
    stage: str | None = None
    recipient_name: str | None = None
    recipient_email: str | None = None

    class ValidationCriteria(ItemDetailEvent.ValidationCriteria):
        recipient_name: str | CriterionValue | None = None
        recipient_email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                ItemDetailEvent._validate_criteria(criteria),
                self._validate_field(self.recipient_name, criteria.recipient_name),
                self._validate_field(self.recipient_email, criteria.recipient_email),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ShareCompletedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        title = str(data.get("productTitle") or data.get("title") or "")
        product_summary = ProductSummary.parse_from_data(data)
        if product_summary:
            item_name = product_summary.title
            item_category = product_summary.category
            item_brand = product_summary.brand
            item_rating = product_summary.rating
            item_price = product_summary.price
        else:
            item_name = title
            item_category = data.get("category")
            item_brand = data.get("brand")
            item_rating = data.get("rating")
            item_price = parse_price(data.get("price")) if data.get("price") is not None else None
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            item_name=item_name,
            item_category=item_category,
            item_brand=item_brand,
            item_rating=item_rating,
            item_price=item_price,
            product_id=data.get("productId"),
            stage=data.get("stage"),
            recipient_name=data.get("recipientName"),
            recipient_email=data.get("recipientEmail"),
        )


def _parse_autozone_review_payload_fields(data: dict[str, Any]) -> dict[str, Any]:
    """
    Map web_3_autozone review logEvent payload onto event fields.

    Payload includes product context (productId, title, price, …) plus review fields:
    rating (review star rating), reviewerName, review (body text). reviewId is optional
    (e.g. omitted on some clients for REVIEW_CREATED).
    """
    body = data.get("review")
    rname = data.get("reviewerName")
    return {
        "review_rating": data.get("rating"),
        "reviewer_name": str(rname) if rname is not None else None,
        "review_body": str(body) if body is not None else None,
    }


class AutozoneReviewCreatedEvent(ItemDetailEvent):
    """Product review created (autozone). Registered via p04 multiplex for REVIEW_CREATED."""

    event_name: str = "REVIEW_CREATED"
    product_id: str | None = None
    review_id: str | None = None
    review_rating: float | int | None = None
    reviewer_name: str | None = None
    review_body: str | None = None

    class ValidationCriteria(ItemDetailEvent.ValidationCriteria):
        reviewer_name: str | CriterionValue | None = None
        review_body: str | CriterionValue | None = None
        review_rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                ItemDetailEvent._validate_criteria(criteria),
                self._validate_field(self.review_rating, criteria.review_rating),
                self._validate_field(self.reviewer_name, criteria.reviewer_name),
                self._validate_field(self.review_body, criteria.review_body),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AutozoneReviewCreatedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        product_summary = ProductSummary.parse_from_data(data)
        if product_summary:
            item_name = product_summary.title
            item_category = product_summary.category
            item_brand = product_summary.brand
            item_price = product_summary.price
        else:
            item_name = str(data.get("title", ""))
            item_category = data.get("category")
            item_brand = data.get("brand")
            item_price = parse_price(data.get("price")) if data.get("price") is not None else None
        extra = _parse_autozone_review_payload_fields(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            item_name=item_name,
            item_category=item_category,
            item_brand=item_brand,
            item_rating=None,
            item_price=item_price,
            product_id=data.get("productId"),
            review_id=data.get("reviewId"),
            **extra,
        )


class AutozoneReviewUpdatedEvent(AutozoneReviewCreatedEvent):
    """Product review updated (autozone)."""

    event_name: str = "REVIEW_UPDATED"


class AutozoneReviewDeletedEvent(AutozoneReviewCreatedEvent):
    """Product review deleted (autozone). Registered via p04 multiplex for REVIEW_DELETED."""

    event_name: str = "REVIEW_DELETED"


class SearchProductEvent(Event, BaseEventValidator):
    """Event triggered when a user searches for a product."""

    event_name: str = "SEARCH_PRODUCT"

    query: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating search product events."""

        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """
        Validate if this search event meets the criteria.
        """
        if not criteria:
            return True
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchProductEvent":
        """Parse a search product event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
        )


class CategoryFilterEvent(Event, BaseEventValidator):
    """Event triggered when a user applies a category filter."""

    event_name: str = "CATEGORY_FILTER"

    category: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating category filter events."""

        category: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all([self._validate_field(self.category, criteria.category)])

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CategoryFilterEvent":
        """Parse a category filter event."""
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            category=str(data.get("category", "")),
        )


class ProceedToCheckoutEvent(Event, BaseEventValidator):
    """Event triggered when a user proceeds to checkout."""

    event_name: str = "PROCEED_TO_CHECKOUT"

    total_items: int
    total_amount: float
    products: list[ProductSummary] = Field(default_factory=list)
    created_at: datetime

    class ValidationCriteria(BaseModel):
        """Criteria for validating a proceed-to-checkout event."""

        total_items: int | CriterionValue | None = None
        total_amount: float | CriterionValue | None = None
        product_titles: list[str] | None = None

        model_config = ConfigDict(extra="forbid")

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Validate the event against the given criteria."""
        if not criteria:
            return True

        product_names = {p.title.lower() for p in self.products} if criteria.product_titles else None

        return all(
            [
                self._validate_field(self.total_items, criteria.total_items),
                self._validate_field(self.total_amount, criteria.total_amount),
                (not criteria.product_titles or any(t.lower() in product_names for t in criteria.product_titles)),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ProceedToCheckoutEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        products_data = data.get("products", [])

        products = [
            ProductSummary(title=str(p.get("title", "")), price=parse_price(p.get("price", "")), quantity=int(p.get("quantity", 1)), brand=str(p.get("brand", "")))
            for p in products_data
            if isinstance(p, dict)
        ]

        created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else base_event.timestamp

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            total_items=int(data.get("total_items", 0)),
            total_amount=float(data.get("total_amount", 0.0)),
            products=products,
            created_at=created_at,
        )


class AddToCartEvent(Event, BaseEventValidator):
    """Event triggered when a user adds an item to the shopping cart."""

    event_name: str = "ADD_TO_CART"

    item_name: str
    item_price: float
    item_quantity: int
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating AddToCart events."""

        title: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None

        model_config = ConfigDict(populate_by_name=True)

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.item_name, criteria.title),
                self._validate_field(self.item_category, criteria.category),
                self._validate_field(self.item_brand, criteria.brand),
                self._validate_field(self.item_price, criteria.price),
                self._validate_field(self.item_rating, criteria.rating),
                self._validate_field(self.item_quantity, criteria.quantity),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AddToCartEvent":
        """Parse an add to cart event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data

        # Use ProductSummary parsing logic for consistency
        product_summary = ProductSummary.parse_from_data(data)

        if not product_summary:
            # Fallback if ProductSummary parsing fails
            price = None
            if "price" in data:
                price = parse_price(data["price"])
            quantity = int(data.get("quantity", 1))
            item_name = data.get("title", "")

            return cls(
                event_name=base_event.event_name,
                timestamp=base_event.timestamp,
                web_agent_id=base_event.web_agent_id,
                user_id=base_event.user_id,
                item_name=item_name,
                item_price=price,
                item_rating=data.get("rating"),
                item_quantity=quantity,
                item_category=data.get("category"),
                item_brand=data.get("brand"),
            )
        else:
            # Use parsed ProductSummary data
            return cls(
                event_name=base_event.event_name,
                timestamp=base_event.timestamp,
                web_agent_id=base_event.web_agent_id,
                user_id=base_event.user_id,
                item_name=product_summary.title,
                item_price=product_summary.price,
                item_rating=product_summary.rating,
                item_quantity=product_summary.quantity,
                item_category=product_summary.category,
                item_brand=product_summary.brand,
            )


class ViewCartEvent(Event, BaseEventValidator):
    """Event triggered when a user views the shopping cart."""

    event_name: str = "VIEW_CART"


class ViewWishlistEvent(Event, BaseEventValidator):
    """Event triggered when a user views wishlist content."""

    event_name: str = "VIEW_WISHLIST"


class QuantityChangedEvent(Event, BaseEventValidator):
    """Event triggered when a user changes item quantity in the shopping cart."""

    event_name: str = "QUANTITY_CHANGED"

    item_name: str
    previous_quantity: int
    new_quantity: int
    item_price: float | None = None
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating quantity change events."""

        title: str | CriterionValue | None = Field(default=None, alias="item_name")
        previous_quantity: int | CriterionValue | None = None
        new_quantity: int | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        rating: float | CriterionValue | None = None

        model_config = ConfigDict(populate_by_name=True)

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.item_name, criteria.title),
                self._validate_field(self.previous_quantity, criteria.previous_quantity),
                self._validate_field(self.new_quantity, criteria.new_quantity),
                self._validate_field(self.item_category, criteria.category),
                self._validate_field(self.item_brand, criteria.brand),
                self._validate_field(self.item_price, criteria.price),
                self._validate_field(self.item_rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "QuantityChangedEvent":
        """Parse a quantity changed event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data

        # Attempt to parse relevant fields, falling back if needed
        item_name = data.get("product_name", "")
        previous_quantity = int(data.get("previous_quantity", 0))
        new_quantity = int(data.get("new_quantity", 0))

        price = None
        if "price" in data:
            price = parse_price(data.get("price"))

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            item_name=item_name,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            item_price=price,
            item_category=data.get("category"),
            item_brand=data.get("brand"),
            item_rating=data.get("rating"),
        )


class OrderCompletedEvent(Event, BaseEventValidator):
    """Event triggered when a user completes an order."""

    event_name: str = "ORDER_COMPLETED"

    items: list[ProductSummary] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        """Criteria for validating order completion events."""

        items: list[ProductSummary] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria or criteria.items is None:
            return True

        # Case 1: Explicit list of ProductSummary items to match exactly
        if isinstance(criteria.items, list):
            for expected_item in criteria.items:
                match_found = any(i.title == expected_item.title and i.quantity == expected_item.quantity for i in self.items)
                if not match_found:
                    return False
            return True

        # Case 2: Flexible criterion (e.g. item with title="Watch", quantity > 1)
        elif isinstance(criteria.items, CriterionValue):
            expected = criteria.items.value
            operator = criteria.items.operator

            def matches(product: ProductSummary, operator: ComparisonOperator) -> bool:
                for key, expected_val in expected.items():
                    actual_val = getattr(product, key, None)
                    if not validate_criterion(actual_val, CriterionValue(value=expected_val, operator=operator)):
                        return False
                return True

            if operator == ComparisonOperator.CONTAINS:
                return any(matches(item, ComparisonOperator.CONTAINS) for item in self.items)
            elif operator == ComparisonOperator.NOT_CONTAINS:
                return all(matches(item, ComparisonOperator.NOT_CONTAINS) for item in self.items)
            elif operator == ComparisonOperator.IN_LIST:
                return any(matches(item, ComparisonOperator.IN_LIST) for item in self.items)
            elif operator == ComparisonOperator.NOT_IN_LIST:
                return all(matches(item, ComparisonOperator.NOT_IN_LIST) for item in self.items)
            elif operator == ComparisonOperator.EQUALS:
                # all items should match exactly once (used rarely)
                return all(matches(item, ComparisonOperator.EQUALS) for item in self.items)
            elif operator == ComparisonOperator.NOT_EQUALS:
                return all(matches(item, ComparisonOperator.NOT_EQUALS) for item in self.items)
            else:
                return False

        return False  # fallback

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "OrderCompletedEvent":
        """Parse an order completed event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        # Parse item summaries
        items_raw = data.get("items", [])
        items: list[ProductSummary] = []

        for item_data in items_raw:
            summary = ProductSummary.parse_from_data(item_data)
            if summary:
                items.append(summary)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            items=items,
        )


class CarouselScrollEvent(Event, BaseEventValidator):
    """Event triggered when a user scrolls a carousel."""

    event_name: str = "CAROUSEL_SCROLL"

    direction: str  # "LEFT" or "RIGHT"
    title: str  # Carousel section title

    class ValidationCriteria(BaseModel):
        """Criteria for validating carousel scroll events."""

        direction: str | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all([self._validate_field(self.direction, criteria.direction), self._validate_field(self.title, criteria.title)])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CarouselScrollEvent":
        """Parse a carousel scroll event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        derived_title = data.get("title", "")
        title = derived_title.split()[0] if derived_title else ""

        title = f"Top Sellers In {title}"

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            direction=data.get("direction", "").upper(),
            title=title,
        )


class CheckoutStartedEvent(Event, BaseEventValidator):
    """Event triggered when a user starts checkout."""

    event_name: str = "CHECKOUT_STARTED"

    item_name: str
    item_price: float
    item_quantity: int
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating checkout start events."""

        name: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.item_name, criteria.name),
                self._validate_field(self.item_category, criteria.category),
                self._validate_field(self.item_brand, criteria.brand),
                self._validate_field(self.item_price, criteria.price),
                self._validate_field(self.item_rating, criteria.rating),
                self._validate_field(self.item_quantity, criteria.quantity),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CheckoutStartedEvent":
        """Parse a checkout started event from backend data."""
        base_event = Event.parse(backend_event)
        data = backend_event.data
        ProductSummary.parse_from_data(data)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            item_name=data.get("title", ""),
            item_price=parse_price(data.get("price", 0.0)),
            item_quantity=int(data.get("quantity", 1)),
            item_category=data.get("category"),
            item_brand=data.get("brand"),
            item_rating=data.get("rating"),
        )


class AutozoneLoginBaseEvent(Event, BaseEventValidator):
    """User signed in (matches `EVENT_TYPES.LOGIN` → AUTOZONE_LOGIN)."""

    event_name: str = "AUTOZONE_LOGIN_BASE"
    username: str | None = None

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([self._validate_field(self.username, criteria.username)])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AutozoneLoginBaseEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            username=str(data["username"]) if data.get("username") is not None else None,
        )


class AutozoneLoginEvent(AutozoneLoginBaseEvent):
    """User signed in (matches `EVENT_TYPES.LOGIN` → AUTOZONE_LOGIN)."""

    event_name: str = "AUTOZONE_LOGIN"


class AutozoneRegisterEvent(AutozoneLoginBaseEvent):
    """New account registered (AUTOZONE_REGISTER)."""

    event_name: str = "AUTOZONE_REGISTER"


class AutozoneLogoutEvent(AutozoneLoginBaseEvent):
    """User logged out (AUTOZONE_LOGOUT)."""

    event_name: str = "AUTOZONE_LOGOUT"


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [
    AutozoneLoginEvent,
    AutozoneRegisterEvent,
    AutozoneLogoutEvent,
    ItemDetailEvent,
    DetailsToggleEvent,
    SearchProductEvent,
    CategoryFilterEvent,
    AddToCartEvent,
    AddToWishlistEvent,
    ShareProductEvent,
    ShareCompletedEvent,
    AutozoneReviewCreatedEvent,
    AutozoneReviewUpdatedEvent,
    AutozoneReviewDeletedEvent,
    ViewCartEvent,
    ViewWishlistEvent,
    QuantityChangedEvent,
    ProceedToCheckoutEvent,
    CheckoutStartedEvent,
    OrderCompletedEvent,
    CarouselScrollEvent,
]
BACKEND_EVENT_TYPES = {
    "AUTOZONE_LOGIN": AutozoneLoginEvent,
    "AUTOZONE_REGISTER": AutozoneRegisterEvent,
    "AUTOZONE_LOGOUT": AutozoneLogoutEvent,
    "CAROUSEL_SCROLL": CarouselScrollEvent,
    "SEARCH_PRODUCT": SearchProductEvent,
    "CATEGORY_FILTER": CategoryFilterEvent,
    "VIEW_DETAIL": ItemDetailEvent,
    "DETAILS_TOGGLE": DetailsToggleEvent,
    "ADD_TO_CART": AddToCartEvent,
    "ADD_TO_WISHLIST": AddToWishlistEvent,
    "SHARE_PRODUCT": ShareProductEvent,
    "SHARE_COMPLETED": ShareCompletedEvent,
    "REVIEW_CREATED": AutozoneReviewCreatedEvent,
    "REVIEW_UPDATED": AutozoneReviewUpdatedEvent,
    "REVIEW_DELETED": AutozoneReviewDeletedEvent,
    "VIEW_CART": ViewCartEvent,
    "VIEW_WISHLIST": ViewWishlistEvent,
    "QUANTITY_CHANGED": QuantityChangedEvent,
    "PROCEED_TO_CHECKOUT": ProceedToCheckoutEvent,
    "CHECKOUT_STARTED": CheckoutStartedEvent,
    "ORDER_COMPLETED": OrderCompletedEvent,
}
