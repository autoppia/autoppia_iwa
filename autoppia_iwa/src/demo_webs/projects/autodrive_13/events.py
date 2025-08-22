from datetime import datetime, time

from dateutil import parser
from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

from ..shared_utils import validate_date_field


class EnterLocationEvent(Event, BaseEventValidator):
    """event triggered when someone enter location"""

    event_name: str = "ENTER_LOCATION"
    location: str

    class ValidationCriteria(BaseModel):
        location: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.location, criteria.location),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EnterLocationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            location=data.get("value"),
        )


class EnterDestinationEvent(Event, BaseEventValidator):
    """event triggered when someone enter destination"""

    event_name: str = "ENTER_DESTINATION"
    destination: str

    class ValidationCriteria(BaseModel):
        destination: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.destination, criteria.destination),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EnterDestinationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            destination=data.get("value"),
        )


class SeePricesEvent(Event, BaseEventValidator):
    """event triggered when someone sees a price"""

    event_name: str = "SEE_PRICES"
    location: str
    destination: str

    class ValidationCriteria(BaseModel):
        location: str | CriterionValue | None = None
        destination: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.destination, criteria.destination),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SeePricesEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            location=data.get("location"),
            destination=data.get("destination"),
        )


class SelectDateEvent(Event, BaseEventValidator):
    """event triggered when someone selects date"""

    event_name: str = "SELECT_DATE"
    date: datetime | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        validate_date = validate_date_field(self.date, criteria.date)
        return all(
            [
                validate_date
                # self._validate_field(self.date, criteria.date),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectDateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(data.get("date")),
        )


class SelectTimeEvent(Event, BaseEventValidator):
    """event triggered when someone selects time"""

    event_name: str = "SELECT_TIME"
    time: datetime | None = None

    class ValidationCriteria(BaseModel):
        time: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_time = validate_date_field(self.time, criteria.time)
        return all([validate_time])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectTimeEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            time=parse_datetime(data.get("time")),
        )


class NextPickupEvent(Event, BaseEventValidator):
    """event triggered when someone clicks on the next button after successful selects date and time for pickup"""

    event_name: str = "NEXT_PICKUP"
    date: datetime | None = None
    time: datetime | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        time: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_date = validate_date_field(self.date, criteria.date)
        validate_time = validate_date_field(self.time, criteria.time)
        return all(
            [
                validate_date,
                validate_time,
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "NextPickupEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(data.get("date")),
            time=parse_datetime(data.get("time")),
        )


class SearchRideEvent(Event, BaseEventValidator):
    """event triggered when someone clicks on the search button after successful selects date and time for pickup"""

    event_name: str = "SEARCH"
    dropoff: str
    # dropoffLength: int
    # hasDropoff: bool
    # hasPickup: bool
    # isScheduled: bool
    pickup: str
    # pickupLength: int
    scheduled: datetime

    class ValidationCriteria(BaseModel):
        dropoff: str | CriterionValue | None = None
        # dropoffLength: int | CriterionValue |None = None
        # hasDropoff: bool | CriterionValue | None = None
        # hasPickup: bool | CriterionValue | None = None
        # isScheduled: bool | CriterionValue | None = None
        pickup: str | CriterionValue | None = None
        # pickupLength: int | CriterionValue |None = None
        scheduled: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        validate_schedule = validate_date_field(self.scheduled, criteria.schedule)
        return all(
            [
                self._validate_field(self.dropoff, criteria.dropoff),
                # self._validate_field(self.dropoffLength, criteria.dropoffLength),
                # self._validate_field(self.hasDropoff, criteria.hasDropoff),
                # self._validate_field(self.hasPickup, criteria.hasPickup),
                # self._validate_field(self.isScheduled, criteria.isSchedule),
                self._validate_field(self.pickup, criteria.pickup),
                # self._validate_field(self.pickupLength, criteria.pickupLength),
                # self._validate_field(self.scheduled, criteria.scheduled),
                validate_schedule,
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchRideEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            dropoff=data.get("dropoff"),
            # dropoffLength=data.get("dropoffLength"),
            # hasDropoff=data.get("hasDropoff"),
            # hasPickup=data.get("hasPickup"),
            # isScheduled=data.get("isScheduled"),
            pickup=data.get("pickup"),
            # pickupLength=data.get("pickupLength"),
            scheduled=parse_datetime(data.get("scheduled")),
        )


class SelectCarEvent(Event, BaseEventValidator):
    """event triggered when someone selects available car to ride"""

    event_name: str = "SELECT_CAR"
    discount_percentage: str
    drop_off: str
    eta: str
    # is_recommended: bool
    old_price: float
    pick_up: str
    price: float
    price_difference: float
    ride_id: int
    ride_name: str
    ride_type: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        discount_percentage: str | CriterionValue | None = None
        drop_off: str | CriterionValue | None = None
        eta: str | CriterionValue | None = None
        # is_recommended: bool | CriterionValue | None = None
        old_price: float | CriterionValue | None = None
        pick_up: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        # price_difference: float | CriterionValue | None = None
        ride_id: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        # ride_type: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_schedule = validate_date_field(self.scheduled, criteria.scheduled)
        return all(
            [
                self._validate_field(self.discount_percentage, criterion.discount_percentage),
                self._validate_field(self.drop_off, criterion.drop_off),
                self._validate_field(self.eta, criterion.eta),
                # self._validate_field(self.is_recommended, criterion.is_recommended),
                self._validate_field(self.old_price, criterion.old_price),
                self._validate_field(self.pick_up, criterion.pick_up),
                self._validate_field(self.price, criterion.price),
                # self._validate_field(self.price_difference, criterion.price_difference),
                self._validate_field(self.ride_id, criterion.ride_id),
                self._validate_field(self.ride_name, criterion.ride_name),
                # self._validate_field(self.ride_type, criterion.ride_type),
                validate_schedule,
                self._validate_field(self.seats, criterion.seats),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectCarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            discount_percentage=data.get("discountPercentage"),
            drop_off=data.get("dropoff"),
            eta=data.get("eta"),
            # is_recommended=data.get("isRecommended"),
            old_price=data.get("oldPrice"),
            pick_up=data.get("pickup"),
            price=data.get("price"),
            # price_difference=data.get("priceDifference"),
            ride_id=data.get("rideId"),
            ride_name=data.get("rideName"),
            # ride_type=data.get("rideType"),
            scheduled=parse_datetime(data.get("scheduled")),
            seats=data.get("seats"),
        )


class ReserveRideEvent(Event, BaseEventValidator):
    """event triggered when someone reserves available car to ride"""

    event_name: str = "RESERVE_RIDE"
    discount_percentage: str
    drop_off: str
    eta: str
    is_recommended: bool
    old_price: float
    pick_up: str
    price: float
    price_difference: float
    ride_id: int
    ride_name: str
    ride_type: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        discount_percentage: str | CriterionValue | None = None
        drop_off: str | CriterionValue | None = None
        eta: str | CriterionValue | None = None
        is_recommended: bool | CriterionValue | None = None
        old_price: float | CriterionValue | None = None
        pick_up: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        price_difference: float | CriterionValue | None = None
        ride_id: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        ride_type: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_scheduled = validate_date_field(self.scheduled, criteria.scheduled)
        return all(
            [
                self._validate_field(self.discount_percentage, criterion.discount_percentage),
                self._validate_field(self.drop_off, criterion.drop_off),
                self._validate_field(self.eta, criterion.eta),
                self._validate_field(self.is_recommended, criterion.is_recommended),
                self._validate_field(self.old_price, criterion.old_price),
                self._validate_field(self.pick_up, criterion.pick_up),
                self._validate_field(self.price, criterion.price),
                self._validate_field(self.price_difference, criterion.price_difference),
                self._validate_field(self.ride_id, criterion.ride_id),
                self._validate_field(self.ride_name, criterion.ride_name),
                self._validate_field(self.ride_type, criterion.ride_type),
                validate_scheduled,
                self._validate_field(self.seats, criterion.seats),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReserveRideEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            discount_percentage=data.get("discountPercentage"),
            drop_off=data.get("dropoff"),
            eta=data.get("eta"),
            is_recommended=data.get("isRecommended"),
            old_price=data.get("oldPrice"),
            pick_up=data.get("pickup"),
            price=data.get("price"),
            price_difference=data.get("priceDifference"),
            ride_id=data.get("rideId"),
            ride_name=data.get("rideName"),
            ride_type=data.get("rideType"),
            scheduled=parse_datetime(data.get("scheduled")),
            seats=data.get("seats"),
        )


class TripDetailsEvent(Event, BaseEventValidator):
    """event triggered when want to check details of the trip"""

    event_name: str = "TRIP_DETAILS"
    date: datetime
    drop_off: str
    drop_off_label: str
    id: str
    payment: str
    pickup: str
    pickup_label: str
    price: float
    ride_index: int
    ride_name: str
    time: datetime

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        drop_off: str | CriterionValue | None = None
        drop_off_label: str | CriterionValue | None = None
        id: str | CriterionValue | None = None
        payment: str | CriterionValue | None = None
        pickup: str | CriterionValue | None = None
        pickup_label: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        ride_index: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        time: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_date = (validate_date_field(self.date, criteria.date),)
        validate_time = (validate_date_field(self.time, criteria.time),)
        return all(
            [
                validate_date,
                self._validate_field(self.drop_off, criterion.drop_off),
                self._validate_field(self.drop_off_label, criterion.drop_off_label),
                self._validate_field(self.id, criterion.id),
                self._validate_field(self.payment, criterion.payment),
                self._validate_field(self.pickup, criterion.pickup),
                self._validate_field(self.pickup_label, criterion.pickup_label),
                self._validate_field(self.price, criterion.price),
                self._validate_field(self.ride_index, criterion.ride_index),
                self._validate_field(self.ride_name, criterion.ride_name),
                validate_time,
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "TripDetailsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        trip_data = data.get("tripData")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(trip_data.get("date")),
            drop_off=trip_data.get("dropoff"),
            drop_off_label=trip_data.get("dropoffLabel"),
            id=trip_data.get("id"),
            payment=trip_data.get("payment"),
            pickup=trip_data.get("pickup"),
            pickup_label=trip_data.get("pickupLabel"),
            price=trip_data.get("price"),
            ride_index=trip_data.get("rideIndex"),
            ride_name=trip_data.get("rideName"),
            time=parse_datetime(trip_data.get("time")),
        )


class CancelReservationEvent(Event, BaseEventValidator):
    """event triggered when want to cancel reservation"""

    event_name: str = "CANCEL_RESERVATION"
    date: datetime
    drop_off: str
    drop_off_label: str
    id: str
    payment: str
    pickup: str
    pickup_label: str
    price: float
    ride_index: int
    ride_name: str
    time: datetime

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        drop_off: str | CriterionValue | None = None
        drop_off_label: str | CriterionValue | None = None
        id: str | CriterionValue | None = None
        payment: str | CriterionValue | None = None
        pickup: str | CriterionValue | None = None
        pickup_label: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        ride_index: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        time: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_date = (validate_date_field(self.date, criteria.date),)
        validate_time = (validate_date_field(self.time, criteria.time),)
        return all(
            [
                validate_date,
                self._validate_field(self.drop_off, criterion.drop_off),
                self._validate_field(self.drop_off_label, criterion.drop_off_label),
                self._validate_field(self.id, criterion.id),
                self._validate_field(self.payment, criterion.payment),
                self._validate_field(self.pickup, criterion.pickup),
                self._validate_field(self.pickup_label, criterion.pickup_label),
                self._validate_field(self.price, criterion.price),
                self._validate_field(self.ride_index, criterion.ride_index),
                self._validate_field(self.ride_name, criterion.ride_name),
                validate_time,
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelReservationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        trip_data = data.get("tripData")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(trip_data.get("date")),
            drop_off=trip_data.get("dropoff"),
            drop_off_label=trip_data.get("dropoffLabel"),
            id=trip_data.get("id"),
            payment=trip_data.get("payment"),
            pickup=trip_data.get("pickup"),
            pickup_label=trip_data.get("pickupLabel"),
            price=trip_data.get("price"),
            ride_index=trip_data.get("rideIndex"),
            ride_name=trip_data.get("rideName"),
            time=parse_datetime(trip_data.get("time")),
        )


def parse_datetime(value: str | None) -> datetime | time | None:
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                if ":" in value:  # updated for time
                    t = value.split(":")  # updated for time
                    if len(t) > 1:  # updated for time
                        return time(int(t[0]), int(t[1]))  # updated for time
            for sep in ("T", " "):
                if sep in value:
                    date_part = value.split(sep)[0]
                    try:
                        return datetime.fromisoformat(date_part)
                    except ValueError:
                        pass
            return parser.isoparse(value)
        return None
    except (ValueError, TypeError):
        return None


EVENTS = [
    EnterLocationEvent,
    EnterDestinationEvent,
    SeePricesEvent,
    NextPickupEvent,
    SelectDateEvent,
    SelectTimeEvent,
    SelectCarEvent,
    SearchRideEvent,
    ReserveRideEvent,
    TripDetailsEvent,
    CancelReservationEvent,
]

BACKEND_EVENT_TYPES = {
    "ENTER_LOCATION": EnterLocationEvent,
    "ENTER_DESTINATION": EnterDestinationEvent,
    "SEE_PRICES": SeePricesEvent,
    "NEXT_PICKUP": NextPickupEvent,
    "SELECT_TIME": SelectTimeEvent,
    "SELECT_DATE": SelectDateEvent,
    "SEARCH": SearchRideEvent,
    "SELECT_CAR": SelectCarEvent,
    "RESERVE_RIDE": ReserveRideEvent,
    "TRIP_DETAILS": TripDetailsEvent,
    "CANCEL_RESERVATION": CancelReservationEvent,
}
