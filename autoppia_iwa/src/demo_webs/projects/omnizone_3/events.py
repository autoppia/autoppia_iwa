from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue, validate_criterion

from ..shared_utils import parse_price


class ProductSummary(BaseModel):
    """Summary of a single product, used in lists within other events."""

    id: str
    title: str
    price: float
    quantity: int = Field(default=1, ge=1)
    brand: str = Field(default="")
    category: str | None = None
    rating: float | None = None

    class Config:
        frozen = True

    @classmethod
    def parse_from_data(cls, data: dict[str, Any]) -> Optional["ProductSummary"]:
        """Parses a dictionary into a ProductSummary instance."""
        if not isinstance(data, dict) or not data.get("title"):
            return None

        try:
            price = parse_price(data.get("price"))

            return cls(
                id=data.get("productId"),
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

    # item_id: str
    item_name: str
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None
    item_price: float | None = None

    class ValidationCriteria(BaseModel):
        """Validation criteria for ItemDetailEvent."""

        # id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        price: float | CriterionValue | None = None

        class Config:
            title = "Item Detail Validation"
            description = "Validates that an item detail page was viewed with specific attributes"

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                # self._validate_field(self.item_id, criteria.id),
                self._validate_field(self.item_name, criteria.name),
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
                # item_id=data.get("productId"),
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
                # item_id=product_summary.id,
            )


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

        class Config:
            extra = "forbid"  # Prevent extra fields

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
            ProductSummary(id=str(p.get("id", "")), title=str(p.get("title", "")), price=parse_price(p.get("price", "")), quantity=int(p.get("quantity", 1)), brand=str(p.get("brand", "")))
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

    item_id: str
    item_name: str
    item_price: float
    item_quantity: int
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating AddToCart events."""

        id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None

        class Config:
            populate_by_name = True

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.item_id, criteria.id),
                self._validate_field(self.item_name, criteria.name),
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
                item_id=data.get("productId", ""),
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
                item_id=product_summary.id,
            )


class ViewCartEvent(Event, BaseEventValidator):
    """Event triggered when a user views the shopping cart."""

    event_name: str = "VIEW_CART"

    class ValidationCriteria(BaseModel):
        """Empty criteria for view cart events (no specific validation needed)."""

        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewCartEvent":
        """Parse a view cart event from backend data."""
        base_event = Event.parse(backend_event)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
        )


class QuantityChangedEvent(Event, BaseEventValidator):
    """Event triggered when a user changes item quantity in the shopping cart."""

    event_name: str = "QUANTITY_CHANGED"

    # item_id: str
    item_name: str
    previous_quantity: int
    new_quantity: int
    item_price: float | None = None
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None
    # created_at: datetime = Field(default_factory=datetime.now)
    # updated_at: datetime = Field(default_factory=datetime.now)

    class ValidationCriteria(BaseModel):
        """Criteria for validating quantity change events."""

        # id: str | CriterionValue | None
        name: str | CriterionValue | None = Field(default=None, alias="item_name")
        previous_quantity: int | CriterionValue | None = None
        new_quantity: int | CriterionValue | None = None
        category: str | CriterionValue | None = None
        brand: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        # created_at: datetime | CriterionValue | None = None
        # updated_at: datetime | CriterionValue | None = None

        class Config:
            populate_by_name = True

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                # self._validate_field(self.item_id, criteria.id),
                self._validate_field(self.item_name, criteria.name),
                self._validate_field(self.previous_quantity, criteria.previous_quantity),
                self._validate_field(self.new_quantity, criteria.new_quantity),
                self._validate_field(self.item_category, criteria.category),
                self._validate_field(self.item_brand, criteria.brand),
                self._validate_field(self.item_price, criteria.price),
                self._validate_field(self.item_rating, criteria.rating),
                # self._validate_field(self.created_at, criteria.created_at),
                # self._validate_field(self.updated_at, criteria.updated_at),
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

        # Pydantic will handle datetime parsing if input is str in ISO format
        # created_at = data.get("created_at")
        # updated_at = data.get("updated_at")
        # if isinstance(created_at, str):
        #     try:
        #         created_at = datetime.fromisoformat(created_at)
        #     except ValueError:
        #         created_at = base_event.timestamp
        # if isinstance(updated_at, str):
        #     try:
        #         updated_at = datetime.fromisoformat(updated_at)
        #     except ValueError:
        #         updated_at = datetime.now()

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
            # created_at=created_at,
            # updated_at=updated_at,
            # item_id=data.get("productId", ""),
        )


class OrderCompletedEvent(Event, BaseEventValidator):
    """Event triggered when a user completes an order."""

    event_name: str = "ORDER_COMPLETED"

    items: list[ProductSummary] = Field(default_factory=list)
    # total_amount: float
    # tax: float
    # shipping: float
    # order_total: float

    class ValidationCriteria(BaseModel):
        """Criteria for validating order completion events."""

        items: list[ProductSummary] | CriterionValue | None = None
        # total_amount: float | CriterionValue | None = None
        # tax: float | CriterionValue | None = None
        # shipping: float | CriterionValue | None = None
        # order_total: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria or criteria.items is None:
            return True

        # Case 1: Explicit list of ProductSummary items to match exactly
        if isinstance(criteria.items, list):
            for expected_item in criteria.items:
                match_found = any(i.title == expected_item.title and i.quantity == expected_item.quantity and (i.id == expected_item.id if expected_item.id else True) for i in self.items)
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

        # Extract numeric totals
        # total_amount = float(data.get("totalAmount", 0.0))
        # tax = float(data.get("tax", 0.0))
        # shipping = float(data.get("shipping", 0.0))
        # order_total = float(data.get("orderTotal", 0.0))
        # total_items = int(data.get("totalItems", 0))

        # Parse item summaries
        items_raw = data.get("items", [])
        items: list[ProductSummary] = []

        for item_data in items_raw:
            summary = ProductSummary.parse_from_data({**item_data, "productId": item_data.get("id")})
            if summary:
                items.append(summary)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # total_amount=total_amount,
            # tax=tax,
            # shipping=shipping,
            # order_total=order_total,
            # total_items=total_items,
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

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            direction=data.get("direction", "").upper(),
            title=data.get("title", ""),
        )


class CheckoutStartedEvent(Event, BaseEventValidator):
    """Event triggered when a user starts checkout."""

    event_name: str = "CHECKOUT_STARTED"

    item_id: str
    item_name: str
    item_price: float
    item_quantity: int
    item_category: str | None = None
    item_brand: str | None = None
    item_rating: float | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating checkout start events."""

        id: str | CriterionValue | None = None
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
                self._validate_field(self.item_id, criteria.id),
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
            item_id=data.get("productId", ""),
            item_name=data.get("title", ""),
            item_price=parse_price(data.get("price", 0.0)),
            item_quantity=int(data.get("quantity", 1)),
            item_category=data.get("category"),
            item_brand=data.get("brand"),
            item_rating=data.get("rating"),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================


EVENTS = [
    ItemDetailEvent,
    SearchProductEvent,
    QuantityChangedEvent,
    AddToCartEvent,
    ViewCartEvent,
    ProceedToCheckoutEvent,
    OrderCompletedEvent,
    CarouselScrollEvent,
    CheckoutStartedEvent,
]
BACKEND_EVENT_TYPES = {
    "CAROUSEL_SCROLL": CarouselScrollEvent,
    "SEARCH_PRODUCT": SearchProductEvent,
    "VIEW_DETAIL": ItemDetailEvent,
    "ADD_TO_CART": AddToCartEvent,
    "CHECKOUT_STARTED": CheckoutStartedEvent,
    "VIEW_CART": ViewCartEvent,
    "QUANTITY_CHANGED": QuantityChangedEvent,
    "PROCEED_TO_CHECKOUT": ProceedToCheckoutEvent,
    "ORDER_COMPLETED": OrderCompletedEvent,
}
