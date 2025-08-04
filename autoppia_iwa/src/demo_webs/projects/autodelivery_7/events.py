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
    restaurant: str
    # itemId: str
    item: str
    price: float

    class ValidationCriteria(BaseModel):
        # restaurantId: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        # itemId: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.restaurantId, criteria.restaurantId),
                self._validate_field(self.restaurant, criteria.restaurant),
                # self._validate_field(self.itemId, criteria.itemId),
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
            # restaurantId=data.get("restaurantId", ""),
            restaurant=data.get("restaurantName", ""),
            # itemId=data.get("itemId", ""),
            item=data.get("itemName", ""),
            price=data.get("itemPrice", 0.0),
        )


class ItemIncrementedEvent(Event, BaseEventValidator):
    event_name: str = "ITEM_INCREMENTED"
    # itemId: str
    item: str
    new_quantity: int

    class ValidationCriteria(BaseModel):
        # itemId: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        new_quantity: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.itemId, criteria.itemId),
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
            # itemId=data.get("itemId", ""),
            item=data.get("itemName", ""),
            new_quantity=data.get("newQuantity", 0),
        )


# class ItemDecrementedEvent(Event, BaseEventValidator):
#     event_name: str = "ITEM_DECREMENTED"
#     # itemId: str
#     itemName: str
#     newQuantity: int
#
#     class ValidationCriteria(BaseModel):
#         # itemId: str | CriterionValue | None = None
#         itemName: str | CriterionValue | None = None
#         newQuantity: int | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         return all(
#             [
#                 # self._validate_field(self.itemId, criteria.itemId),
#                 self._validate_field(self.itemName, criteria.itemName),
#                 self._validate_field(self.newQuantity, criteria.newQuantity),
#             ]
#         )
#
#     @classmethod
#     def parse(cls, backend_event: BackendEvent) -> "ItemDecrementedEvent":
#         base = Event.parse(backend_event)
#         data = backend_event.data
#         return cls(
#             event_name=base.event_name,
#             timestamp=base.timestamp,
#             web_agent_id=base.web_agent_id,
#             user_id=base.user_id,
#             # itemId=data.get("itemId", ""),
#             itemName=data.get("itemName", ""),
#             newQuantity=data.get("newQuantity", 0),
#         )


class AddToCartEvent(Event, BaseEventValidator):
    event_name: str = "ADD_TO_CART_MENU_ITEM"
    # itemId: str
    item: str
    price: float
    size: str
    restaurant: str
    # sizePriceMod: float
    # options: list[str]
    preferences: str
    quantity: int
    totalPrice: float

    class ValidationCriteria(BaseModel):
        # itemId: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        size: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        # sizePriceMod: float | CriterionValue | None = None
        # options: str | CriterionValue | None = None
        preferences: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        totalPrice: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.itemId, criteria.itemId),
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.size, criteria.size),
                self._validate_field(self.restaurant, criteria.restaurant),
                # self._validate_field(self.sizePriceMod, criteria.sizePriceMod),
                # self._validate_field(self.options, criteria.options),
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
            item=data.get("itemName", ""),
            price=data.get("basePrice", 0.0),
            size=data.get("size", ""),
            restaurant=data.get("restaurantName", ""),
            # sizePriceMod=data.get("sizePriceMod", 0.0),
            # options=data.get("options", []),
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
    items: list[CheckoutItem]

    class ValidationCriteria(BaseModel):
        # pass
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
    delivery_preference: str

    class ValidationCriteria(BaseModel):
        delivery_preference: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.delivery_preference, criteria.delivery_preference)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DropoffPreferenceEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            delivery_preference=backend_event.data.get("preference", ""),
        )


class OrderItem(BaseModel):
    id: str
    name: str
    price: float
    quantity: int


class PlaceOrderEvent(Event, BaseEventValidator):
    event_name: str = "PLACE_ORDER"
    username: str
    phone: str
    address: str
    # mode: str
    # deliveryTime: str
    delivery_preference: str
    items: list[OrderItem]
    total: float

    class ValidationCriteria(BaseModel):
        username: str | CriterionValue | None = None
        phone: str | CriterionValue | None = None
        address: str | CriterionValue | None = None
        # mode: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        delivery_preference: str | CriterionValue | None = None
        # deliveryTime: str | CriterionValue | None = None
        total: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.phone, criteria.phone),
                self._validate_field(self.address, criteria.address),
                # self._validate_field(self.mode, criteria.mode),
                # self._validate_field(self.deliveryTime, criteria.deliveryTime),
                # self._validate_field(self.total, criteria.total),
                self._validate_field(self.delivery_preference, criteria.delivery_preference),
                any(i for i in self.items if (self._validate_field(i.name, criteria.item) and self._validate_field(i.price, criteria.price and self._validate_field(i.quantity, criteria.quantity)))),
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
            username=data.get("name", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
            # mode=data.get("mode", ""),
            # deliveryTime=data.get("deliveryTime", ""),
            # dropoff=data.get("dropoff", ""),
            delivery_preference=data.get("dropoff", ""),
            items=items,
            total=data.get("total", 0.0),
        )


# class PickupModeEvent(Event, BaseEventValidator, AddToCartEvent):
#     event_name: str = "PICKUP_MODE"
#     mode: str
#
#     class ValidationCriteria(AddToCartEvent.ValidationCriteria):
#         mode: str | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         return all([self._validate_field(self.mode, criteria.mode), AddToCartEvent._validate_criteria(self, criteria)])
#
#     @classmethod
#     def parse(cls, backend_event: BackendEvent) -> "PickupModeEvent":
#         base = Event.parse(backend_event)
#         cart_data=AddToCartEvent.parse(backend_event)
#         return cls(
#             event_name=base.event_name,
#             timestamp=base.timestamp,
#             web_agent_id=base.web_agent_id,
#             user_id=base.user_id,
#             mode=backend_event.data.get("mode", ""),
#             **cart_data.model_dump(),
#         )


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
    # fromRestaurantId: str
    fromRestaurantName: str

    class ValidationCriteria(BaseModel):
        # fromRestaurantId: str | CriterionValue | None = None
        fromRestaurantName: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.fromRestaurantId, criteria.fromRestaurantId),
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
            # fromRestaurantId=data.get("fromRestaurantId", ""),
            fromRestaurantName=data.get("fromRestaurantName", ""),
        )


class AddressAddedEvent(Event, BaseEventValidator):
    event_name: str = "ADDRESS_ADDED"
    address: str
    mode: str
    item: str
    price: float
    size: str
    restaurant: str
    preferences: str
    quantity: int
    totalPrice: float

    class ValidationCriteria(BaseModel):
        address: str | CriterionValue | None = None
        mode: str | CriterionValue | None = None
        item: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        size: str | CriterionValue | None = None
        restaurant: str | CriterionValue | None = None
        preferences: str | CriterionValue | None = None
        quantity: int | CriterionValue | None = None
        totalPrice: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.address, criteria.address),
                self._validate_field(self.mode, criteria.mode),
                self._validate_field(self.item, criteria.item),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.size, criteria.size),
                self._validate_field(self.restaurant, criteria.restaurant),
                self._validate_field(self.preferences, criteria.preferences),
                self._validate_field(self.quantity, criteria.quantity),
                self._validate_field(self.totalPrice, criteria.totalPrice),
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
            item=data.get("itemName", ""),
            price=data.get("basePrice", 0.0),
            size=data.get("size", ""),
            restaurant=data.get("restaurantName", ""),
            preferences=data.get("preferences", ""),
            quantity=data.get("quantity", 0),
            totalPrice=data.get("totalPrice", 0.0),
        )


# class DeliveryModeEvent(Event, BaseEventValidator):
#     event_name: str = "DELIVERY_MODE"
#     mode: str
#
#     class ValidationCriteria(BaseModel):
#         mode: str | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         return self._validate_field(self.mode, criteria.mode)
#
#     @classmethod
#     def parse(cls, backend_event: BackendEvent) -> "DeliveryModeEvent":
#         base = Event.parse(backend_event)
#         return cls(
#             event_name=base.event_name,
#             timestamp=base.timestamp,
#             web_agent_id=base.web_agent_id,
#             user_id=base.user_id,
#             mode=backend_event.data.get("mode", ""),
#         )


EVENTS = [
    SearchRestaurantEvent,
    ViewRestaurantEvent,
    AddToCartModalOpenEvent,
    ItemIncrementedEvent,
    # ItemDecrementedEvent,
    AddToCartEvent,
    OpenCheckoutPageEvent,
    DropoffPreferenceEvent,
    AddressAddedEvent,
    # PickupModeEvent,
    EmptyCartEvent,
    DeleteReviewEvent,
    BackToAllRestaurantsEvent,
    # DeliveryModeEvent,
    PlaceOrderEvent,
]
BACKEND_EVENT_TYPES = {
    "SEARCH_RESTAURANT": SearchRestaurantEvent,
    "VIEW_RESTAURANT": ViewRestaurantEvent,
    "ADD_TO_CART_MODAL_OPEN": AddToCartModalOpenEvent,
    "ITEM_INCREMENTED": ItemIncrementedEvent,
    # "ITEM_DECREMENTED": ItemDecrementedEvent,
    "ADD_TO_CART_MENU_ITEM": AddToCartEvent,
    "OPEN_CHECKOUT_PAGE": OpenCheckoutPageEvent,
    "DROPOFF_PREFERENCE": DropoffPreferenceEvent,
    "PLACE_ORDER": PlaceOrderEvent,
    # "PICKUP_MODE": PickupModeEvent,
    "EMPTY_CART": EmptyCartEvent,
    "DELETE_REVIEW": DeleteReviewEvent,
    "BACK_TO_ALL_RESTAURANTS": BackToAllRestaurantsEvent,
    "ADDRESS_ADDED": AddressAddedEvent,
    # "DELIVERY_MODE": DeliveryModeEvent,
}
