from datetime import datetime

from dateutil import parser
from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import validate_date_field


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return parser.isoparse(value)
    except (ValueError, TypeError):
        return None


class SearchHotelEvent(Event, BaseEventValidator):
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
        date_from_valid = validate_date_field(self.date_from, criteria.date_from)
        date_to_valid = validate_date_field(self.date_to, criteria.date_to)
        return all(
            [
                self._validate_field(self.search_term, criteria.search_term),
                date_from_valid,
                date_to_valid,
                self._validate_field(self.adults, criteria.adults),
                self._validate_field(self.children, criteria.children),
                self._validate_field(self.infants, criteria.infants),
                self._validate_field(self.pets, criteria.pets),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchHotelEvent":
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


# class SearchClearedEvent(Event, BaseEventValidator):
#     """Event triggered when the user clears the search input"""
#
#     event_name: str = "SEARCH_CLEARED"
#     source: str | None = None
#
#     class ValidationCriteria(BaseModel):
#         source: str | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         return self._validate_field(self.source, criteria.source)
#
#     @classmethod
#     def parse(cls, backend_event: BackendEvent) -> "SearchClearedEvent":
#         base_event = Event.parse(backend_event)
#         data = backend_event.data or {}
#
#         return cls(
#             event_name=base_event.event_name,
#             timestamp=base_event.timestamp,
#             web_agent_id=base_event.web_agent_id,
#             user_id=base_event.user_id,
#             source=data.get("source"),
#         )


class HotelInfo(BaseModel):
    # hotel_id: str
    title: str
    location: str
    price: int
    rating: float
    reviews: int
    guests: int
    datesFrom: datetime
    datesTo: datetime
    baths: int
    bedrooms: int
    beds: int
    host_name: str
    # host_since: int
    # host_avatar: str
    amenities: list[dict[str, str]]

    class ValidationCriteria(BaseModel):
        # hotel_id: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        datesFrom: datetime | CriterionValue | None = None
        datesTo: datetime | CriterionValue | None = None
        baths: int | CriterionValue | None = None
        bedrooms: int | CriterionValue | None = None
        beds: int | CriterionValue | None = None
        host_name: str | CriterionValue | None = None
        # host_since: int | CriterionValue | None = None
        # host_avatar: str | CriterionValue | None = None
        amenities: list[dict[str, str]] | None = None

    def _validate_criteria(self, criteria: "HotelInfo.ValidationCriteria" | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.hotel_id, criteria.hotel_id),
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.reviews, criteria.reviews),
                self._validate_field(self.guests, criteria.guests),
                self._validate_field(self.datesFrom, criteria.datesFrom),
                self._validate_field(self.datesTo, criteria.datesTo),
                self._validate_field(self.baths, criteria.baths),
                self._validate_field(self.bedrooms, criteria.bedrooms),
                self._validate_field(self.beds, criteria.beds),
                self._validate_field(self.host_name, criteria.host_name),
                # self._validate_field(self.host_since, criteria.host_since),
                # self._validate_field(self.host_avatar, criteria.host_avatar),
                self._validate_field(self.amenities, criteria.amenities),
            ]
        )

    @classmethod
    def parse(cls, data) -> "HotelInfo":
        data = data.get("hotel", {})
        return cls(
            # hotel_id=data.get("id"),
            title=data.get("title"),
            location=data.get("location"),
            price=data.get("price"),
            rating=data.get("rating"),
            reviews=data.get("reviews"),
            guests=data.get("guests"),
            datesFrom=parse_datetime(data.get("datesFrom")),
            datesTo=parse_datetime(data.get("datesTo")),
            baths=data.get("baths", 0),
            bedrooms=data.get("bedrooms", 0),
            beds=data.get("beds", 0),
            host_name=data.get("name", data.get("host")),
            # host_since=data.get("since"),
            # host_avatar=data.get("avatar"),
            amenities=data.get("amenities", []),
        )


class ViewHotelEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user views a hotel listing"""

    event_name: str = "VIEW_HOTEL"
    # hotel_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_from_valid = self._validate_field(self.date_from, criteria.datesFrom)
        date_to_valid = self._validate_field(self.date_to, criteria.datesTo)
        return all(
            [
                # self._validate_field(self.hotel_id, criteria.hotel_id),
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.price, criteria.price),
                date_from_valid,
                date_to_valid,
                self._validate_field(self.guests, criteria.guests),
                self._validate_field(self.host_name, criteria.host_name),
                self._validate_field(self.amenities, criteria.amenities),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        dates = data.get("dates", {})
        hotel_info = HotelInfo.parse({"hotel": data})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date_from=parse_datetime(dates.get("from")),
            date_to=parse_datetime(dates.get("to")),
            **hotel_info.model_dump(),
        )


class IncreaseNumberOfGuestsEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "INCREASE_NUMBER_OF_GUESTS"
    # from_guests: int
    to_guests: int

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        """Criteria for validating increase guests events"""

        # from_guests: int | CriterionValue | None = None
        to_guests: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.from_guests, criteria.from_guests),
                self._validate_field(self.to_guests, criteria.to_guests),
                super()._validate_criteria(criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "IncreaseNumberOfGuestsEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse(backend_event.data)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # from_guests=backend_event.data.get("from", 0),
            to_guests=backend_event.data.get("to", 0),
            **hotel_info.model_dump(),
        )


# class DecreaseNumberOfGuestsEvent(Event, BaseEventValidator, HotelInfo):
#     event_name: str = "DECREASE_NUMBER_OF_GUESTS"
#     from_guests: int
#     to_guests: int
#
#     class ValidationCriteria(HotelInfo.ValidationCriteria):
#         """Criteria for validating decrease guests events"""
#
#         from_guests: int | CriterionValue | None = None
#         to_guests: int | CriterionValue | None = None
#
#     def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
#         if not criteria:
#             return True
#         return all(
#             [
#                 self._validate_field(self.from_guests, criteria.from_guests),
#                 self._validate_field(self.to_guests, criteria.to_guests),
#                 super()._validate_criteria(criteria),
#             ]
#         )
#
#     @classmethod
#     def parse(cls, backend_event: BackendEvent) -> "DecreaseNumberOfGuestsEvent":
#         base_event = Event.parse(backend_event)
#         hotel_info = HotelInfo.parse(backend_event.data)
#         data = backend_event.data
#         from_guests = data.get("from", 0)
#         to_guests = data.get("to", 0)
#         return cls(
#             event_name=base_event.event_name,
#             timestamp=base_event.timestamp,
#             web_agent_id=base_event.web_agent_id,
#             user_id=base_event.user_id,
#             from_guests=from_guests,
#             to_guests=to_guests,
#             **hotel_info.model_dump(),
#         )


class ReserveHotelEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user reserves a hotel"""

    event_name: str = "RESERVE_HOTEL"
    hotel_id: str | None = None
    guests: int | None = None
    checkin: datetime | None = None
    checkout: datetime | None = None

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        hotel_id: str | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        date_from: datetime | None = None
        date_to: datetime | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_from_valid = validate_date_field(self.date_from, criteria.date_from)
        date_to_valid = validate_date_field(self.date_to, criteria.date_to)
        return all(
            [
                self._validate_field(self.hotel_id, criteria.hotel_id),
                self._validate_field(self.guests, criteria.guests),
                date_from_valid,
                date_to_valid,
                super()._validate_criteria(criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ReserveHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        hotel_info = HotelInfo.parse(data)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hotel_id=data.get("id"),
            guests=data.get("guests"),
            checkin=parse_datetime(data.get("checkin")),
            checkout=parse_datetime(data.get("checkout")),
            **hotel_info.model_dump(),
        )


class EditCheckInOutDatesEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "EDIT_CHECK_IN_OUT_DATES"
    checkin: datetime
    checkout: datetime
    source: str

    class ValidationCriteria(BaseModel):
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        checkin_valid = validate_date_field(self.checkin, criteria.checkin)
        checkout_valid = validate_date_field(self.checkout, criteria.checkout)
        return all(
            [
                checkin_valid,
                checkout_valid,
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditCheckInOutDatesEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        checkin = parse_datetime(data.get("checkin"))
        checkout = parse_datetime(data.get("checkout"))
        source = data.get("source", "")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            checkin=checkin,
            checkout=checkout,
            source=source,
        )


class ConfirmAndPayEvent(Event, BaseEventValidator):
    event_name: str = "CONFIRM_AND_PAY"
    checkin: datetime
    checkout: datetime
    guests: int
    listing_title: str
    price_per_night: int
    nights: int
    price_subtotal: int
    cleaning_fee: int
    service_fee: int
    total: int
    payment_method: str
    card_number: str
    expiration: str
    cvv: str
    country: str
    source: str

    class ValidationCriteria(BaseModel):
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        listingTitle: str | CriterionValue | None = None
        pricePerNight: int | CriterionValue | None = None
        nights: int | CriterionValue | None = None
        priceSubtotal: int | CriterionValue | None = None
        cleaningFee: int | CriterionValue | None = None
        serviceFee: int | CriterionValue | None = None
        total: int | CriterionValue | None = None
        paymentMethod: str | CriterionValue | None = None
        country: str | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        checkin_valid = validate_date_field(self.checkin, criteria.checkin)
        checkout_valid = validate_date_field(self.checkout, criteria.checkout)
        return all(
            [
                checkin_valid,
                checkout_valid,
                self._validate_field(self.guests, criteria.guests),
                self._validate_field(self.listing_title, criteria.listingTitle),
                self._validate_field(self.price_per_night, criteria.pricePerNight),
                self._validate_field(self.nights, criteria.nights),
                self._validate_field(self.price_subtotal, criteria.priceSubtotal),
                self._validate_field(self.cleaning_fee, criteria.cleaningFee),
                self._validate_field(self.service_fee, criteria.serviceFee),
                self._validate_field(self.total, criteria.total),
                self._validate_field(self.payment_method, criteria.paymentMethod),
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ConfirmAndPayEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            checkin=parse_datetime(data.get("checkin")),
            checkout=parse_datetime(data.get("checkout")),
            guests=data.get("guests"),
            listing_title=data.get("listingTitle", ""),
            price_per_night=data.get("pricePerNight"),
            nights=data.get("nights"),
            price_subtotal=data.get("priceSubtotal"),
            cleaning_fee=data.get("cleaningFee"),
            service_fee=data.get("serviceFee"),
            total=data.get("total"),
            payment_method=data.get("paymentMethod", ""),
            card_number=data.get("cardNumber", ""),
            expiration=data.get("expiration", ""),
            cvv=data.get("cvv", ""),
            country=data.get("country", ""),
            source=data.get("source", ""),
        )


class MessageHostEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "MESSAGE_HOST"
    message: str
    host_name: str
    # source: str

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        message: str | CriterionValue | None = None
        hostName: str | CriterionValue | None = None
        # source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.message, criteria.message),
                self._validate_field(self.host_name, criteria.hostName),
                # self._validate_field(self.source, criteria.source),
                super()._validate_criteria(criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "MessageHostEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        hotel = HotelInfo.parse(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            message=data.get("message", ""),
            host_name=data.get("hostName", ""),
            # source=data.get("source", ""),
            **hotel.model_dunp(),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================

EVENTS = [
    SearchHotelEvent,
    # SearchClearedEvent,
    ViewHotelEvent,
    ReserveHotelEvent,
    IncreaseNumberOfGuestsEvent,
    # DecreaseNumberOfGuestsEvent,
    EditCheckInOutDatesEvent,
    ConfirmAndPayEvent,
    MessageHostEvent,
]

BACKEND_EVENT_TYPES = {
    "SEARCH_HOTEL": SearchHotelEvent,
    # "SEARCH_CLEARED": SearchClearedEvent,
    "VIEW_HOTEL": ViewHotelEvent,
    "RESERVE_HOTEL": ReserveHotelEvent,
    "INCREASE_NUMBER_OF_GUESTS": IncreaseNumberOfGuestsEvent,
    # "DECREASE_NUMBER_OF_GUESTS": DecreaseNumberOfGuestsEvent,
    "EDIT_CHECK_IN_OUT_DATES": EditCheckInOutDatesEvent,
    "CONFIRM_AND_PAY": ConfirmAndPayEvent,
    "MESSAGE_HOST": MessageHostEvent,
}
