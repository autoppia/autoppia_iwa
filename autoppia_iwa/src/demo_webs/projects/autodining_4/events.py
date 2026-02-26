from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from dateutil.parser import isoparse
from loguru import logger
from pydantic import BaseModel, field_validator

from ..base_events import BaseEventValidator, Event
from ..criterion_helper import ComparisonOperator, CriterionValue
from ..shared_utils import parse_price


# Helper Pydantic Models for ViewFullMenuEvent
class MenuItem(BaseModel):
    name: str
    price: float | None = None

    @classmethod
    def parse_from_data(cls, data: dict[str, Any]) -> "MenuItem":
        return cls(name=data.get("name", ""), price=parse_price(data.get("price")))


class MenuCategory(BaseModel):
    category: str
    items: list[MenuItem]

    @classmethod
    def parse_from_data(cls, data: dict[str, Any]) -> "MenuCategory":
        items_data = data.get("items", [])
        return cls(category=data.get("category", ""), items=[MenuItem.parse_from_data(item_data) for item_data in items_data if isinstance(item_data, dict)])


class DateDropdownOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the date dropdown is opened."""

    event_name: str = "DATE_DROPDOWN_OPENED"
    date: datetime | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None

        class Config:
            title = "Date Dropdown Opened Validation"
            description = "Validates that the date dropdown was opened with a specific date."

    def _normalize_criteria_date(self, criteria_date: datetime | CriterionValue | None) -> date | None:
        """Normalize criteria date to date object."""
        if isinstance(criteria_date, CriterionValue):
            raw_value = criteria_date.value
            if isinstance(raw_value, str):
                return isoparse(raw_value).date()
            if isinstance(raw_value, datetime):
                return raw_value.date()
            if isinstance(raw_value, date):
                return raw_value
            return None
        if isinstance(criteria_date, datetime):
            return criteria_date.date()
        if isinstance(criteria_date, date):
            return criteria_date
        return None

    def _normalize_event_date(self) -> date | None:
        """Normalize event date to date object."""
        if isinstance(self.date, datetime):
            return self.date.date()
        if isinstance(self.date, date):
            return self.date
        return None

    def _compare_dates(self, event_date: date, criteria_dt: date, operator: ComparisonOperator) -> bool:
        """Compare dates based on operator."""
        if operator == ComparisonOperator.EQUALS:
            return event_date == criteria_dt
        if operator == ComparisonOperator.GREATER_THAN:
            return event_date > criteria_dt
        if operator == ComparisonOperator.LESS_THAN:
            return event_date < criteria_dt
        if operator == ComparisonOperator.GREATER_EQUAL:
            return event_date >= criteria_dt
        if operator == ComparisonOperator.LESS_EQUAL:
            return event_date <= criteria_dt
        return False

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria or not criteria.date:
            return True

        criteria_dt = self._normalize_criteria_date(criteria.date)
        if criteria_dt is None:
            return False

        event_date = self._normalize_event_date()
        if event_date is None:
            return False

        op = getattr(criteria.date, "operator", ComparisonOperator.EQUALS)
        return self._compare_dates(event_date, criteria_dt, op)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DateDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        selected_date_str = data.get("date")
        parsed_date = None
        if selected_date_str:
            parsed_date = isoparse(selected_date_str).date()

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parsed_date,
        )


class TimeDropdownOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the time dropdown is opened."""

    event_name: str = "TIME_DROPDOWN_OPENED"
    time: str

    class ValidationCriteria(BaseModel):
        time: str | CriterionValue | None = None

        class Config:
            title = "Time Dropdown Opened Validation"
            description = "Validates that the time dropdown was opened with a specific time."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.time, criteria.time)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "TimeDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            time=data.get("time", ""),
        )


class PeopleDropdownOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the people dropdown is opened."""

    event_name: str = "PEOPLE_DROPDOWN_OPENED"
    people: int

    class ValidationCriteria(BaseModel):
        people: int | CriterionValue | None = None

        class Config:
            title = "People Dropdown Opened Validation"
            description = "Validates that the people dropdown was opened with a specific count."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.people, criteria.people)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PeopleDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            people=int(data.get("people", 0)),
        )


class SearchRestaurantEvent(Event, BaseEventValidator):
    """Event triggered when a user searches for a restaurant."""

    event_name: str = "SEARCH_RESTAURANT"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

        class Config:
            title = "Search Restaurant Validation"
            description = "Validates that a restaurant search was performed with a specific query."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
        )


class ViewRestaurantEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant's details are viewed."""

    event_name: str = "VIEW_RESTAURANT"
    restaurant_id: str
    name: str
    desc: str
    rating: int
    reviews: int
    bookings: int
    cuisine: str

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

        class Config:
            title = "View Restaurant Validation"
            description = "Validates that a specific restaurant was viewed."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.desc, criteria.desc),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.bookings, criteria.bookings),
                self._validate_field(self.cuisine, criteria.cuisine),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get("restaurantId", ""),
            name=data.get("restaurantName", ""),
            desc=data.get("desc", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
        )


class ViewFullMenuEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant's full menu is viewed."""

    event_name: str = "VIEW_FULL_MENU"
    restaurant_id: str
    name: str
    desc: str
    rating: int
    reviews: int
    bookings: int
    cuisine: str
    action: str
    time: str  # e.g. "1:00 PM"
    date: date  # e.g. "2024-07-18"
    people: int
    menu: list[MenuCategory]

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        date: date | CriterionValue | None = None
        people: int | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

        class Config:
            title = "View Full Menu Validation"
            description = "Validates viewing of a full menu with specific details."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.action, criteria.action),
                self._validate_field(self.time, criteria.time),
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.people, criteria.people),
                self._validate_field(self.desc, criteria.desc),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.bookings, criteria.bookings),
                self._validate_field(self.cuisine, criteria.cuisine),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewFullMenuEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        menu_data = data.get("menu", [])

        parsed_date = None
        date_str = data.get("date")
        if date_str:
            try:
                parsed_date = date.fromisoformat(date_str)
            except ValueError:
                logger.warning(f"Could not parse date string: {date_str}")

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get("restaurantId", ""),
            name=data.get("restaurantName", ""),
            action=data.get("action", ""),
            time=data.get("time", ""),
            date=parsed_date,
            desc=data.get("desc", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
            people=int(data.get("people", 0)),
            menu=[MenuCategory.parse_from_data(cat_data) for cat_data in menu_data if isinstance(cat_data, dict)],
        )


class CollapseMenuEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant's menu is collapsed."""

    event_name: str = "COLLAPSE_MENU"
    restaurant_id: str
    name: str
    desc: str
    rating: int
    reviews: int
    bookings: int
    cuisine: str
    action: str
    time: str
    date: date  # e.g. "2024-07-18"
    people: int
    menu: list[MenuCategory]

    class ValidationCriteria(BaseModel):
        action: str | CriterionValue | None = None
        restaurant_id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        people: int | CriterionValue | None = None

        class Config:
            title = "Collapse Menu Validation"
            description = "Validates that a menu was collapsed."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.action, criteria.action),
                self._validate_field(self.desc, criteria.desc),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.reviews, criteria.reviews),
                self._validate_field(self.bookings, criteria.bookings),
                self._validate_field(self.cuisine, criteria.cuisine),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CollapseMenuEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        menu_data = data.get("menu", [])

        parsed_date = None
        date_str = data.get("date")
        if date_str:
            try:
                parsed_date = date.fromisoformat(date_str)
            except ValueError:
                logger.warning(f"Could not parse date string for CollapseMenuEvent: {date_str}")

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_id=data.get("restaurantId", ""),
            name=data.get("restaurantName", ""),
            action=data.get("action", ""),
            time=data.get("time", ""),
            date=parsed_date,
            desc=data.get("desc", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
            people=int(data.get("people", 0)),
            menu=[MenuCategory.parse_from_data(cat_data) for cat_data in menu_data if isinstance(cat_data, dict)],
        )


class BookRestaurantEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant booking is attempted or made (prior to completion details)."""

    event_name: str = "BOOK_RESTAURANT"
    name: str
    desc: str
    rating: int
    reviews: int
    bookings: int
    cuisine: str
    time: str  # e.g. "1:30 PM"
    date: date  # e.g. Date(2025, 5, 16)
    people: int

    # --------------------------- ValidationCriteria ---------------------------

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        date: date | CriterionValue | None = None
        people: int | CriterionValue | None = None

        # ── coerción de datetime ISO-8601 (con hora) a date ──
        @field_validator("date", mode="before")
        @classmethod
        def coerce_datetime_to_date(cls, v):
            if isinstance(v, str) and "T" in v:
                return datetime.fromisoformat(v).date()
            return v

        class Config:
            title = "Book Restaurant Validation"
            description = "Validates a restaurant booking action."

    # ----------------------- instancia: validación ---------------------------

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Return True if this event matches the provided criteria object."""
        if not criteria:
            return True

        # tabla de comparación para fechas
        comp_table: dict[str, Callable[[date, date], bool]] = {
            ComparisonOperator.EQUALS: lambda s, c: s == c,
            ComparisonOperator.NOT_EQUALS: lambda s, c: s != c,
            ComparisonOperator.GREATER_THAN: lambda s, c: s > c,
            ComparisonOperator.GREATER_EQUAL: lambda s, c: s >= c,
            ComparisonOperator.LESS_THAN: lambda s, c: s < c,
            ComparisonOperator.LESS_EQUAL: lambda s, c: s <= c,
        }

        # --- date --
        if isinstance(criteria.date, CriterionValue):
            op = criteria.date.operator
            comp_date = criteria.date.value
            if isinstance(comp_date, str):
                comp_date = datetime.fromisoformat(comp_date).date() if "T" in comp_date else date.fromisoformat(comp_date)

            try:
                date_valid = comp_table[op](self.date, comp_date)
            except KeyError:
                logger.error("Unknown comparison operator for date: %s", op)
                date_valid = False
        else:
            date_valid = criteria.date is None or self._validate_field(self.date, criteria.date)
        result = all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.desc, criteria.desc),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.reviews, criteria.reviews),
                self._validate_field(self.bookings, criteria.bookings),
                self._validate_field(self.cuisine, criteria.cuisine),
                self._validate_field(self.time, criteria.time),
                date_valid,
                self._validate_field(self.people, criteria.people),
            ]
        )

        if not result:
            print("AY")
        return result

    # ----------------------- clase: parseo desde backend ---------------------

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookRestaurantEvent":
        """Build a BookRestaurantEvent from a raw BackendEvent dict."""
        base_event = Event.parse(backend_event)
        data = backend_event.data

        date_str: str | None = data.get("date")
        parsed_date: date | None = None
        if date_str:
            try:
                parsed_date = datetime.fromisoformat(date_str).date()
            except ValueError:
                logger.warning("Could not parse date string '%s' for BookRestaurantEvent", date_str, exc_info=True)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("restaurantName", ""),
            time=data.get("time", ""),
            date=parsed_date,
            people=int(data.get("people", 0)),
            desc=data.get("desc", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
        )


class CountrySelectedEvent(Event, BaseEventValidator):
    """Event triggered when a country is selected in a form."""

    event_name: str = "COUNTRY_SELECTED"
    name: str
    code: str  # e.g., "IN"
    country: str  # e.g., "India"
    desc: str
    rating: int
    reviews: int
    bookings: int
    cuisine: str

    class ValidationCriteria(BaseModel):
        code: str | CriterionValue | None = None
        country: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

        class Config:
            title = "Country Selected Validation"
            description = "Validates that a country was selected."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.code, criteria.code),
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.desc, criteria.desc),
                self._validate_field(self.reviews, criteria.reviews),
                self._validate_field(self.bookings, criteria.bookings),
                self._validate_field(self.cuisine, criteria.cuisine),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CountrySelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            code=data.get("countryCode", ""),
            country=data.get("countryName", ""),
            name=data.get("restaurantName", ""),
            desc=data.get("desc", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
        )


class OccasionSelectedEvent(Event, BaseEventValidator):
    """Event triggered when an occasion is selected for a reservation."""

    event_name: str = "OCCASION_SELECTED"
    occasion: str  # e.g., "birthday"
    name: str
    desc: str | CriterionValue | None = None
    rating: int | CriterionValue | None = None
    reviews: int | CriterionValue | None = None
    bookings: int | CriterionValue | None = None
    cuisine: str | CriterionValue | None = None

    class ValidationCriteria(BaseModel):
        occasion: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        desc: str | CriterionValue | None = None
        rating: int | CriterionValue | None = None
        reviews: int | CriterionValue | None = None
        bookings: int | CriterionValue | None = None
        cuisine: str | CriterionValue | None = None

        class Config:
            title = "Occasion Selected Validation"
            description = "Validates that an occasion was selected."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.occasion, criteria.occasion)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "OccasionSelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            occasion=data.get("occasion", ""),
            desc=data.get("desc", ""),
            name=data.get("restaurantName", ""),
            rating=data.get("rating", 0),
            cuisine=data.get("cuisine", ""),
            reviews=data.get("reviews", 0),
            bookings=data.get("bookings", 0),
        )


class ReservationCompleteEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant reservation is completed."""

    event_name: str = "RESERVATION_COMPLETE"
    reservation: str  # e.g., "Jul 18"
    time: str  # e.g., "1:30 PM"
    people: int
    code: str
    country: str
    phone: str
    occasion: str
    request: str | None = None

    class ValidationCriteria(BaseModel):
        reservation: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        people: int | CriterionValue | None = None
        occasion: str | CriterionValue | None = None
        phone: str | CriterionValue | None = None
        country: str | CriterionValue | None = None
        code: str | CriterionValue | None = None
        request: str | None = None

        class Config:
            title = "Reservation Complete Validation"
            description = "Validates the completion of a reservation with key details."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.reservation, criteria.reservation),
                self._validate_field(self.time, criteria.time),
                self._validate_field(self.people, criteria.people),
                self._validate_field(self.occasion, criteria.occasion),
                self._validate_field(self.request, criteria.request),
                self._validate_field(self.country, criteria.country),
                self._validate_field(self.code, criteria.code),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ReservationCompleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        parsed_date = data.get("date", "")
        last_element = parsed_date.split(" ")[-1]
        if len(last_element) == 1:
            parsed_date = parsed_date.replace(last_element, "0" + last_element)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            reservation=parsed_date,
            time=data.get("time", ""),
            people=int(data.get("people", "")),
            code=data.get("countryCode", ""),
            country=data.get("countryName", ""),
            phone=data.get("phoneNumber", ""),
            occasion=data.get("occasion", ""),
            request=data.get("specialRequest"),
        )


class ScrollViewEvent(Event, BaseEventValidator):
    """Event triggered when a generic view is scrolled."""

    event_name: str = "SCROLL_VIEW"
    direction: str  # "right" or "left", etc.
    section: str

    class ValidationCriteria(BaseModel):
        direction: str | CriterionValue | None = None
        section: str | CriterionValue | None = None

        class Config:
            title = "Scroll View Validation"
            description = "Validates a scroll action on a view."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.direction, criteria.direction),
                self._validate_field(self.section, criteria.section),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ScrollViewEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            direction=data.get("direction", "").lower(),
            section=data.get("sectionTitle", ""),
        )


class AboutPageViewEvent(Event, BaseEventValidator):
    """Event triggered when a help page is viewed."""

    event_name: str = "ABOUT_PAGE_VIEW"


class AboutFeatureClickEvent(Event, BaseEventValidator):
    """Event triggered when a user clicks an about/feature highlight."""

    event_name: str = "ABOUT_FEATURE_CLICK"
    feature: str | None = None

    class ValidationCriteria(BaseModel):
        feature: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.feature, criteria.feature)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AboutFeatureClickEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            feature=data.get("feature", ""),
        )


class HelpPageViewEvent(Event, BaseEventValidator):
    """Event triggered when a help page is viewed."""

    event_name: str = "HELP_PAGE_VIEW"


class HelpCategorySelectedEvent(Event, BaseEventValidator):
    """Event triggered when a help category is selected."""

    event_name: str = "HELP_CATEGORY_SELECTED"
    category: str | None = None

    class ValidationCriteria(BaseModel):
        category: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.category, criteria.category)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HelpCategorySelectedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            category=data.get("category", ""),
        )


class HelpFaqToggledEvent(Event, BaseEventValidator):
    """Event triggered when a FAQ item is expanded/collapsed."""

    event_name: str = "HELP_FAQ_TOGGLED"
    question: str | None = None

    class ValidationCriteria(BaseModel):
        question: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.question, criteria.question)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "HelpFaqToggledEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            question=data.get("question", ""),
        )


class ContactEvent(Event, BaseEventValidator):
    """Event triggered when a user submit a contact form."""

    event_name: str = "CONTACT_FORM_SUBMIT"

    email: str
    message: str
    username: str
    subject: str

    class ValidationCriteria(BaseModel):
        email: str | CriterionValue | None = None
        message: str | CriterionValue | None = None
        username: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.email, criteria.email),
                self._validate_field(self.message, criteria.message),
                self._validate_field(self.username, criteria.username),
                self._validate_field(self.subject, criteria.subject),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ContactEvent":
        base_event = Event.parse(backend_event)
        event_data = backend_event.data
        form_data = event_data.get("data", {})
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            message=form_data.get("message", ""),
            username=form_data.get("name", ""),
            email=form_data.get("email", ""),
            subject=form_data.get("subject", ""),
        )


class ContactPageViewEvent(Event, BaseEventValidator):
    """Event triggered when a user views the contact page."""

    event_name: str = "CONTACT_PAGE_VIEW"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ContactPageViewEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
        )


class ContactCardClickEvent(Event, BaseEventValidator):
    """Event triggered when a specific contact card is clicked (email/phone/chat)."""

    event_name: str = "CONTACT_CARD_CLICK"
    card_type: str | None = None

    class ValidationCriteria(BaseModel):
        card_type: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.card_type, criteria.card_type)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ContactCardClickEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            card_type=data.get("card_type", ""),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES (UPDATED)
# =============================================================================

EVENTS = [
    DateDropdownOpenedEvent,
    TimeDropdownOpenedEvent,
    PeopleDropdownOpenedEvent,
    SearchRestaurantEvent,  # Restaurant search
    ViewRestaurantEvent,
    ViewFullMenuEvent,
    CollapseMenuEvent,
    BookRestaurantEvent,
    CountrySelectedEvent,
    OccasionSelectedEvent,
    ReservationCompleteEvent,  # Restaurant reservation
    ScrollViewEvent,  # Generic scroll
    AboutPageViewEvent,
    AboutFeatureClickEvent,
    ContactPageViewEvent,
    ContactCardClickEvent,
    HelpPageViewEvent,
    HelpCategorySelectedEvent,
    HelpFaqToggledEvent,
    ContactEvent,
]

BACKEND_EVENT_TYPES = {
    "DATE_DROPDOWN_OPENED": DateDropdownOpenedEvent,
    "TIME_DROPDOWN_OPENED": TimeDropdownOpenedEvent,
    "PEOPLE_DROPDOWN_OPENED": PeopleDropdownOpenedEvent,
    "SEARCH_RESTAURANT": SearchRestaurantEvent,
    "VIEW_RESTAURANT": ViewRestaurantEvent,
    "VIEW_FULL_MENU": ViewFullMenuEvent,
    "COLLAPSE_MENU": CollapseMenuEvent,
    "BOOK_RESTAURANT": BookRestaurantEvent,
    "COUNTRY_SELECTED": CountrySelectedEvent,
    "OCCASION_SELECTED": OccasionSelectedEvent,
    "RESERVATION_COMPLETE": ReservationCompleteEvent,
    "SCROLL_VIEW": ScrollViewEvent,
    "ABOUT_PAGE_VIEW": AboutPageViewEvent,
    "ABOUT_FEATURE_CLICK": AboutFeatureClickEvent,
    "CONTACT_PAGE_VIEW": ContactPageViewEvent,
    "CONTACT_CARD_CLICK": ContactCardClickEvent,
    "HELP_PAGE_VIEW": HelpPageViewEvent,
    "HELP_CATEGORY_SELECTED": HelpCategorySelectedEvent,
    "HELP_FAQ_TOGGLED": HelpFaqToggledEvent,
    "CONTACT_FORM_SUBMIT": ContactEvent,
}
