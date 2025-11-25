from __future__ import annotations

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

class DateDropdownOpenedEvent(Event, BaseEventValidator):
    """User focuses the reservation date selector."""

    event_name: str = "DATE_DROPDOWN_OPENED"
    selected_date: str | None = None

    class ValidationCriteria(BaseModel):
        selected_date: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.selected_date, criteria.selected_date),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DateDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            selected_date=data.get('date'),
        )


class TimeDropdownOpenedEvent(Event, BaseEventValidator):
    """User opens the reservation time dropdown."""

    event_name: str = "TIME_DROPDOWN_OPENED"
    selected_time: str | None = None

    class ValidationCriteria(BaseModel):
        selected_time: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.selected_time, criteria.selected_time),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "TimeDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            selected_time=data.get('time'),
        )


class PeopleDropdownOpenedEvent(Event, BaseEventValidator):
    """User opens the guest-count dropdown."""

    event_name: str = "PEOPLE_DROPDOWN_OPENED"
    people_count: int | None = None

    class ValidationCriteria(BaseModel):
        people_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.people_count, criteria.people_count),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PeopleDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            people_count=data.get('people'),
        )


class SearchRestaurantEvent(Event, BaseEventValidator):
    """Free-text restaurant search."""

    event_name: str = "SEARCH_RESTAURANT"
    query: str | None = None

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.query, criteria.query),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get('query'),
        )


class ViewRestaurantEvent(Event, BaseEventValidator):
    """User opens a restaurant detail card."""

    event_name: str = "VIEW_RESTAURANT"
    restaurant_id: str | None = None
    restaurant_name: str | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.restaurant_id, criteria.restaurant_id),
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get('restaurantId'),
            restaurant_name=data.get('restaurantName'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
        )


class ViewFullMenuEvent(Event, BaseEventValidator):
    """User expands the restaurant's full menu with booking context."""

    event_name: str = "VIEW_FULL_MENU"
    restaurant_id: str | None = None
    restaurant_name: str | None = None
    action: str | None = None
    time: str | None = None
    selected_date: str | None = None
    people: int | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None
    menu: list[str] | None = None

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: str | CriterionValue | None = None
        people: int | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        menu: list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.restaurant_id, criteria.restaurant_id),
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.action, criteria.action),
            self._validate_field(self.time, criteria.time),
            self._validate_field(self.selected_date, criteria.selected_date),
            self._validate_field(self.people, criteria.people),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
            self._validate_field(self.menu, criteria.menu),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewFullMenuEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get('restaurantId'),
            restaurant_name=data.get('restaurantName'),
            action=data.get('action'),
            time=data.get('time'),
            selected_date=data.get('date'),
            people=data.get('people'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
            menu=data.get('menu'),
        )


class CollapseMenuEvent(Event, BaseEventValidator):
    """User collapses the expanded menu view."""

    event_name: str = "COLLAPSE_MENU"
    restaurant_id: str | None = None
    restaurant_name: str | None = None
    action: str | None = None
    time: str | None = None
    selected_date: str | None = None
    people: int | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None
    menu: list[str] | None = None

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: str | CriterionValue | None = None
        people: int | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        menu: list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.restaurant_id, criteria.restaurant_id),
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.action, criteria.action),
            self._validate_field(self.time, criteria.time),
            self._validate_field(self.selected_date, criteria.selected_date),
            self._validate_field(self.people, criteria.people),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
            self._validate_field(self.menu, criteria.menu),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CollapseMenuEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get('restaurantId'),
            restaurant_name=data.get('restaurantName'),
            action=data.get('action'),
            time=data.get('time'),
            selected_date=data.get('date'),
            people=data.get('people'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
            menu=data.get('menu'),
        )


class BookRestaurantEvent(Event, BaseEventValidator):
    """CTA click to book a restaurant."""

    event_name: str = "BOOK_RESTAURANT"
    restaurant_name: str | None = None
    time: str | None = None
    selected_date: str | None = None
    people: int | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None

    class ValidationCriteria(BaseModel):
        restaurant_name: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: str | CriterionValue | None = None
        people: int | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.time, criteria.time),
            self._validate_field(self.selected_date, criteria.selected_date),
            self._validate_field(self.people, criteria.people),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_name=data.get('restaurantName'),
            time=data.get('time'),
            selected_date=data.get('date'),
            people=data.get('people'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
        )


class CountrySelectedEvent(Event, BaseEventValidator):
    """User chooses a country in the reservation form."""

    event_name: str = "COUNTRY_SELECTED"
    country_code: str | None = None
    country_name: str | None = None
    restaurant_name: str | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None

    class ValidationCriteria(BaseModel):
        country_code: str | CriterionValue | None = None
        country_name: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.country_code, criteria.country_code),
            self._validate_field(self.country_name, criteria.country_name),
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CountrySelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            country_code=data.get('countryCode'),
            country_name=data.get('countryName'),
            restaurant_name=data.get('restaurantName'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
        )


class OccasionSelectedEvent(Event, BaseEventValidator):
    """User sets an occasion for the reservation."""

    event_name: str = "OCCASION_SELECTED"
    occasion: str | None = None
    restaurant_name: str | None = None
    desc: str | None = None
    rating: float | None = None
    reviews: int | None = None
    bookings: int | None = None
    cuisine: str | None = None

    class ValidationCriteria(BaseModel):
        occasion: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.occasion, criteria.occasion),
            self._validate_field(self.restaurant_name, criteria.restaurant_name),
            self._validate_field(self.desc, criteria.desc),
            self._validate_field(self.rating, criteria.rating),
            self._validate_field(self.reviews, criteria.reviews),
            self._validate_field(self.bookings, criteria.bookings),
            self._validate_field(self.cuisine, criteria.cuisine),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "OccasionSelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            occasion=data.get('occasion'),
            restaurant_name=data.get('restaurantName'),
            desc=data.get('desc'),
            rating=data.get('rating'),
            reviews=data.get('reviews'),
            bookings=data.get('bookings'),
            cuisine=data.get('cuisine'),
        )


class ReservationCompleteEvent(Event, BaseEventValidator):
    """Full reservation payload after submission."""

    event_name: str = "RESERVATION_COMPLETE"
    reservation_date_str: str | None = None
    reservation_time: str | None = None
    people_count: int | None = None
    country_code: str | None = None
    country_name: str | None = None
    phone_number: str | None = None
    occasion: str | None = None
    special_request: str | None = None

    class ValidationCriteria(BaseModel):
        reservation_date_str: str | CriterionValue | None = None
        reservation_time: str | CriterionValue | None = None
        people_count: int | CriterionValue | None = None
        country_code: str | CriterionValue | None = None
        country_name: str | CriterionValue | None = None
        phone_number: str | CriterionValue | None = None
        occasion: str | CriterionValue | None = None
        special_request: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.reservation_date_str, criteria.reservation_date_str),
            self._validate_field(self.reservation_time, criteria.reservation_time),
            self._validate_field(self.people_count, criteria.people_count),
            self._validate_field(self.country_code, criteria.country_code),
            self._validate_field(self.country_name, criteria.country_name),
            self._validate_field(self.phone_number, criteria.phone_number),
            self._validate_field(self.occasion, criteria.occasion),
            self._validate_field(self.special_request, criteria.special_request),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReservationCompleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            reservation_date_str=data.get('date'),
            reservation_time=data.get('time'),
            people_count=data.get('people'),
            country_code=data.get('countryCode'),
            country_name=data.get('countryName'),
            phone_number=data.get('phoneNumber'),
            occasion=data.get('occasion'),
            special_request=data.get('specialRequest'),
        )


class ScrollViewEvent(Event, BaseEventValidator):
    """Horizontal scroll interaction for restaurant carousels."""

    event_name: str = "SCROLL_VIEW"
    direction: str | None = None
    section_title: str | None = None

    class ValidationCriteria(BaseModel):
        direction: str | CriterionValue | None = None
        section_title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([
            self._validate_field(self.direction, criteria.direction),
            self._validate_field(self.section_title, criteria.section_title),
        ])

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ScrollViewEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            direction=data.get('direction'),
            section_title=data.get('sectionTitle'),
        )


EVENTS = [
    DateDropdownOpenedEvent,
    TimeDropdownOpenedEvent,
    PeopleDropdownOpenedEvent,
    SearchRestaurantEvent,
    ViewRestaurantEvent,
    ViewFullMenuEvent,
    CollapseMenuEvent,
    BookRestaurantEvent,
    CountrySelectedEvent,
    OccasionSelectedEvent,
    ReservationCompleteEvent,
    ScrollViewEvent
]
