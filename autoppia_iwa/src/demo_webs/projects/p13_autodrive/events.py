from datetime import date, datetime, time as dt_time
from typing import Any

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.shared.logging import log_event  # noqa: F401

from ...shared_utils import validate_date_field, validate_time_field


def _parse_datetime_flexible(value: str) -> datetime | dt_time | None:
    """Parse date/datetime strings without dateutil (avoids broken optional deps)."""
    s = value.strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        pass
    for sep in ("T", " "):
        if sep in s:
            date_part = s.split(sep)[0]
            try:
                return datetime.fromisoformat(date_part)
            except ValueError:
                pass
    if ":" in s:
        parts = s.split(":")
        if len(parts) >= 2:
            try:
                return dt_time(int(parts[0]), int(parts[1]))
            except ValueError:
                pass
    return None


def _coerce_datetime_like_criterion(criterion: Any) -> Any:
    """Normalize expected date/datetime criteria (e.g. ISO strings from JSON) to datetime/date objects."""
    if criterion is None:
        return None
    if isinstance(criterion, CriterionValue):
        v = criterion.value
        if isinstance(v, datetime):
            return criterion
        if type(v) is date:
            return CriterionValue(
                value=datetime.combine(v, dt_time.min),
                operator=criterion.operator,
            )
        if isinstance(v, str) and v.strip():
            p = parse_datetime(v.strip())
            if isinstance(p, datetime):
                return CriterionValue(value=p, operator=criterion.operator)
            if isinstance(p, dt_time):
                return CriterionValue(
                    value=datetime.combine(date.today(), p),
                    operator=criterion.operator,
                )
        return criterion
    if isinstance(criterion, datetime):
        return criterion
    if type(criterion) is date:
        return datetime.combine(criterion, dt_time.min)
    if isinstance(criterion, str) and criterion.strip():
        p = parse_datetime(criterion.strip())
        if isinstance(p, datetime):
            return p
        if isinstance(p, dt_time):
            return datetime.combine(date.today(), p)
    return criterion


def _coerce_time_like_criterion(criterion: Any) -> Any:
    """Normalize expected time criteria (e.g. strings) to time objects."""
    if criterion is None:
        return None
    if isinstance(criterion, CriterionValue):
        v = criterion.value
        if isinstance(v, dt_time):
            return criterion
        if isinstance(v, datetime):
            return CriterionValue(value=v.time(), operator=criterion.operator)
        if type(v) is date:
            return CriterionValue(value=dt_time.min, operator=criterion.operator)
        if isinstance(v, str) and v.strip():
            p = parse_datetime(v.strip())
            if isinstance(p, dt_time):
                return CriterionValue(value=p, operator=criterion.operator)
            if isinstance(p, datetime):
                return CriterionValue(value=p.time(), operator=criterion.operator)
        return criterion
    if isinstance(criterion, dt_time):
        return criterion
    if isinstance(criterion, datetime):
        return criterion.time()
    if type(criterion) is date:
        return dt_time.min
    if isinstance(criterion, str) and criterion.strip():
        p = parse_datetime(criterion.strip())
        if isinstance(p, dt_time):
            return p
        if isinstance(p, datetime):
            return p.time()
    return criterion


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
        data = backend_event.data
        raw = data.get("value")
        if raw is None:
            raw = data.get("location")
        location = "" if raw is None else str(raw)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            location=location,
        )


class EnterLocationEvent(SearchLocationEvent):
    event_name: str = "ENTER_LOCATION"


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
        data = backend_event.data
        raw = data.get("value")
        if raw is None:
            raw = data.get("destination")
        destination = "" if raw is None else str(raw)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            destination=destination,
        )


class EnterDestinationEvent(SearchDestinationEvent):
    event_name: str = "ENTER_DESTINATION"


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

        return validate_date_field(self.date, _coerce_datetime_like_criterion(criteria.date))

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


def parse_time(value: str | None) -> dt_time | None:
    if not value:
        return None
    try:
        if isinstance(value, dt_time):
            return value
        if isinstance(value, str):
            pt = _parse_datetime_flexible(value)
            if isinstance(pt, datetime):
                return pt.time()
            if isinstance(pt, dt_time):
                return pt
            return None
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
        validate_time = validate_time_field(self.time, _coerce_time_like_criterion(criteria.time))
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
    time: dt_time | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        time: dt_time | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_date = validate_date_field(self.date, _coerce_datetime_like_criterion(criteria.date))
        validate_time = validate_time_field(self.time, _coerce_time_like_criterion(criteria.time))
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

        validate_schedule = validate_date_field(self.scheduled, _coerce_datetime_like_criterion(criteria.scheduled))
        result = all(
            [
                self._validate_field(self.destination, criteria.destination),
                self._validate_field(self.location, criteria.location),
                validate_schedule,
            ]
        )
        return result

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchRideEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        scheduled = parse_ride_scheduled(data.get("scheduled"), backend_event.timestamp)
        if scheduled is None:
            scheduled = _datetime_from_event_timestamp(backend_event.timestamp)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            destination=str(data.get("dropoff") or ""),
            location=str(data.get("pickup") or ""),
            scheduled=scheduled,
        )


class SelectCarEvent(Event, BaseEventValidator):
    """event triggered when someone selects available car to ride"""

    event_name: str = "SELECT_CAR"
    destination: str
    location: str
    price: float
    ride_name: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        destination: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_schedule = validate_date_field(self.scheduled, _coerce_datetime_like_criterion(criteria.scheduled))
        result = all(
            [
                self._validate_field(self.destination, criteria.destination),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.ride_name, criteria.ride_name),
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
        kw = _reserve_ride_field_values(backend_event.data or {}, backend_event.timestamp)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **kw,
        )


class ReserveRideEvent(Event, BaseEventValidator):
    """event triggered when someone reserves available car to ride"""

    event_name: str = "RESERVE_RIDE"
    destination: str
    location: str
    price: float
    ride_name: str
    scheduled: datetime
    seats: int

    class ValidationCriteria(BaseModel):
        destination: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: float | CriterionValue | None = None
        ride_name: str | CriterionValue | None = None
        scheduled: datetime | CriterionValue | None = None
        seats: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        validate_scheduled = validate_date_field(self.scheduled, _coerce_datetime_like_criterion(criteria.scheduled))
        return all(
            [
                self._validate_field(self.destination, criteria.destination),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.ride_name, criteria.ride_name),
                validate_scheduled,
                self._validate_field(self.seats, criteria.seats),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReserveRideEvent":
        base_event = Event.parse(backend_event)
        kw = _reserve_ride_field_values(backend_event.data or {}, backend_event.timestamp)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **kw,
        )


class TripDetailsEvent(ReserveRideEvent):
    event_name: str = "TRIP_DETAILS"


class CancelReservationEvent(ReserveRideEvent):
    """event triggered when user cancels a reservation"""

    event_name: str = "CANCEL_RESERVATION"

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelReservationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        trip = data.get("tripData")
        if isinstance(trip, dict):
            ride = trip.get("ride") if isinstance(trip.get("ride"), dict) else {}
            flat: dict[str, Any] = {
                "pickup": trip.get("pickup"),
                "dropoff": trip.get("dropoff"),
                "rideName": ride.get("name") or ride.get("rideName"),
                "price": trip.get("price"),
                "seats": trip.get("seats"),
                "scheduled": data.get("scheduled"),
            }
            trip_sched = _scheduled_datetime_from_trip(trip)
            kw = _reserve_ride_field_values(
                flat,
                backend_event.timestamp,
                scheduled_override=trip_sched,
            )
        else:
            kw = _reserve_ride_field_values(data, backend_event.timestamp)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **kw,
        )


class SubmitTripReviewEvent(Event, BaseEventValidator):
    event_name: str = "SUBMIT_REVIEW"
    rating: float | int | None = None
    reviewer_name: str | None = None
    comment: str | None = None

    class ValidationCriteria(BaseModel):
        rating: float | CriterionValue | None = None
        reviewer_name: str | CriterionValue | None = None
        comment: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([self._validate_field(self.rating, criteria.rating), self._validate_field(self.reviewer_name, criteria.reviewer_name), self._validate_field(self.comment, criteria.comment)])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SubmitTripReviewEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        rev = data.get("review") if isinstance(data.get("review"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            rating=data.get("rating"),
            reviewer_name=data.get("name") or rev.get("name"),
            comment=rev.get("comment") or data.get("comment"),
        )


class SubmitReviewRouterEvent(Event):
    """Dispatches SUBMIT_REVIEW: autodrive trip review vs autolodge hotel review (merged map uses p13 entry)."""

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "Event":
        data = backend_event.data or {}
        if data.get("tripId") is not None or isinstance(data.get("tripData"), dict):
            return SubmitTripReviewEvent.parse(backend_event)
        from autoppia_iwa.src.demo_webs.projects.p08_autolodge.events import SubmitHotelReviewEvent

        return SubmitHotelReviewEvent.parse(backend_event)


class ViewAvailableTripsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_AVAILABLE_TRIPS"
    total_trips: int | None = None

    class ValidationCriteria(BaseModel):
        total_trips: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.total_trips, criteria.total_trips)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewAvailableTripsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            total_trips=data.get("totalTrips"),
        )


class BookTripEvent(ReserveRideEvent):
    event_name: str = "BOOK_TRIP"
    trip_id: str | None = None
    source: str | None = None

    class ValidationCriteria(ReserveRideEvent.ValidationCriteria):
        trip_id: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                super()._validate_criteria(criteria),
                self._validate_field(self.trip_id, criteria.trip_id),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookTripEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        kw = _reserve_ride_field_values(data, backend_event.timestamp)
        tid = data.get("tripId")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            trip_id=str(tid) if tid is not None else None,
            source=data.get("source"),
            **kw,
        )


class FilterTripsEvent(Event, BaseEventValidator):
    event_name: str = "FILTER_TRIPS"
    filter_type: str | None = None
    filter_value: str | None = None

    class ValidationCriteria(BaseModel):
        filter_type: str | CriterionValue | None = None
        filter_value: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.filter_type, criteria.filter_type),
                self._validate_field(self.filter_value, criteria.filter_value),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterTripsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            filter_type=data.get("filterType"),
            filter_value=data.get("filterValue"),
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
            return _parse_datetime_flexible(value)
        return None
    except (ValueError, TypeError):
        return None


def _datetime_from_event_timestamp(ts: Any) -> datetime:
    if isinstance(ts, str):
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt.replace(tzinfo=None) if dt.tzinfo else dt
        except (ValueError, TypeError):
            pass
    if isinstance(ts, int | float):
        try:
            return datetime.utcfromtimestamp(float(ts))
        except (ValueError, OSError, TypeError):
            pass
    return datetime.utcnow()


def parse_ride_scheduled(value: Any, event_timestamp: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.lower() == "now":
            return _datetime_from_event_timestamp(event_timestamp)
    parsed = parse_datetime(value if isinstance(value, str) else str(value))
    if isinstance(parsed, datetime):
        return parsed
    if isinstance(parsed, dt_time):
        return datetime.combine(date.today(), parsed)
    return None


def _scheduled_datetime_from_trip(trip: dict[str, Any]) -> datetime | None:
    date_raw = trip.get("date")
    time_raw = trip.get("time")
    if not date_raw:
        return None
    try:
        if isinstance(date_raw, str):
            day = datetime.fromisoformat(date_raw[:10]).date()
        else:
            return None
    except ValueError:
        return None
    if isinstance(time_raw, str):
        parts = time_raw.strip().split(":")
        if len(parts) >= 2:
            try:
                return datetime.combine(day, dt_time(int(parts[0]), int(parts[1])))
            except ValueError:
                pass
    t_part = parse_time(time_raw) if time_raw else None
    if isinstance(t_part, dt_time):
        return datetime.combine(day, t_part)
    if isinstance(t_part, datetime):
        return t_part
    return datetime.combine(day, dt_time.min)


def _reserve_ride_field_values(
    data: dict[str, Any],
    event_ts: Any,
    *,
    scheduled_override: datetime | None = None,
) -> dict[str, Any]:
    if scheduled_override is not None:
        scheduled = scheduled_override
    else:
        scheduled = parse_ride_scheduled(data.get("scheduled"), event_ts)
        if scheduled is None:
            scheduled = _datetime_from_event_timestamp(event_ts)
    price = data.get("price")
    seats = data.get("seats")
    return {
        "destination": str(data.get("dropoff") or ""),
        "location": str(data.get("pickup") or ""),
        "price": float(price) if price is not None else 0.0,
        "ride_name": str(data.get("rideName") or ""),
        "scheduled": scheduled,
        "seats": int(seats) if seats is not None else 1,
    }


EVENTS = [
    SearchLocationEvent,
    SearchDestinationEvent,
    EnterLocationEvent,
    EnterDestinationEvent,
    NextPickupEvent,
    SelectDateEvent,
    SelectTimeEvent,
    SelectCarEvent,
    SearchRideEvent,
    ReserveRideEvent,
    TripDetailsEvent,
    CancelReservationEvent,
    SubmitTripReviewEvent,
    SubmitReviewRouterEvent,
    ViewAvailableTripsEvent,
    BookTripEvent,
    FilterTripsEvent,
]

BACKEND_EVENT_TYPES = {
    "SEARCH_LOCATION": SearchLocationEvent,
    "SEARCH_DESTINATION": SearchDestinationEvent,
    "ENTER_LOCATION": EnterLocationEvent,
    "ENTER_DESTINATION": EnterDestinationEvent,
    "NEXT_PICKUP": NextPickupEvent,
    "SELECT_TIME": SelectTimeEvent,
    "SELECT_DATE": SelectDateEvent,
    "SEARCH": SearchRideEvent,
    "SELECT_CAR": SelectCarEvent,
    "RESERVE_RIDE": ReserveRideEvent,
    "TRIP_DETAILS": TripDetailsEvent,
    "CANCEL_RESERVATION": CancelReservationEvent,
    "SUBMIT_REVIEW": SubmitReviewRouterEvent,
    "VIEW_AVAILABLE_TRIPS": ViewAvailableTripsEvent,
    "BOOK_TRIP": BookTripEvent,
    "FILTER_TRIPS": FilterTripsEvent,
}
