from datetime import datetime

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue, validate_criterion


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class SearchHotelEvent(Event):
    """Event triggered when a user searches for a hotel"""

    event_name: str = "SEARCH_HOTEL"
    search_term: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    adults: int = 0
    children: int = 0
    infants: int = 0
    pets: int = 0

    class ValidationCriteria(BaseModel):
        """Criteria for validating hotel search events"""

        search_term: str | CriterionValue | None = None
        date_from: datetime | CriterionValue | None = None
        date_to: datetime | CriterionValue | None = None
        adults: int | CriterionValue | None = None
        children: int | CriterionValue | None = None
        infants: int | CriterionValue | None = None
        pets: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["search_term", "date_from", "date_to", "adults", "children", "infants", "pets"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        date_range = data.get("dateRange", {})
        guests = data.get("guests", {})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            search_term=data.get("searchTerm"),
            date_from=parse_datetime(date_range.get("from")),
            date_to=parse_datetime(date_range.get("to")),
            adults=guests.get("adults", 0),
            children=guests.get("children", 0),
            infants=guests.get("infants", 0),
            pets=guests.get("pets", 0),
        )


class SearchClearedEvent(Event):
    """Event triggered when the user clears the search input"""

    event_name: str = "SEARCH_CLEARED"
    source: str | None = None

    class ValidationCriteria(BaseModel):
        """Criteria for validating search cleared events"""

        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return not (criteria.source is not None and (self.source is None or not validate_criterion(self.source, criteria.source)))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchClearedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, source=data.get("source"))


class ViewHotelEvent(Event):
    """Event triggered when a user views a hotel listing"""

    event_name: str = "VIEW_HOTEL"
    hotel_id: str | None = None
    title: str | None = None
    location: str | None = None
    rating: float | None = None
    price: float | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    guests: int | None = None
    host_name: str | None = None
    host_since: int | None = None
    host_avatar: str | None = None
    amenities: list[str] = list

    class ValidationCriteria(BaseModel):
        hotel_id: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        price: float | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        host_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["hotel_id", "title", "location", "rating", "price", "guests", "host_name"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        dates = data.get("dates", {})
        host = data.get("host", {})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hotel_id=data.get("id"),
            title=data.get("title"),
            location=data.get("location"),
            rating=data.get("rating"),
            price=data.get("price"),
            date_from=parse_datetime(dates.get("from")),
            date_to=parse_datetime(dates.get("to")),
            guests=data.get("guests"),
            host_name=host.get("name"),
            host_since=host.get("since"),
            host_avatar=host.get("avatar"),
            amenities=data.get("amenities", []),
        )


class ReserveHotelEvent(Event):
    """Event triggered when a user reserves a hotel"""

    event_name: str = "RESERVE_HOTEL"
    hotel_id: str | None = None
    checkin: datetime | None = None
    checkout: datetime | None = None
    guests: int | None = None

    class ValidationCriteria(BaseModel):
        hotel_id: str | CriterionValue | None = None
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None
        guests: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["hotel_id", "checkin", "checkout", "guests"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReserveHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hotel_id=data.get("id"),
            checkin=parse_datetime(data.get("checkin")),
            checkout=parse_datetime(data.get("checkout")),
            guests=data.get("guests"),
        )


class IncreaseNumberOfGuestsEvent(Event):
    """Event triggered when a user increases the number of guests"""

    event_name: str = "INCREASE_NUMBER_OF_GUESTS"
    from_count: int | None = None
    to_count: int | None = None

    class ValidationCriteria(BaseModel):
        from_count: int | CriterionValue | None = None
        to_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        if criteria.from_count is not None and (self.from_count is None or not validate_criterion(self.from_count, criteria.from_count)):
            return False

        return not (criteria.to_count is not None and (self.to_count is None or not validate_criterion(self.to_count, criteria.to_count)))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "IncreaseNumberOfGuestsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, from_count=data.get("from"), to_count=data.get("to")
        )


class DecreaseNumberOfGuestsEvent(Event):
    """Event triggered when a user decreases the number of guests"""

    event_name: str = "DECREASE_NUMBER_OF_GUESTS"
    from_count: int | None = None
    to_count: int | None = None

    class ValidationCriteria(BaseModel):
        from_count: int | CriterionValue | None = None
        to_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        if criteria.from_count is not None and (self.from_count is None or not validate_criterion(self.from_count, criteria.from_count)):
            return False

        return not (criteria.to_count is not None and (self.to_count is None or not validate_criterion(self.to_count, criteria.to_count)))

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DecreaseNumberOfGuestsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, from_count=data.get("from"), to_count=data.get("to")
        )


class EditCheckInOutDatesEvent(Event):
    """Event triggered when a user edits check-in and check-out dates"""

    event_name: str = "EDIT_CHECK_IN_OUT_DATES"
    checkin: datetime | None = None
    checkout: datetime | None = None
    source: str | None = None

    class ValidationCriteria(BaseModel):
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["checkin", "checkout", "source"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "EditCheckInOutDatesEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            checkin=parse_datetime(data.get("checkin")),
            checkout=parse_datetime(data.get("checkout")),
            source=data.get("source"),
        )


class ConfirmAndPayEvent(Event):
    """Event triggered when a user confirms a reservation and pays"""

    event_name: str = "CONFIRM_AND_PAY"
    checkin: datetime | None = None
    checkout: datetime | None = None
    guests: int | None = None
    listing_title: str | None = None
    price_per_night: float | None = None
    nights: int | None = None
    price_subtotal: float | None = None
    cleaning_fee: float | None = None
    service_fee: float | None = None
    total: float | None = None
    payment_method: str | None = None
    card_number: str | None = None
    expiration: str | None = None
    cvv: str | None = None
    country: str | None = None
    source: str | None = None

    class ValidationCriteria(BaseModel):
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        listing_title: str | CriterionValue | None = None
        total: float | CriterionValue | None = None
        payment_method: str | CriterionValue | None = None
        country: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["checkin", "checkout", "guests", "listing_title", "total", "payment_method", "country"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ConfirmAndPayEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            checkin=parse_datetime(data.get("checkin")),
            checkout=parse_datetime(data.get("checkout")),
            guests=data.get("guests"),
            listing_title=data.get("listingTitle"),
            price_per_night=data.get("pricePerNight"),
            nights=data.get("nights"),
            price_subtotal=data.get("priceSubtotal"),
            cleaning_fee=data.get("cleaningFee"),
            service_fee=data.get("serviceFee"),
            total=data.get("total"),
            payment_method=data.get("paymentMethod"),
            card_number=data.get("cardNumber"),
            expiration=data.get("expiration"),
            cvv=data.get("cvv"),
            country=data.get("country"),
            source=data.get("source"),
        )


class MessageHostEvent(Event):
    """Event triggered when a user sends a message to the host"""

    event_name: str = "MESSAGE_HOST"
    message: str | None = None
    host_name: str | None = None
    source: str | None = None

    class ValidationCriteria(BaseModel):
        message: str | CriterionValue | None = None
        host_name: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        for field in ["message", "host_name", "source"]:
            value = getattr(self, field)
            expected = getattr(criteria, field)
            if expected is not None and (value is None or not validate_criterion(value, expected)):
                return False

        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "MessageHostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            message=data.get("message"),
            host_name=data.get("hostName"),
            source=data.get("source"),
        )


class BackToAllHotelsEvent(Event):
    """Event triggered when a user navigates back to the list of all hotels"""

    event_name: str = "BACK_TO_ALL_HOTELS"

    class ValidationCriteria(BaseModel):
        """No specific fields for this event, but placeholder for extensibility"""

        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True  # No data to validate for this event

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BackToAllHotelsEvent":
        base_event = Event.parse(backend_event)
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id)
