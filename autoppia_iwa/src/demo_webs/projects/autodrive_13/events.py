from datetime import datetime, time

from dateutil import parser
from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

from ..shared_utils import validate_date_field


class EnterLocationEvent(Event, BaseEventValidator):
    """event triggered when someone enter location"""

    event_name: str = "ENTER_LOCATION"
    value: str

    class ValidationCriteria(BaseModel):
        value: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return all(
            [
                self._validate_field(self.value, criteria.value),
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
            value=data.get("value"),
        )


class EnterDestinationEvent(Event, BaseEventValidator):
    """event triggered when someone enter destination"""

    event_name: str = "ENTER_DESTINATION"
    value: str

    class ValidationCriteria(BaseModel):
        value: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.value, criteria.value),
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
            value=data.get("value"),
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
]

BACKEND_EVENT_TYPES = {
    "ENTER_LOCATION": EnterLocationEvent,
    "ENTER_DESTINATION": EnterDestinationEvent,
    "SEE_PRICES": SeePricesEvent,
    "NEXT_PICKUP": NextPickupEvent,
    "SELECT_TIME": SelectTimeEvent,
    "SELECT_DATE": SelectDateEvent,
}
