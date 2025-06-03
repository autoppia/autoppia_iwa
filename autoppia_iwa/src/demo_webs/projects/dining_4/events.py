from datetime import UTC, date, datetime
from typing import Any

from dateutil.parser import isoparse
from loguru import logger
from pydantic import BaseModel

from ..base_events import BaseEventValidator, Event
from ..criterion_helper import CriterionValue
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

        criteria_utc = criteria_dt.astimezone(UTC)

        return self.selected_date.year == criteria_utc.year and self.selected_date.month == criteria_utc.month and self.selected_date.day == criteria_utc.day

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
    # restaurant_id: str
    restaurant_name: str
    time: str  # e.g., "1:30 PM"
    selected_date: date  # e.g., "2025-05-16"
    people: int

    class ValidationCriteria(BaseModel):
        # restaurant_id: str | CriterionValue | None = None
        restaurant_name: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        selected_date: date | CriterionValue | None = None
        people: int | CriterionValue | None = None

        class Config:
            title = "Book Restaurant Validation"
            description = "Validates a restaurant booking action."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.restaurant_name, criteria.restaurant_name),
                self._validate_field(self.time, criteria.time),
                self._validate_field(self.selected_date, criteria.selected_date),
                self._validate_field(self.people, criteria.people),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookRestaurantEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data

        parsed_date = None
        date_str = data.get("date")
        if date_str:
            try:
                parsed_date = date.fromisoformat(date_str)
            except ValueError:
                logger.warning(f"Could not parse date string for BookRestaurantEvent: {date_str}")

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # restaurant_id=data.get("restaurantId", ""),
            restaurant_name=data.get("restaurantName", ""),
            time=data.get("time", ""),
            selected_date=parsed_date,
            people=int(data.get("people", 0)),
        )


class CountrySelectedEvent(Event, BaseEventValidator):
    """Event triggered when a country is selected in a form."""

    event_name: str = "COUNTRY_SELECTED"
    country_code: str  # e.g., "IN"
    country_name: str  # e.g., "India"

    class ValidationCriteria(BaseModel):
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
    # restaurant_id: str
    reservation_date_str: str  # e.g., "Jul 18"
    reservation_time: str  # e.g., "1:30 PM"
    people_count: int
    country_code: str
    country_name: str
    phone_number: str
    occasion: str
    special_request: str | None = None
    # email: str

    class ValidationCriteria(BaseModel):
        # restaurant_id: str | CriterionValue | None = None
        reservation_date_str: str | CriterionValue | None = None
        reservation_time: str | CriterionValue | None = None
        people_count: int | CriterionValue | None = None
        # email: str | CriterionValue | None = None
        occasion: str | CriterionValue | None = None

        class Config:
            title = "Reservation Complete Validation"
            description = "Validates the completion of a reservation with key details."

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.restaurant_id, criteria.restaurant_id),
                self._validate_field(self.reservation_date_str, criteria.reservation_date_str),
                self._validate_field(self.reservation_time, criteria.reservation_time),
                self._validate_field(self.people_count, criteria.people_count),
                # self._validate_field(self.email, criteria.email),
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
            # restaurant_id=data.get("restaurantId", ""),
            reservation_date_str=parsed_date,
            reservation_time=data.get("time", ""),
            people_count=int(data.get("people", "")),
            country_code=data.get("countryCode", ""),
            country_name=data.get("countryName", ""),
            phone_number=data.get("phoneNumber", ""),
            occasion=data.get("occasion", ""),
            special_request=data.get("specialRequest"),
            # email=data.get("email", ""),
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
