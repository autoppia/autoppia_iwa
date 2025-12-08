from datetime import datetime

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import parse_datetime, validate_date_field


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
        datesFrom: datetime | CriterionValue | None = None
        datesTo: datetime | CriterionValue | None = None
        adults: int | CriterionValue | None = None
        children: int | CriterionValue | None = None
        infants: int | CriterionValue | None = None
        pets: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_from_valid = validate_date_field(self.date_from, criteria.datesFrom)
        date_to_valid = validate_date_field(self.date_to, criteria.datesTo)
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
            search_term=data.get("searchTerm", ""),
            date_from=parse_datetime(date_range.get("from")),
            date_to=parse_datetime(date_range.get("to")),
            adults=guests.get("adults", 0),
            children=guests.get("children", 0),
            infants=guests.get("infants", 0),
            pets=guests.get("pets", 0),
        )


class HotelInfo(BaseModel):
    """Hotel information used in multiple events."""

    title: str
    location: str
    price: int
    rating: float
    reviews: int
    guests: int
    max_guests: int
    datesFrom: datetime
    datesTo: datetime
    baths: int
    bedrooms: int
    beds: int
    host_name: str
    amenities: list[str]

    class ValidationCriteria(BaseModel):
        title: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        price: int | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        guests: int | CriterionValue | None = None
        max_guests: int | CriterionValue | None = None
        datesFrom: datetime | CriterionValue | None = None
        datesTo: datetime | CriterionValue | None = None
        baths: int | CriterionValue | None = None
        bedrooms: int | CriterionValue | None = None
        beds: int | CriterionValue | None = None
        host_name: str | CriterionValue | None = None
        amenities: str | list | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        date_from_valid = validate_date_field(self.datesFrom, criteria.datesFrom)
        date_to_valid = validate_date_field(self.datesTo, criteria.datesTo)

        def validate_amenities(amenities, criteria_amenities):
            if criteria_amenities is None:
                return True
            if isinstance(criteria_amenities, str):
                return any(criteria_amenities.lower() in a.lower() for a in amenities)
            elif isinstance(criteria_amenities, list):
                return all(a in amenities for a in criteria_amenities)
            elif hasattr(criteria_amenities, "operator"):
                op = criteria_amenities.operator
                val = criteria_amenities.value
                if op == ComparisonOperator.EQUALS:
                    return any(val.lower() == a.lower() for a in amenities)
                elif op == ComparisonOperator.CONTAINS:
                    return any(val.lower() in a.lower() for a in amenities)
                elif op == ComparisonOperator.NOT_CONTAINS:
                    return all(val.lower() not in a.lower() for a in amenities)
                elif op == ComparisonOperator.IN_LIST:
                    if isinstance(val, str):
                        return val in amenities
                    if isinstance(val, list):
                        return any(a in amenities for a in val)
                elif op == ComparisonOperator.NOT_IN_LIST:
                    if isinstance(val, str):
                        return val not in amenities
                    if isinstance(val, list):
                        return all(a not in amenities for a in val)
            return True

        result = all(
            [
                date_to_valid,
                date_from_valid,
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.reviews, criteria.reviews),
                self._validate_field(self.guests, criteria.guests),
                self._validate_field(self.max_guests, criteria.max_guests),
                self._validate_field(self.baths, criteria.baths),
                self._validate_field(self.bedrooms, criteria.bedrooms),
                self._validate_field(self.beds, criteria.beds),
                self._validate_field(self.host_name, criteria.host_name),
                validate_amenities(self.amenities, criteria.amenities),
            ]
        )
        return result

    @classmethod
    def parse(cls, data) -> "HotelInfo":
        hotel = data.get("hotel", {})
        host = hotel.get("host", {})
        amenities = []
        for a in hotel.get("amenities", []):
            if isinstance(a, dict) and "title" in a:
                amenities.append(a["title"])
            elif isinstance(a, list):
                amenities.extend(a)
            elif isinstance(a, str):
                amenities.append(a)

        date_from = hotel.get("dateFrom") or hotel.get("datesFrom") or (hotel.get("dates") or {}).get("from")
        date_to = hotel.get("datesTo") or (hotel.get("dates") or {}).get("to")
        return cls(
            title=hotel.get("title"),
            location=hotel.get("location"),
            price=hotel.get("price"),
            rating=hotel.get("rating"),
            reviews=hotel.get("reviews"),
            guests=hotel.get("guests"),
            max_guests=hotel.get("maxGuests", 0),
            datesFrom=parse_datetime(date_from),
            datesTo=parse_datetime(date_to),
            baths=hotel.get("baths", 0),
            bedrooms=hotel.get("bedrooms", 0),
            beds=hotel.get("beds", 0),
            host_name=host.get("name", ""),
            amenities=amenities,
        )


class ViewHotelEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user views a hotel listing"""

    event_name: str = "VIEW_HOTEL"

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return HotelInfo._validate_criteria(self, criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewHotelEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse({"hotel": backend_event.data or {}})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **hotel_info.model_dump(),
        )


class AddToWishlistEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user views a hotel listing"""

    event_name: str = "ADD_TO_WISHLIST"

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return HotelInfo._validate_criteria(self, criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddToWishlistEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse({"hotel": backend_event.data or {}})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **hotel_info.model_dump(),
        )


class RemoveFromWishlistEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user removes a hotel from their wishlist."""

    event_name: str = "REMOVE_FROM_WISHLIST"

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return HotelInfo._validate_criteria(self, criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "RemoveFromWishlistEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse({"hotel": backend_event.data or {}})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            **hotel_info.model_dump(),
        )


class ShareHotelEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user views a hotel listing"""

    event_name: str = "SHARE_HOTEL"
    email: str

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all([HotelInfo._validate_criteria(self, criteria), self._validate_field(self.email, criteria.email)])

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ShareHotelEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        email = data.get("email", "")
        hotel_info = HotelInfo.parse({"hotel": data})

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            email=email,
            **hotel_info.model_dump(),
        )


class IncreaseNumberOfGuestsEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "INCREASE_NUMBER_OF_GUESTS"
    guests_to: int

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        guests_to: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return all(
            [
                self._validate_field(self.guests_to, getattr(criteria, "guests_to", None)),
                HotelInfo._validate_criteria(self, criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "IncreaseNumberOfGuestsEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse(backend_event.data or {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            guests_to=(backend_event.data or {}).get("to", 0),
            **hotel_info.model_dump(),
        )


class EditNumberOfGuestsEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "EDIT_NUMBER_OF_GUESTS"
    guests_to: int

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        guests_to: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return all(
            [
                self._validate_field(self.guests_to, getattr(criteria, "guests_to", None)),
                HotelInfo._validate_criteria(self, criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditNumberOfGuestsEvent":
        base_event = Event.parse(backend_event)
        hotel_info = HotelInfo.parse(backend_event.data or {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            guests_to=(backend_event.data or {}).get("to", 0),
            **hotel_info.model_dump(),
        )


class SubmitHotelReviewEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user submits a review/rating for a hotel"""

    event_name: str = "SUBMIT_HOTEL_REVIEW"
    comment: str | None = None

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        comment: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                HotelInfo._validate_criteria(self, criteria),
                self._validate_field(self.comment, criteria.comment),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SubmitHotelReviewEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        hotel_info = HotelInfo.parse(
            {
                "hotel": {
                    "title": data.get("title"),
                    "location": data.get("location"),
                    "price": data.get("price"),
                    "rating": data.get("rating"),
                    "reviews": data.get("reviews"),
                    "guests": data.get("guests"),
                    "maxGuests": data.get("maxGuests"),
                    "datesFrom": data.get("datesFrom") or (data.get("dates") or {}).get("from"),
                    "datesTo": data.get("datesTo") or (data.get("dates") or {}).get("to"),
                    "baths": data.get("baths", 0),
                    "bedrooms": data.get("bedrooms", 0),
                    "beds": data.get("beds", 0),
                    "host": {"name": data.get("host_name", "")},
                    "amenities": data.get("amenities", []),
                }
            }
        )

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            comment=data.get("comment"),
            **hotel_info.model_dump(),
        )


class SubmitReviewEvent(SubmitHotelReviewEvent):
    """Alias for frontend event SUBMIT_REVIEW"""

    event_name: str = "SUBMIT_REVIEW"


class FilterHotelsEvent(Event, BaseEventValidator):
    """Event triggered when user filters hotels list."""

    event_name: str = "FILTER_HOTELS"
    rating: float | None = None
    price: float | None = None
    region: str | None = None
    results: int | None = None

    class ValidationCriteria(BaseModel):
        rating: float | CriterionValue | None = None
        price: float | CriterionValue | None = None
        region: str | CriterionValue | None = None
        results: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.price, criteria.price),
                self._validate_field(self.region, criteria.region),
                self._validate_field(self.results, criteria.results),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FilterHotelsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            rating=data.get("rating"),
            price=data.get("price"),
            region=data.get("region"),
            results=data.get("results"),
        )


class ApplyFiltersEvent(FilterHotelsEvent):
    """Frontend logs APPLY_FILTERS; reuse filter payload shape."""

    event_name: str = "APPLY_FILTERS"

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ApplyFiltersEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            rating=data.get("minRating") or data.get("rating"),
            price=data.get("maxPrice") or data.get("price"),
            region=data.get("region"),
            results=data.get("results"),
        )


class ReserveHotelEvent(Event, BaseEventValidator, HotelInfo):
    """Event triggered when a user reserves a hotel"""

    event_name: str = "RESERVE_HOTEL"
    guests_set: int | None = None

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        guests_set: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.guests_set, criteria.guests_set),
                HotelInfo._validate_criteria(self, criteria),
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
            guests_set=data.get("guests_set"),
            **hotel_info.model_dump(),
        )


class EditCheckInOutDatesEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "EDIT_CHECK_IN_OUT_DATES"
    checkin: datetime
    checkout: datetime

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        checkin: datetime | CriterionValue | None = None
        checkout: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        checkin_valid = validate_date_field(self.checkin, criteria.checkin)
        checkout_valid = validate_date_field(self.checkout, criteria.checkout)
        return all(
            [
                checkin_valid,
                checkout_valid,
                HotelInfo._validate_criteria(self, criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditCheckInOutDatesEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        d_range = data.get("dateRange", {})
        checkin = parse_datetime(d_range.get("from"))
        checkout = parse_datetime(d_range.get("to"))

        hotel_info = HotelInfo.parse(data)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            checkin=checkin,
            checkout=checkout,
            **hotel_info.model_dump(),
        )


class ConfirmAndPayEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "CONFIRM_AND_PAY"
    nights: int
    price_subtotal: int
    total: int
    card_number: str
    expiration: str
    cvv: str
    country: str
    guests_set: int | None = None
    zipcode: str | None = None

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        """Criteria for validating confirm and pay events"""

        nights: int | CriterionValue | None = None
        priceSubtotal: int | CriterionValue | None = None
        total: int | CriterionValue | None = None
        country: str | CriterionValue | None = None
        cardNumber: str | CriterionValue | None = None
        cvv: str | CriterionValue | None = None
        expiration: str | CriterionValue | None = None
        guests_set: int | CriterionValue | None = None
        zipcode: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.nights, criteria.nights),
                self._validate_field(self.price_subtotal, criteria.priceSubtotal),
                self._validate_field(self.total, criteria.total),
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.card_number, criteria.cardNumber),
                self._validate_field(self.expiration, criteria.expiration),
                self._validate_field(self.cvv, criteria.cvv),
                self._validate_field(self.guests_set, criteria.guests_set),
                self._validate_field(self.zipcode, criteria.zipcode),
                HotelInfo._validate_criteria(self, criteria),
            ]
        )


class PaymentMethodSelectedEvent(Event, BaseEventValidator):
    """Event when user selects payment method."""

    event_name: str = "PAYMENT_METHOD_SELECTED"
    method: str | None = None
    hotel_id: int | None = None
    title: str | None = None

    class ValidationCriteria(BaseModel):
        method: str | CriterionValue | None = None
        hotel_id: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.method, criteria.method),
                self._validate_field(self.hotel_id, criteria.hotel_id),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PaymentMethodSelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            method=data.get("method"),
            hotel_id=data.get("hotelId") or data.get("id"),
            title=data.get("title"),
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ConfirmAndPayEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        hotel = HotelInfo.parse(data)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            nights=data.get("nights"),
            price_subtotal=data.get("priceSubtotal"),
            total=data.get("total"),
            card_number=data.get("cardNumber", ""),
            expiration=data.get("expiration", ""),
            cvv=data.get("cvv", ""),
            country=data.get("country", ""),
            guests_set=data.get("guests_set"),
            zipcode=data.get("zip"),
            **hotel.model_dump(),
        )


class MessageHostEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "MESSAGE_HOST"
    message: str

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        message: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.message, criteria.message),
                HotelInfo._validate_criteria(self, criteria),
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
            **hotel.model_dump(),
        )


class BackToAllHotelsEvent(Event, BaseEventValidator, HotelInfo):
    event_name: str = "BACK_TO_ALL_HOTELS"

    class ValidationCriteria(HotelInfo.ValidationCriteria):
        pass  # No fields to validate

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return HotelInfo._validate_criteria(self, criteria)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BackToAllHotelsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        hotel = HotelInfo.parse(data)
        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, **hotel.model_dump())


class WishlistOpenedEvent(Event, BaseEventValidator):
    """User opens wishlist page."""

    event_name: str = "WISHLIST_OPENED"
    count: int | None = None

    class ValidationCriteria(BaseModel):
        count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.count, criteria.count)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "WishlistOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            count=data.get("count"),
        )


class BookFromWishlistEvent(Event, BaseEventValidator):
    """User proceeds to book from wishlist."""

    event_name: str = "BOOK_FROM_WISHLIST"
    hotel_id: int | None = None
    title: str | None = None

    class ValidationCriteria(BaseModel):
        hotel_id: int | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.hotel_id, criteria.hotel_id),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BookFromWishlistEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            hotel_id=data.get("hotelId") or data.get("id"),
            title=data.get("title"),
        )


class PopularHotelsViewedEvent(Event, BaseEventValidator):
    """User views popular hotels page."""

    event_name: str = "POPULAR_HOTELS_VIEWED"
    count: int | None = None

    class ValidationCriteria(BaseModel):
        count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.count, criteria.count)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PopularHotelsViewedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            count=data.get("count"),
        )


class HelpViewedEvent(Event, BaseEventValidator):
    """User opens help page."""

    event_name: str = "HELP_VIEWED"
    page: str | None = None

    class ValidationCriteria(BaseModel):
        page: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.page, criteria.page)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "HelpViewedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            page=data.get("page") or data.get("source"),
        )


class FaqOpenedEvent(Event, BaseEventValidator):
    """User opens an FAQ item."""

    event_name: str = "FAQ_OPENED"
    question: str | None = None

    class ValidationCriteria(BaseModel):
        question: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.question, criteria.question)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FaqOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            question=data.get("question"),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================

EVENTS = [
    SearchHotelEvent,
    ViewHotelEvent,
    SubmitHotelReviewEvent,
    SubmitReviewEvent,
    FilterHotelsEvent,
    ApplyFiltersEvent,
    ReserveHotelEvent,
    IncreaseNumberOfGuestsEvent,
    EditNumberOfGuestsEvent,
    EditCheckInOutDatesEvent,
    PaymentMethodSelectedEvent,
    ConfirmAndPayEvent,
    MessageHostEvent,
    AddToWishlistEvent,
    RemoveFromWishlistEvent,
    ShareHotelEvent,
    BackToAllHotelsEvent,
    WishlistOpenedEvent,
    BookFromWishlistEvent,
    PopularHotelsViewedEvent,
    HelpViewedEvent,
    FaqOpenedEvent,
]

BACKEND_EVENT_TYPES = {
    "SEARCH_HOTEL": SearchHotelEvent,
    "VIEW_HOTEL": ViewHotelEvent,
    "SUBMIT_HOTEL_REVIEW": SubmitHotelReviewEvent,
    "SUBMIT_REVIEW": SubmitReviewEvent,
    "FILTER_HOTELS": FilterHotelsEvent,
    "APPLY_FILTERS": ApplyFiltersEvent,
    "RESERVE_HOTEL": ReserveHotelEvent,
    "INCREASE_NUMBER_OF_GUESTS": IncreaseNumberOfGuestsEvent,
    "EDIT_NUMBER_OF_GUESTS": EditNumberOfGuestsEvent,
    "EDIT_CHECK_IN_OUT_DATES": EditCheckInOutDatesEvent,
    "PAYMENT_METHOD_SELECTED": PaymentMethodSelectedEvent,
    "CONFIRM_AND_PAY": ConfirmAndPayEvent,
    "MESSAGE_HOST": MessageHostEvent,
    "ADD_TO_WISHLIST": AddToWishlistEvent,
    "REMOVE_FROM_WISHLIST": RemoveFromWishlistEvent,
    "SHARE_HOTEL": ShareHotelEvent,
    "BACK_TO_ALL_HOTELS": BackToAllHotelsEvent,
    "WISHLIST_OPENED": WishlistOpenedEvent,
    "BOOK_FROM_WISHLIST": BookFromWishlistEvent,
    "POPULAR_HOTELS_VIEWED": PopularHotelsViewedEvent,
    "HELP_VIEWED": HelpViewedEvent,
    "FAQ_OPENED": FaqOpenedEvent,
}
