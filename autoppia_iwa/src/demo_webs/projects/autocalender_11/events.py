from datetime import datetime

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import parse_datetime, validate_date_field


class SelectViewEvent(Event, BaseEventValidator):
    """Base event for selecting different calendar views"""

    event_name: str
    # source: str
    # selected_view: str

    class ValidationCriteria(BaseModel):
        # source: str | CriterionValue | None = None
        # selectedView: str | CriterionValue | None = None
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.source, criteria.source),
                # self._validate_field(self.selected_view, criteria.selectedView),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectViewEvent":
        base_event = Event.parse(backend_event)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # source=data.get("source", ""),
            # selected_view=data.get("selectedView", ""),
        )


class SelectMonthEvent(SelectViewEvent):
    """Event triggered when user selects month view"""

    event_name: str = "SELECT_MONTH"


class SelectWeekEvent(SelectViewEvent):
    """Event triggered when user selects week view"""

    event_name: str = "SELECT_WEEK"


class SelectFiveDaysEvent(SelectViewEvent):
    """Event triggered when user selects 5-day view"""

    event_name: str = "SELECT_FIVE_DAYS"


class SelectDayEvent(SelectViewEvent):
    """Event triggered when user selects day view"""

    event_name: str = "SELECT_DAY"


class SelectTodayEvent(Event, BaseEventValidator):
    """Event triggered when user clicks on today"""

    event_name: str = "SELECT_TODAY"
    # source: str
    # selected_date: datetime | None = None

    class ValidationCriteria(BaseModel):
        # source: str | CriterionValue | None = None
        # selectedDate: datetime | CriterionValue | None = None
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        # date_valid = validate_date_field(self.selected_date, criteria.selectedDate)
        return all(
            [
                # self._validate_field(self.source, criteria.source),
                # date_valid,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectTodayEvent":
        base_event = Event.parse(backend_event)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # source=data.get("source", ""),
            # selected_date=parse_datetime(data.get("selectedDate")),
        )


class AddNewCalendarEvent(Event, BaseEventValidator):
    """Event triggered when user opens add calendar modal"""

    event_name: str = "ADD_NEW_CALENDAR"
    # source: str
    # action: str

    class ValidationCriteria(BaseModel):
        # source: str | CriterionValue | None = None
        # action: str | CriterionValue | None = None
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.source, criteria.source),
                # self._validate_field(self.action, criteria.action),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddNewCalendarEvent":
        base_event = Event.parse(backend_event)

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # source=data.get("source", ""),
            # action=data.get("action", ""),
        )


class CreateCalendarEvent(Event, BaseEventValidator):
    """Event triggered when user creates a new calendar"""

    event_name: str = "CREATE_CALENDAR"
    name: str
    description: str
    # color: str

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        # color: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.description, criteria.description),
                # self._validate_field(self.color, criteria.color),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CreateCalendarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            # color=data.get("color", ""),
        )


class ChooseCalendarEvent(Event, BaseEventValidator):
    """Event triggered when user selects or deselects a calendar"""

    event_name: str = "CHOOSE_CALENDAR"
    calendar_name: str
    selected: bool
    # color: str

    class ValidationCriteria(BaseModel):
        calendar_name: str | CriterionValue | None = None
        selected: bool | CriterionValue | None = None
        # color: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.calendar_name, criteria.calendar_name),
                self._validate_field(self.selected, criteria.selected),
                # self._validate_field(self.color, criteria.color),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ChooseCalendarEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            calendar_name=data.get("calendarName", ""),
            selected=data.get("selected", False),
            # color=data.get("color", ""),
        )


class AddEventEvent(Event, BaseEventValidator):
    """Event triggered when user adds a calendar event"""

    event_name: str = "ADD_EVENT"
    # source: str
    title: str
    calendar: str
    date: str
    start_time: str
    end_time: str
    # color: str
    # is_editing: bool

    class ValidationCriteria(BaseModel):
        # source: str | CriterionValue | None = None
        title: str | CriterionValue | None = None
        calendar: str | CriterionValue | None = None
        date: str | CriterionValue | None = None
        start_time: str | CriterionValue | None = None
        end_time: str | CriterionValue | None = None
        # color: str | CriterionValue | None = None
        # isEditing: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.source, criteria.source),
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.calendar, criteria.calendar),
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.start_time, criteria.start_time),
                self._validate_field(self.end_time, criteria.end_time),
                # self._validate_field(self.color, criteria.color),
                # self._validate_field(self.is_editing, criteria.isEditing),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddEventEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        start_time, end_time = "", ""
        st = data.get("startTime", [])
        if st:
            start_time = st[0] + ":" + st[1]
        et = data.get("endTime", [])
        if et:
            end_time = et[0] + ":" + et[1]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # source=data.get("source", ""),
            title=data.get("title", ""),
            calendar=data.get("calendar", ""),
            date=data.get("date", ""),
            start_time=start_time,
            end_time=end_time,
            # color=data.get("color", ""),
            # is_editing=data.get("isEditing", False),
        )


class CellClickedEvent(Event, BaseEventValidator):
    """Event triggered when user clicks on a calendar cell"""

    event_name: str = "CELL_CLCIKED"
    source: str
    date: datetime | None = None
    hour: int | None = None
    view: str

    class ValidationCriteria(BaseModel):
        source: str | CriterionValue | None = None
        date: datetime | CriterionValue | None = None
        hour: int | CriterionValue | None = None
        view: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.date, criteria.date)
        return all(
            [
                self._validate_field(self.source, criteria.source),
                date_valid,
                self._validate_field(self.hour, criteria.hour) if self.hour is not None else True,
                self._validate_field(self.view, criteria.view),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CellClickedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            source=data.get("source", ""),
            date=parse_datetime(data.get("date")),
            hour=data.get("hour"),
            view=data.get("view", ""),
        )


class CancelAddEventEvent(Event, BaseEventValidator):
    """Event triggered when user cancels adding an event"""

    event_name: str = "CANCEL_ADD_EVENT"
    source: str
    date: str
    # reason: str
    title: str

    class ValidationCriteria(BaseModel):
        source: str | CriterionValue | None = None
        date: str | CriterionValue | None = None
        # reason: str | CriterionValue | None = None
        title: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.source, criteria.source),
                self._validate_field(self.date, criteria.date),
                # self._validate_field(self.reason, criteria.reason),
                self._validate_field(self.title, criteria.title),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CancelAddEventEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            source=data.get("source", ""),
            date=data.get("date", ""),
            # reason=data.get("reason", ""),
            title=data.get("title", ""),
        )


class DeleteAddedEventEvent(Event, BaseEventValidator):
    """Event triggered when user deletes an existing calendar event"""

    event_name: str = "DELETE_ADDED_EVENT"
    source: str
    # event_id: str
    event_title: str
    calendar: str
    date: str

    class ValidationCriteria(BaseModel):
        source: str | CriterionValue | None = None
        # eventId: str | CriterionValue | None = None
        eventTitle: str | CriterionValue | None = None
        calendar: str | CriterionValue | None = None
        date: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.source, criteria.source),
                # self._validate_field(self.event_id, criteria.eventId),
                self._validate_field(self.event_title, criteria.eventTitle),
                self._validate_field(self.calendar, criteria.calendar),
                self._validate_field(self.date, criteria.date),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteAddedEventEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            source=data.get("source", ""),
            # event_id=data.get("eventId", ""),
            event_title=data.get("eventTitle", ""),
            calendar=data.get("calendar", ""),
            date=data.get("date", ""),
        )


CALENDAR_EVENTS = [
    SelectMonthEvent,
    SelectWeekEvent,
    SelectFiveDaysEvent,
    SelectDayEvent,
    SelectTodayEvent,
    AddNewCalendarEvent,
    CreateCalendarEvent,
    ChooseCalendarEvent,
    AddEventEvent,
    CellClickedEvent,
    CancelAddEventEvent,
    DeleteAddedEventEvent,
]

CALENDAR_BACKEND_EVENT_TYPES = {
    "SELECT_MONTH": SelectMonthEvent,
    "SELECT_WEEK": SelectWeekEvent,
    "SELECT_FIVE_DAYS": SelectFiveDaysEvent,
    "SELECT_DAY": SelectDayEvent,
    "SELECT_TODAY": SelectTodayEvent,
    "ADD_NEW_CALENDAR": AddNewCalendarEvent,
    "CREATE_CALENDAR": CreateCalendarEvent,
    "CHOOSE_CALENDAR": ChooseCalendarEvent,
    "ADD_EVENT": AddEventEvent,
    "CELL_CLCIKED": CellClickedEvent,
    "CANCEL_ADD_EVENT": CancelAddEventEvent,
    "DELETE_ADDED_EVENT": DeleteAddedEventEvent,
}
