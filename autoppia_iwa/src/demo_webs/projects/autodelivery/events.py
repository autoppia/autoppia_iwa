from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class SearchRestaurantEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_RESTAURANT"
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
    event_name: str = "VIEW_RESTAURANT"
    # id: str
    name: str
    cuisine: str
    rating: float

    class ValidationCriteria(BaseModel):
        # id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.id, criteria.id),
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
            # id=data.get("id", ""),
            name=data.get("name", ""),
            cuisine=data.get("cuisine", ""),
            rating=data.get("rating", 0.0),
        )


class AddToCartModalOpenEvent(Event, BaseEventValidator):
    event_name: str = "ADD_TO_CART_MODAL_OPEN"
    # restaurantId: str
    restaurantName: str
    # itemId: str
    itemName: str
    itemPrice: float

    class ValidationCriteria(BaseModel):
        # restaurantId: str | CriterionValue | None = None
        restaurantName: str | CriterionValue | None = None
        # itemId: str | CriterionValue | None = None
        itemName: str | CriterionValue | None = None
        itemPrice: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.restaurantId, criteria.restaurantId),
                self._validate_field(self.restaurantName, criteria.restaurantName),
                # self._validate_field(self.itemId, criteria.itemId),
                self._validate_field(self.itemName, criteria.itemName),
                self._validate_field(self.itemPrice, criteria.itemPrice),
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
            # restaurantId=data.get("restaurantId", ""),
            restaurantName=data.get("restaurantName", ""),
            # itemId=data.get("itemId", ""),
            itemName=data.get("itemName", ""),
            itemPrice=data.get("itemPrice", 0.0),
        )


class ItemIncrementedEvent(Event, BaseEventValidator):
    event_name: str = "ITEM_INCREMENTED"
    # itemId: str
    itemName: str
    newQuantity: int

    class ValidationCriteria(BaseModel):
        # itemId: str | CriterionValue | None = None
        itemName: str | CriterionValue | None = None
        newQuantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.itemId, criteria.itemId),
                self._validate_field(self.itemName, criteria.itemName),
                self._validate_field(self.newQuantity, criteria.newQuantity),
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
            # itemId=data.get("itemId", ""),
            itemName=data.get("itemName", ""),
            newQuantity=data.get("newQuantity", 0),
        )


class ItemDecrementedEvent(Event, BaseEventValidator):
    event_name: str = "ITEM_DECREMENTED"
    # itemId: str
    itemName: str
    newQuantity: int

    class ValidationCriteria(BaseModel):
        # itemId: str | CriterionValue | None = None
        itemName: str | CriterionValue | None = None
        newQuantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.itemId, criteria.itemId),
                self._validate_field(self.itemName, criteria.itemName),
                self._validate_field(self.newQuantity, criteria.newQuantity),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ItemDecrementedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            # itemId=data.get("itemId", ""),
            itemName=data.get("itemName", ""),
            newQuantity=data.get("newQuantity", 0),
        )


class AddToCartEvent(Event, BaseEventValidator):
    event_name: str = "ADD_TO_CART"
    # itemId: str
    itemName: str
    basePrice: float
    size: str
    sizePriceMod: float
    options: list[str]
    preferences: str
    quantity: int
    totalPrice: float

    class ValidationCriteria(BaseModel):
        # itemId: str | CriterionValue | None = None
        itemName: str | CriterionValue | None = None
        basePrice: float | CriterionValue | None = None
        size: str | CriterionValue | None = None
        sizePriceMod: float | CriterionValue | None = None
        options: str | CriterionValue | None = None
        preferences: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        totalPrice: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.itemId, criteria.itemId),
                self._validate_field(self.itemName, criteria.itemName),
                self._validate_field(self.basePrice, criteria.basePrice),
                self._validate_field(self.size, criteria.size),
                self._validate_field(self.sizePriceMod, criteria.sizePriceMod),
                self._validate_field(self.options, criteria.options),
                self._validate_field(self.preferences, criteria.preferences),
                self._validate_field(self.quantity, criteria.quantity),
                self._validate_field(self.totalPrice, criteria.totalPrice),
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
            # itemId=data.get("itemId", ""),
            itemName=data.get("itemName", ""),
            basePrice=data.get("basePrice", 0.0),
            size=data.get("size", ""),
            sizePriceMod=data.get("sizePriceMod", 0.0),
            options=data.get("options", []),
            preferences=data.get("preferences", ""),
            quantity=data.get("quantity", 0),
            totalPrice=data.get("totalPrice", 0.0),
        )


class CheckoutItem(BaseModel):
    id: str
    name: str
    quantity: int
    price: float


class OpenCheckoutPageEvent(Event, BaseEventValidator):
    event_name: str = "OPEN_CHECKOUT_PAGE"
    itemCount: int
    items: List[CheckoutItem]

    class ValidationCriteria(BaseModel):
        itemCount: int | CriterionValue | None = None
        items: list | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.itemCount, criteria.itemCount),
                self._validate_field(self.items, criteria.items),
            ]
        )

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
            itemCount=data.get("itemCount", 0),
            items=items,
        )


class DropoffPreferenceEvent(Event, BaseEventValidator):
    event_name: str = "DROPOFF_PREFERENCE"
    preference: str

    class ValidationCriteria(BaseModel):
        preference: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.preference, criteria.preference)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DropoffPreferenceEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            preference=backend_event.data.get("preference", ""),
        )


class OrderItem(BaseModel):
    id: str
    name: str
    price: float
    quantity: int


class PlaceOrderEvent(Event, BaseEventValidator):
    event_name: str = "PLACE_ORDER"
    name: str
    phone: str
    address: str
    mode: str
    deliveryTime: str
    dropoff: str
    items: list[OrderItem]
    total: float

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        phone: str | CriterionValue | None = None
        address: str | CriterionValue | None = None
        mode: str | CriterionValue | None = None
        deliveryTime: str | CriterionValue | None = None
        dropoff: str | CriterionValue | None = None
        items: list | CriterionValue | None = None
        total: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.phone, criteria.phone),
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.mode, criteria.mode),
                self._validate_field(self.deliveryTime, criteria.deliveryTime),
                self._validate_field(self.dropoff, criteria.dropoff),
                self._validate_field(self.items, criteria.items),
                self._validate_field(self.total, criteria.total),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PlaceOrderEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        items = [OrderItem(**item) for item in data.get("items", [])]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            mode=data.get("mode", ""),
            deliveryTime=data.get("deliveryTime", ""),
            dropoff=data.get("dropoff", ""),
            items=items,
            total=data.get("total", 0.0),
        )


class PickupModeEvent(Event, BaseEventValidator):
    event_name: str = "PICKUP_MODE"
    mode: str

    class ValidationCriteria(BaseModel):
        mode: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.mode, criteria.mode)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PickupModeEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            mode=backend_event.data.get("mode", ""),
        )


class EmptyCartEvent(Event, BaseEventValidator):
    event_name: str = "EMPTY_CART"
    message: str

    class ValidationCriteria(BaseModel):
        message: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.message, criteria.message)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmptyCartEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            message=backend_event.data.get("message", ""),
        )


class DeleteReviewEvent(Event, BaseEventValidator):
    event_name: str = "DELETE_REVIEW"
    author: str
    rating: int
    comment: str
    date: str

    class ValidationCriteria(BaseModel):
        author: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        comment: str | CriterionValue | None = None
        date: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.author, criteria.author),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.comment, criteria.comment),
                self._validate_field(self.date, criteria.date),
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
            rating=data.get("rating", 0),
            comment=data.get("comment", ""),
            date=data.get("date", ""),
        )


class BackToAllRestaurantsEvent(Event, BaseEventValidator):
    event_name: str = "BACK_TO_ALL_RESTAURANTS"
    fromRestaurantId: str
    fromRestaurantName: str

    class ValidationCriteria(BaseModel):
        fromRestaurantId: str | CriterionValue | None = None
        fromRestaurantName: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.fromRestaurantId, criteria.fromRestaurantId),
                self._validate_field(self.fromRestaurantName, criteria.fromRestaurantName),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BackToAllRestaurantsEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            fromRestaurantId=data.get("fromRestaurantId", ""),
            fromRestaurantName=data.get("fromRestaurantName", ""),
        )


class AddressAddedEvent(Event, BaseEventValidator):
    event_name: str = "ADDRESS_ADDED"
    address: str
    mode: str

    class ValidationCriteria(BaseModel):
        address: str | CriterionValue | None = None
        mode: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.mode, criteria.mode),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddressAddedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            address=data.get("address", ""),
            mode=data.get("mode", ""),
        )


class DeliveryModeEvent(Event, BaseEventValidator):
    event_name: str = "DELIVERY_MODE"
    mode: str

    class ValidationCriteria(BaseModel):
        mode: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.mode, criteria.mode)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeliveryModeEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            mode=backend_event.data.get("mode", ""),
        )
