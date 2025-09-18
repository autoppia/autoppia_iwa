from datetime import datetime, time as dt_time

from dateutil import parser
from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.utils import log_event

from ..shared_utils import validate_date_field, validate_time_field


class SearchLocationEvent(Event, BaseEventValidator):
    """event triggered when someone enter location"""

    event_name: str = "SEARCH_LOCATION"
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
    def parse(cls, backend_event: "BackendEvent") -> "SearchLocationEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            location=data.get("value"),
        )


class SearchDestinationEvent(Event, BaseEventValidator):
    """event triggered when someone enter destination"""

    event_name: str = "SEARCH_DESTINATION"
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
    def parse(cls, backend_event: "BackendEvent") -> "SearchDestinationEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
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
        log_event(backend_event)
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

        return validate_date_field(self.date, criteria.date)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectDateEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(data.get("date")),
        )


def parse_time(value: str | None) -> dt_time | None:
    if not value:
        return None
    try:
        if isinstance(value, dt_time):
            return value
        if isinstance(value, str):
            return parser.parse(value)
        return None
    except (ValueError, TypeError):
        return None


class SelectTimeEvent(Event, BaseEventValidator):
    """event triggered when someone selects time"""

    event_name: str = "SELECT_TIME"
    time: dt_time | None = None

    class ValidationCriteria(BaseModel):
        time: dt_time | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_time = validate_time_field(self.time, criteria.time)
        return all([validate_time])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectTimeEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
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
    time: dt_time | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        time: dt_time | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_date = validate_date_field(self.date, criteria.date)
        validate_time = validate_time_field(self.time, criteria.time)
        return all(
            [
                validate_date,
                validate_time,
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "NextPickupEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
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
    destination: str
    location: str
    scheduled: datetime

    class ValidationCriteria(BaseModel):
        destination: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None  # skip for now but will work on it

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        validate_schedule = validate_date_field(self.scheduled, criteria.scheduled)
        result = all(
            [
                self._validate_field(self.destination, criteria.destination),
                self._validate_field(self.location, criteria.location),
                validate_schedule,
            ]
        )
        if not result:
            ...
        return result

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchRideEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            destination=data.get("dropoff"),
            location=data.get("pickup"),
            scheduled=parse_datetime(data.get("scheduled")),
        )


class SelectCarEvent(Event, BaseEventValidator):
    """event triggered when someone selects available car to ride"""

    event_name: str = "SELECT_CAR"
    # discount_percentage: str
    destination: str
    # eta: str
    # is_recommended: bool
    # old_price: float
    location: str
    price: float
    # price_difference: float
    # ride_id: int
    ride_name: str
    # ride_type: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        # discount_percentage: str | CriterionValue | None = None
        destination: str | CriterionValue | None = None
        # eta: str | CriterionValue | None = None
        # is_recommended: bool | CriterionValue | None = None
        # old_price: float | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        # price_difference: float | CriterionValue | None = None
        # ride_id: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        # ride_type: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_schedule = validate_date_field(self.scheduled, criteria.scheduled)
        result = all(
            [
                # self._validate_field(self.discount_percentage, criteria.discount_percentage),
                self._validate_field(self.destination, criteria.destination),
                # self._validate_field(self.eta, criteria.eta),
                # self._validate_field(self.is_recommended, criteria.is_recommended),
                # self._validate_field(self.old_price, criteria.old_price),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                # self._validate_field(self.price_difference, criteria.price_difference),
                # self._validate_field(self.ride_id, criteria.ride_id),
                self._validate_field(self.ride_name, criteria.ride_name),
                # self._validate_field(self.ride_type, criteria.ride_type),
                validate_schedule,
                self._validate_field(self.seats, criteria.seats),
            ]
        )
        if not result:
            ...
        return result

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SelectCarEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # discount_percentage=data.get("discountPercentage"),
            destination=data.get("dropoff"),
            # eta=data.get("eta"),
            # is_recommended=data.get("isRecommended"),
            # old_price=data.get("oldPrice"),
            location=data.get("pickup"),
            price=data.get("price"),
            # price_difference=data.get("priceDifference"),
            # ride_id=data.get("rideId"),
            ride_name=data.get("rideName"),
            # ride_type=data.get("rideType"),
            scheduled=parse_datetime(data.get("scheduled")),
            seats=data.get("seats"),
        )


class ReserveRideEvent(Event, BaseEventValidator):
    """event triggered when someone reserves available car to ride"""

    event_name: str = "RESERVE_RIDE"
    # discount_percentage: str
    destination: str
    # eta: str
    # is_recommended: bool
    # old_price: float
    location: str
    price: float
    # price_difference: float
    # ride_id: int
    ride_name: str
    # ride_type: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        # discount_percentage: str | CriterionValue | None = None
        destination: str | CriterionValue | None = None
        # eta: str | CriterionValue | None = None
        # is_recommended: bool | CriterionValue | None = None
        # old_price: float | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        # price_difference: float | CriterionValue | None = None
        # ride_id: int | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        # ride_type: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_scheduled = validate_date_field(self.scheduled, criteria.scheduled)
        return all(
            [
                # self._validate_field(self.discount_percentage, criteria.discount_percentage),
                self._validate_field(self.destination, criteria.destination),
                # self._validate_field(self.eta, criteria.eta),
                # self._validate_field(self.is_recommended, criteria.is_recommended),
                # self._validate_field(self.old_price, criteria.old_price),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                # self._validate_field(self.price_difference, criteria.price_difference),
                # self._validate_field(self.ride_id, criteria.ride_id),
                self._validate_field(self.ride_name, criteria.ride_name),
                # self._validate_field(self.ride_type, criteria.ride_type),
                validate_scheduled,
                self._validate_field(self.seats, criteria.seats),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReserveRideEvent":
        base_event = Event.parse(backend_event)
        log_event(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # discount_percentage=data.get("discountPercentage"),
            destination=data.get("dropoff"),
            # eta=data.get("eta"),
            # is_recommended=data.get("isRecommended"),
            # old_price=data.get("oldPrice"),
            location=data.get("pickup"),
            price=data.get("price"),
            # price_difference=data.get("priceDifference"),
            # ride_id=data.get("rideId"),
            ride_name=data.get("rideName"),
            # ride_type=data.get("rideType"),
            scheduled=parse_datetime(data.get("scheduled")),
            seats=data.get("seats"),
        )


def parse_datetime(value: str | None) -> datetime | dt_time | None:
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
                        return dt_time(int(t[0]), int(t[1]))  # updated for time
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
    SearchLocationEvent,
    SearchDestinationEvent,
    NextPickupEvent,
    SelectDateEvent,
    SelectTimeEvent,
    SelectCarEvent,
    SearchRideEvent,
    ReserveRideEvent,
]

BACKEND_EVENT_TYPES = {
    "SEARCH_LOCATION": SearchLocationEvent,
    "SEARCH_DESTINATION": SearchDestinationEvent,
    "NEXT_PICKUP": NextPickupEvent,
    "SELECT_TIME": SelectTimeEvent,
    "SELECT_DATE": SelectDateEvent,
    "SEARCH": SearchRideEvent,
    "SELECT_CAR": SelectCarEvent,
    "RESERVE_RIDE": ReserveRideEvent,
}
