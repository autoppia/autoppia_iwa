from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class SearchRestaurantEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_DELIVERY_RESTAURANT"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchRestaurantEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            query=backend_event.data.get("query", ""),
        )


class ViewRestaurantEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_DELIVERY_RESTAURANT"
    name: str
    cuisine: str
    rating: float

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.cuisine, criteria.cuisine),
                self._validate_field(self.rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewRestaurantEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            name=data.get("name", ""),
            cuisine=data.get("cuisine", ""),
            rating=float(data.get("rating", 0.0)),
        )


class RestaurantFilterEvent(Event, BaseEventValidator):
    event_name: str = "RESTAURANT_FILTER"
    cuisine: str | None = None
    rating: float | None = None

    class ValidationCriteria(BaseModel):
        cuisine: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.cuisine, criteria.cuisine),
                self._validate_field(self.rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "RestaurantFilterEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            cuisine=data.get("cuisine"),
            rating=float(data.get("rating", 0)) if data.get("rating") is not None else None,
        )


class AddToCartModalOpenEvent(Event, BaseEventValidator):
    event_name: str = "ADD_TO_CART_MODAL_OPEN"
    restaurant: str
    item: str
    price: float

    class ValidationCriteria(BaseModel):
        restaurant: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant, criteria.restaurant),
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.price, criteria.price),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddToCartModalOpenEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            restaurant=data.get("restaurantName", ""),
            item=data.get("itemName", ""),
            price=data.get("itemPrice", 0.0),
        )


class ItemIncrementedEvent(Event, BaseEventValidator):
    event_name: str = "ITEM_INCREMENTED"
    item: str
    new_quantity: int

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        new_quantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.new_quantity, criteria.new_quantity),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ItemIncrementedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            item=data.get("itemName", ""),
            new_quantity=data.get("newQuantity", 0),
        )


class AddToCartEvent(Event, BaseEventValidator):
    event_name: str = "ADD_TO_CART_MENU_ITEM"
    item: str
    price: float
    size: str
    restaurant: str
    preferences: str
    quantity: int
    total_price: float

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        size: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        preferences: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        total_price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.size, criteria.size),
                self._validate_field(self.restaurant, criteria.restaurant),
                self._validate_field(self.preferences, criteria.preferences),
                self._validate_field(self.quantity, criteria.quantity),
                self._validate_field(self.total_price, criteria.total_price),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddToCartEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            item=data.get("itemName", ""),
            price=data.get("basePrice", 0.0),
            size=data.get("size", ""),
            restaurant=data.get("restaurantName", ""),
            preferences=data.get("preferences", ""),
            quantity=data.get("quantity", 0),
            total_price=data.get("totalPrice", 0.0),
        )


class CheckoutItem(BaseModel):
    name: str
    quantity: int
    price: float
    # size: str | None = None
    # preferences: list[str] | None = None


class OpenCheckoutPageEvent(Event, BaseEventValidator):
    event_name: str = "OPEN_CHECKOUT_PAGE"
    items: list[CheckoutItem]

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        if len(self.items) == 0:
            return False

        for item in self.items:
            if self._validate_field(item.name, criteria.item) and self._validate_field(item.quantity, criteria.quantity) and self._validate_field(item.price, criteria.price):
                return True
        return False

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "OpenCheckoutPageEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        items = [CheckoutItem(**item) for item in data.get("items", [])]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            items=items,
        )


class QuickOrderStartedEvent(Event, BaseEventValidator):
    event_name: str = "QUICK_ORDER_STARTED"


class QuickReorderEvent(Event, BaseEventValidator):
    event_name: str = "QUICK_REORDER"
    item: str
    restaurant: str

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.restaurant, criteria.restaurant),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "QuickReorderEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            item=data.get("itemName", ""),
            restaurant=data.get("restaurantName", ""),
        )


class ViewAllRestaurantsEvent(Event, BaseEventValidator):
    """Event triggered when user goes back to all restaurants list."""

    event_name: str = "VIEW_ALL_RESTAURANTS"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewAllRestaurantsEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
        )


class EditCartItemEvent(Event, BaseEventValidator):
    """Event triggered when editing an item from the cart."""

    event_name: str = "EDIT_CART_ITEM"
    item: str
    restaurant: str | None = None

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.restaurant, criteria.restaurant),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditCartItemEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            item=data.get("itemName", ""),
            restaurant=data.get("restaurantName"),
        )


class DropoffPreferenceEvent(Event, BaseEventValidator):
    event_name: str = "DROPOFF_PREFERENCE"
    delivery_preference: str
    restaurant: str
    items: list[CheckoutItem]

    class ValidationCriteria(BaseModel):
        delivery_preference: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        base_validation = all(
            [
                self._validate_field(self.delivery_preference, criteria.delivery_preference),
                self._validate_field(self.restaurant, criteria.restaurant),
            ]
        )

        if not base_validation:
            return False

        if criteria.item is None and criteria.price is None and criteria.quantity is None:
            return True

        for item in self.items:
            if self._validate_field(item.name, criteria.item) and self._validate_field(item.price, criteria.price) and self._validate_field(item.quantity, criteria.quantity):
                return True
        return False

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DropoffPreferenceEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        items = [CheckoutItem(**item) for item in data.get("items", [])]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            delivery_preference=data.get("selectedPreference", ""),
            restaurant=data.get("restaurantName", ""),
            items=items,
        )


class PlaceOrderEvent(Event, BaseEventValidator):
    event_name: str = "PLACE_ORDER"
    username: str
    phone: str
    address: str
    delivery_preference: str
    items: list[CheckoutItem]
    mode: str
    total: float

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None
        phone: str | CriterionValue | None = None
        address: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        mode: str | CriterionValue | None = None
        delivery_preference: str | CriterionValue | None = None
        total: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        base_validation = all(
            [
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.phone, criteria.phone),
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.delivery_preference, criteria.delivery_preference),
                self._validate_field(self.mode, criteria.mode),
                self._validate_field(self.total, criteria.total),
            ]
        )

        if not base_validation:
            return False

        if criteria.item is None and criteria.price is None and criteria.quantity is None:
            return True

        for item in self.items:
            if self._validate_field(item.name, criteria.item) and self._validate_field(item.price, criteria.price) and self._validate_field(item.quantity, criteria.quantity):
                return True
        return False

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PlaceOrderEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        items = [CheckoutItem(**item) for item in data.get("items", [])]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            username=data.get("name", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            delivery_preference=data.get("dropoff", ""),
            mode=data.get("mode", ""),
            items=items,
            total=data.get("total", 0.0),
        )


class EmptyCartEvent(Event, BaseEventValidator):
    event_name: str = "EMPTY_CART"
    item: str
    price: float
    quantity: int
    restaurant: str
    # cartTotal: float

    class ValidationCriteria(BaseModel):
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        # cartTotal: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.quantity, criteria.quantity),
                self._validate_field(self.restaurant, criteria.restaurant),
                # self._validate_field(self.cartTotal, criteria.cartTotal),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmptyCartEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            item=data.get("itemName", ""),
            price=data.get("price", 0.0),
            quantity=data.get("quantity", 0),
            restaurant=data.get("restaurantName", ""),
            # cartTotal=data.get("cartTotal", 0.0),
        )


class DeleteReviewEvent(Event, BaseEventValidator):
    event_name: str = "DELETE_REVIEW"
    author: str
    review_rating: float
    comment: str
    date: str
    name: str
    cuisine: str
    rating: float
    description: str

    class ValidationCriteria(BaseModel):
        author: str | CriterionValue | None = None
        review_rating: float | CriterionValue | None = None
        comment: str | CriterionValue | None = None
        date: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        description: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.review_rating, criteria.review_rating),
                self._validate_field(self.comment, criteria.comment),
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.cuisine, criteria.cuisine),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.description, criteria.description),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteReviewEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            author=data.get("author", ""),
            review_rating=float(data.get("rating", 0)),
            comment=data.get("comment", ""),
            date=data.get("date", ""),
            name=data.get("restaurantName", ""),
            cuisine=data.get("cuisine", ""),
            rating=float(data.get("restaurantRating", 0.0)),
            description=data.get("restaurantDescription", ""),
        )


class BackToAllRestaurantsEvent(Event, BaseEventValidator):
    event_name: str = "BACK_TO_ALL_RESTAURANTS"
    from_restaurant_name: str

    class ValidationCriteria(BaseModel):
        from_restaurant_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.from_restaurant_name, criteria.from_restaurant_name)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BackToAllRestaurantsEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            from_restaurant_name=data.get("fromRestaurantName", ""),
        )


class AddressAddedEvent(Event, BaseEventValidator):
    event_name: str = "ADDRESS_ADDED"
    address: str
    mode: str
    items: list[CheckoutItem]
    restaurant: str
    total_price: float

    class ValidationCriteria(BaseModel):
        address: str | CriterionValue | None = None
        mode: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        # size: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        # preferences: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        total_price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        base_validation = all(
            [
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.mode, criteria.mode),
                self._validate_field(self.restaurant, criteria.restaurant),
                self._validate_field(self.total_price, criteria.total_price),
            ]
        )

        if not base_validation:
            return False

        if criteria.item is None and criteria.price is None and criteria.quantity is None:
            return True

        for item in self.items:
            if (
                self._validate_field(item.name, criteria.item) and self._validate_field(item.price, criteria.price) and self._validate_field(item.quantity, criteria.quantity)
                # and self._validate_field(item.size, criteria.size)
                # and self._validate_field(item.preferences, criteria.preferences)
            ):
                return True
        return False

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddressAddedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        items = [CheckoutItem(**item) for item in data.get("items", [])]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            address=data.get("address", ""),
            mode=data.get("mode", ""),
            restaurant=data.get("restaurantName", ""),
            total_price=data.get("totalPrice", 0.0),
            items=items,
        )


EVENTS = [
    SearchRestaurantEvent,
    ViewRestaurantEvent,
    RestaurantFilterEvent,
    AddToCartModalOpenEvent,
    ItemIncrementedEvent,
    AddToCartEvent,
    OpenCheckoutPageEvent,
    DropoffPreferenceEvent,
    AddressAddedEvent,
    EmptyCartEvent,
    DeleteReviewEvent,
    BackToAllRestaurantsEvent,
    PlaceOrderEvent,
    QuickOrderStartedEvent,
    QuickReorderEvent,
    ViewAllRestaurantsEvent,
    EditCartItemEvent,
]
BACKEND_EVENT_TYPES = {
    "SEARCH_DELIVERY_RESTAURANT": SearchRestaurantEvent,
    "VIEW_DELIVERY_RESTAURANT": ViewRestaurantEvent,
    "RESTAURANT_FILTER": RestaurantFilterEvent,
    "ADD_TO_CART_MODAL_OPEN": AddToCartModalOpenEvent,
    "ITEM_INCREMENTED": ItemIncrementedEvent,
    "ADD_TO_CART_MENU_ITEM": AddToCartEvent,
    "OPEN_CHECKOUT_PAGE": OpenCheckoutPageEvent,
    "DROPOFF_PREFERENCE": DropoffPreferenceEvent,
    "PLACE_ORDER": PlaceOrderEvent,
    "EMPTY_CART": EmptyCartEvent,
    "DELETE_REVIEW": DeleteReviewEvent,
    "BACK_TO_ALL_RESTAURANTS": BackToAllRestaurantsEvent,
    "ADDRESS_ADDED": AddressAddedEvent,
    "QUICK_ORDER_STARTED": QuickOrderStartedEvent,
    "QUICK_REORDER": QuickReorderEvent,
    "VIEW_ALL_RESTAURANTS": ViewAllRestaurantsEvent,
    "EDIT_CART_ITEM": EditCartItemEvent,
}
