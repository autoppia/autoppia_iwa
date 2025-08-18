from datetime import datetime, time

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


class CellClickedEvent(Event, BaseEventValidator):
    """Event triggered when user clicks on a calendar cell"""

    event_name: str = "CELL_CLICKED"
    # source: str
    date: datetime | None = None
    hour: int | None = None
    view: str

    class ValidationCriteria(BaseModel):
        # source: str | CriterionValue | None = None
        date: datetime | CriterionValue | None = None
        hour: int | CriterionValue | None = None
        view: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.date, criteria.date)
        return all(
            [
                # self._validate_field(self.source, criteria.source),
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
            # source=data.get("source", ""),
            date=parse_datetime(data.get("date")),
            hour=data.get("hour"),
            view=data.get("view", ""),
        )


class AddEventEvent(Event, BaseEventValidator):
    """Event triggered when user adds a calendar event"""

    event_name: str = "ADD_EVENT"
    title: str
    calendar: str
    date: str
    start_time: time
    end_time: time
    all_day: bool
    recurrence: str
    attendees: list[str]
    reminders: list[int]
    busy: bool
    visibility: str
    location: str
    description: str
    meeting_link: str

    class ValidationCriteria(BaseModel):
        title: str | CriterionValue | None = None
        calendar: str | CriterionValue | None = None
        date: str | CriterionValue | None = None
        start_time: time | CriterionValue | None = None
        end_time: time | CriterionValue | None = None
        all_day: bool | CriterionValue | None = None
        recurrence: str | CriterionValue | None = None
        attendees: str | CriterionValue | None = None
        reminders: int | CriterionValue | None = None
        busy: bool | CriterionValue | None = None
        visibility: str | CriterionValue | None = None
        location: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        meeting_link: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.title, criteria.title),
                self._validate_field(self.calendar, criteria.calendar),
                validate_date_field(self.date, criteria.date),
                self._validate_field(self.start_time, criteria.start_time),
                self._validate_field(self.end_time, criteria.end_time),
                self._validate_field(self.all_day, criteria.all_day),
                self._validate_field(self.recurrence, criteria.recurrence),
                any([at for at in self.attendees if self._validate_field(at, criteria.attendees)]),
                any([rem for rem in self.reminders if self._validate_field(rem, criteria.reminders)]),
                # self._validate_field(self.attendees, criteria.attendees),
                # self._validate_field(self.reminders, criteria.reminders),
                self._validate_field(self.busy, criteria.busy),
                self._validate_field(self.visibility, criteria.visibility),
                self._validate_field(self.location, criteria.location),
                self._validate_field(self.description, criteria.description),
                self._validate_field(self.meeting_link, criteria.meeting_link),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddEventEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        start_time, end_time = "", ""
        st = data.get("startTime", [])
        if st:
            time_str = str(st[0]) + ":" + str(st[1]).zfill(2)
            start_time = datetime.strptime(time_str, "%H:%M").time()
        et = data.get("endTime", [])
        if et:
            time_str = str(et[0]) + ":" + str(et[1]).zfill(2)
            end_time = datetime.strptime(time_str, "%H:%M").time()

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            title=data.get("title", ""),
            calendar=data.get("calendar", ""),
            date=data.get("date", ""),
            start_time=start_time,
            end_time=end_time,
            all_day=data.get("allDay", False),
            recurrence=data.get("recurrence", ""),
            attendees=data.get("attendees", []),
            reminders=data.get("reminders", []),
            busy=data.get("busy", False),
            visibility=data.get("visibility", ""),
            location=data.get("location", ""),
            description=data.get("description", ""),
            meeting_link=data.get("meetingLink", ""),
        )


class EventWizardOpenEvent(AddEventEvent):
    """Event triggered when the event creation/editing wizard is opened."""

    event_name: str = "EVENT_WIZARD_OPEN"


class CancelAddEventEvent(AddEventEvent):
    """Event triggered when user cancels adding an event"""

    event_name: str = "CANCEL_ADD_EVENT"


class DeleteAddedEventEvent(AddEventEvent):
    """Event triggered when user deletes an existing calendar event"""

    event_name: str = "DELETE_ADDED_EVENT"


class SearchSubmitEvent(Event, BaseEventValidator):
    """Event triggered when user submits a search query"""

    event_name: str = "SEARCH_SUBMIT"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchSubmitEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=data.get("query", ""),
        )


class EventAddReminderEvent(Event, BaseEventValidator):
    """Event triggered when a reminder is added to an event"""

    event_name: str = "EVENT_ADD_REMINDER"
    minutes: int

    class ValidationCriteria(BaseModel):
        minutes: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return self._validate_field(self.minutes, criteria.minutes)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EventAddReminderEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            minutes=data.get("minutes", 0),
        )


class EventRemoveReminderEvent(EventAddReminderEvent):
    """Event triggered when a reminder is removed from an event"""

    event_name: str = "EVENT_REMOVE_REMINDER"


class EventAddAttendeeEvent(Event, BaseEventValidator):
    """Event triggered when an attendee is added to an event"""

    event_name: str = "EVENT_ADD_ATTENDEE"
    email: str

    class ValidationCriteria(BaseModel):
        email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return self._validate_field(self.email, criteria.email)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EventAddAttendeeEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}

        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            email=data.get("email", ""),
        )


class EventRemoveAttendeeEvent(EventAddAttendeeEvent):
    """Event triggered when an attendee is removed from an event"""

    event_name: str = "EVENT_REMOVE_ATTENDEE"


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
    SearchSubmitEvent,
    EventWizardOpenEvent,
    EventAddReminderEvent,
    EventRemoveReminderEvent,
    EventAddAttendeeEvent,
    EventRemoveAttendeeEvent,
]

BACKEND_EVENT_TYPES = {
    "SELECT_MONTH": SelectMonthEvent,
    "SELECT_WEEK": SelectWeekEvent,
    "SELECT_FIVE_DAYS": SelectFiveDaysEvent,
    "SELECT_DAY": SelectDayEvent,
    "SELECT_TODAY": SelectTodayEvent,
    "ADD_NEW_CALENDAR": AddNewCalendarEvent,
    "CREATE_CALENDAR": CreateCalendarEvent,
    "CHOOSE_CALENDAR": ChooseCalendarEvent,
    "ADD_EVENT": AddEventEvent,
    "CELL_CLICKED": CellClickedEvent,
    "CANCEL_ADD_EVENT": CancelAddEventEvent,
    "DELETE_ADDED_EVENT": DeleteAddedEventEvent,
    "SEARCH_SUBMIT": SearchSubmitEvent,
    "EVENT_ADD_REMINDER": EventAddReminderEvent,
    "EVENT_REMOVE_REMINDER": EventRemoveReminderEvent,
    "EVENT_ADD_ATTENDEE": EventAddAttendeeEvent,
    "EVENT_REMOVE_ATTENDEE": EventRemoveAttendeeEvent,
    "EVENT_WIZARD_OPEN": EventWizardOpenEvent,
}
