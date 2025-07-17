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
    selected_date: datetime

    class ValidationCriteria(BaseModel):
        selected_date: datetime | CriterionValue | None = None

        class Config:
            title = "Date Dropdown Opened Validation"
            description = "Validates that the date dropdown was opened with a specific date."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria or not criteria.selected_date:
            return True

        # Normalize selected_date to datetime if CriterionValue
        if isinstance(criteria.selected_date, CriterionValue):
            raw_value = criteria.selected_date.value
            if isinstance(raw_value, str):
                criteria_dt = isoparse(raw_value)
            elif isinstance(raw_value, datetime):
                criteria_dt = raw_value
            else:
                return False
        elif isinstance(criteria.selected_date, datetime):
            criteria_dt = criteria.selected_date
        else:
            return False

        event_dt = self.selected_date

        # --- ONLYAAAA-MM-DD -------------------------------------
        event_date = event_dt.date() if isinstance(event_dt, datetime) else event_dt
        criteria_date = criteria_dt.date() if isinstance(criteria_dt, datetime) else criteria_dt

        # --- Operador -------------------------------------------------------------
        op = getattr(criteria.selected_date, "operator", ComparisonOperator.EQUALS)

        if op == ComparisonOperator.EQUALS:
            return event_date == criteria_date
        elif op == ComparisonOperator.GREATER_THAN:
            return event_date > criteria_date
        elif op == ComparisonOperator.LESS_THAN:
            return event_date < criteria_date
        elif op == ComparisonOperator.GREATER_EQUAL:
            return event_date >= criteria_date
        elif op == ComparisonOperator.LESS_EQUAL:
            return event_date <= criteria_date
        else:
            return False

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DateDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        selected_date_str = backend_event.data.get("date")

        parsed_date = isoparse(selected_date_str) if selected_date_str else None

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            selected_date=parsed_date,
        )


class TimeDropdownOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the time dropdown is opened."""

    event_name: str = "TIME_DROPDOWN_OPENED"
    selected_time: str

    class ValidationCriteria(BaseModel):
        selected_time: str | CriterionValue | None = None

        class Config:
            title = "Time Dropdown Opened Validation"
            description = "Validates that the time dropdown was opened with a specific time."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.selected_time, criteria.selected_time)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "TimeDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            selected_time=data.get("time", ""),
        )


class PeopleDropdownOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the people dropdown is opened."""

    event_name: str = "PEOPLE_DROPDOWN_OPENED"
    people_count: int

    class ValidationCriteria(BaseModel):
        people_count: int | CriterionValue | None = None

        class Config:
            title = "People Dropdown Opened Validation"
            description = "Validates that the people dropdown was opened with a specific count."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.people_count, criteria.people_count)

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "PeopleDropdownOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            people_count=int(data.get("people", 0)),
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
    restaurant_name: str

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None

        class Config:
            title = "View Restaurant Validation"
            description = "Validates that a specific restaurant was viewed."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.restaurant_name, criteria.restaurant_name),
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
            restaurant_name=data.get("restaurantName", ""),
        )


class ViewFullMenuEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant's full menu is viewed."""

    event_name: str = "VIEW_FULL_MENU"
    restaurant_id: str
    restaurant_name: str
    action: str
    time: str  # e.g. "1:00 PM"
    selected_date: date  # e.g. "2024-07-18"
    people: int
    menu: list[MenuCategory]

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: date | CriterionValue | None = None
        people: int | CriterionValue | None = None

        class Config:
            title = "View Full Menu Validation"
            description = "Validates viewing of a full menu with specific details."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.restaurant_name, criteria.restaurant_name),
                self._validate_field(self.action, criteria.action),
                self._validate_field(self.time, criteria.time),
                self._validate_field(self.selected_date, criteria.selected_date),
                self._validate_field(self.people, criteria.people),
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
            restaurant_name=data.get("restaurantName", ""),
            action=data.get("action", ""),
            time=data.get("time", ""),
            selected_date=parsed_date,
            people=int(data.get("people", 0)),
            menu=[MenuCategory.parse_from_data(cat_data) for cat_data in menu_data if isinstance(cat_data, dict)],
        )


class CollapseMenuEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant's menu is collapsed."""

    event_name: str = "COLLAPSE_MENU"
    restaurant_id: str
    restaurant_name: str
    action: str
    time: str
    selected_date: date  # e.g. "2024-07-18"
    people: int
    menu: list[MenuCategory]

    class ValidationCriteria(BaseModel):
        restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None

        class Config:
            title = "Collapse Menu Validation"
            description = "Validates that a menu was collapsed."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.restaurant_name, criteria.restaurant_name),
                self._validate_field(self.action, criteria.action),
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
            restaurant_name=data.get("restaurantName", ""),
            action=data.get("action", ""),
            time=data.get("time", ""),
            selected_date=parsed_date,
            people=int(data.get("people", 0)),
            menu=[MenuCategory.parse_from_data(cat_data) for cat_data in menu_data if isinstance(cat_data, dict)],
        )


class BookRestaurantEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant booking is attempted or made (prior to completion details)."""

    event_name: str = "BOOK_RESTAURANT"
    restaurant_name: str
    time: str  # e.g. "1:30 PM"
    selected_date: date  # e.g. Date(2025, 5, 16)
    people: int

    # --------------------------- ValidationCriteria ---------------------------

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: date | CriterionValue | None = None
        people: int | CriterionValue | None = None

        # ── coerción de datetime ISO-8601 (con hora) a date ──
        @field_validator("selected_date", mode="before")
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
            ComparisonOperator.GREATER_THAN: lambda s, c: s >= c,
            ComparisonOperator.GREATER_EQUAL: lambda s, c: s >= c,
            ComparisonOperator.LESS_THAN: lambda s, c: s <= c,
            ComparisonOperator.LESS_EQUAL: lambda s, c: s <= c,
        }

        # --- selected_date ---
        if isinstance(criteria.selected_date, CriterionValue):
            op = criteria.selected_date.operator
            comp_date = criteria.selected_date.value
            if isinstance(comp_date, str):
                comp_date = datetime.fromisoformat(comp_date).date() if "T" in comp_date else date.fromisoformat(comp_date)

            try:
                selected_date_valid = comp_table[op](self.selected_date, comp_date)
            except KeyError:
                logger.error("Unknown comparison operator for selected_date: %s", op)
                selected_date_valid = False
        else:
            selected_date_valid = criteria.selected_date is None or self._validate_field(self.selected_date, criteria.selected_date)

        return all(
            [
                criteria.name is None or self._validate_field(self.restaurant_name, criteria.name),
                criteria.time is None or self._validate_field(self.time, criteria.time),
                selected_date_valid,
                criteria.people is None or self._validate_field(self.people, criteria.people),
            ]
        )

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
                # admite tanto "YYYY-MM-DD" como "YYYY-MM-DDTHH:MM:SSZ"
                parsed_date = datetime.fromisoformat(date_str).date() if "T" in date_str else date.fromisoformat(date_str)
            except ValueError:
                logger.warning("Could not parse date string '%s' for BookRestaurantEvent", date_str, exc_info=True)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            restaurant_name=data.get("restaurantName", ""),
            time=data.get("time", ""),
            selected_date=parsed_date,
            people=int(data.get("people", 0)),
        )


class CountrySelectedEvent(Event, BaseEventValidator):
    """Event triggered when a country is selected in a form."""

    event_name: str = "COUNTRY_SELECTED"
    restaurant_name: str
    country_code: str  # e.g., "IN"
    country_name: str  # e.g., "India"

    class ValidationCriteria(BaseModel):
        restaurant_name: str | CriterionValue | None = None
        country_code: str | CriterionValue | None = None
        country_name: str | CriterionValue | None = None

        class Config:
            title = "Country Selected Validation"
            description = "Validates that a country was selected."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.restaurant_name, criteria.restaurant_name),
                self._validate_field(self.country_code, criteria.country_code),
                self._validate_field(self.country_name, criteria.country_name),
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
            country_code=data.get("countryCode", ""),
            country_name=data.get("countryName", ""),
            restaurant_name=data.get("restaurantName", ""),
        )


class OccasionSelectedEvent(Event, BaseEventValidator):
    """Event triggered when an occasion is selected for a reservation."""

    event_name: str = "OCCASION_SELECTED"
    occasion: str  # e.g., "birthday"

    class ValidationCriteria(BaseModel):
        occasion: str | CriterionValue | None = None

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
        )


class ReservationCompleteEvent(Event, BaseEventValidator):
    """Event triggered when a restaurant reservation is completed."""

    event_name: str = "RESERVATION_COMPLETE"
    reservation_date_str: str  # e.g., "Jul 18"
    reservation_time: str  # e.g., "1:30 PM"
    people_count: int
    country_code: str
    country_name: str
    phone_number: str
    occasion: str
    special_request: str | None = None

    class ValidationCriteria(BaseModel):
        reservation_date_str: str | CriterionValue | None = None
        reservation_time: str | CriterionValue | None = None
        people_count: int | CriterionValue | None = None
        occasion: str | CriterionValue | None = None
        phone_number: str | CriterionValue | None = None

        class Config:
            title = "Reservation Complete Validation"
            description = "Validates the completion of a reservation with key details."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.reservation_date_str, criteria.reservation_date_str),
                self._validate_field(self.reservation_time, criteria.reservation_time),
                self._validate_field(self.people_count, criteria.people_count),
                self._validate_field(self.occasion, criteria.occasion),
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
            reservation_date_str=parsed_date,
            reservation_time=data.get("time", ""),
            people_count=int(data.get("people", "")),
            country_code=data.get("countryCode", ""),
            country_name=data.get("countryName", ""),
            phone_number=data.get("phoneNumber", ""),
            occasion=data.get("occasion", ""),
            special_request=data.get("specialRequest"),
        )


class ScrollViewEvent(Event, BaseEventValidator):
    """Event triggered when a generic view is scrolled."""

    event_name: str = "SCROLL_VIEW"
    direction: str  # "right" or "left", etc.
    section_title: str

    class ValidationCriteria(BaseModel):
        direction: str | CriterionValue | None = None
        section_title: str | CriterionValue | None = None

        class Config:
            title = "Scroll View Validation"
            description = "Validates a scroll action on a view."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.direction, criteria.direction),
                self._validate_field(self.section_title, criteria.section_title),
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
            section_title=data.get("sectionTitle", ""),
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
}
