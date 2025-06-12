from datetime import datetime

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

# =============================================================================
#                           BASE MODELS
# =============================================================================


class SidebarItem(BaseModel):
    label: str
    href: str


class Matter(BaseModel):
    id: str
    name: str
    client: str
    status: str
    updated: str


class Client(BaseModel):
    id: str
    name: str
    email: str
    matters: int
    avatar: str = ""
    status: str
    last: str


class Document(BaseModel):
    id: str
    name: str
    size: str
    version: str
    updated: str
    status: str


class CalendarEvent(BaseModel):
    id: str
    date: str
    label: str
    time: str
    color: str


class TimeLog(BaseModel):
    id: str
    matter: str
    client: str
    date: str
    hours: float
    description: str
    status: str


# =============================================================================
#                           EVENT CLASSES
# =============================================================================


class MattersSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Matters is clicked in sidebar"""

    event_name: str = "MATTERS_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [self._validate_field(self.data.label, criteria.label), self._validate_field(self.data.href, criteria.href)],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "MattersSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class AddNewMatter(Event, BaseEventValidator):
    """Event triggered when a new matter is created"""

    event_name: str = "ADD_NEW_MATTER"
    matter: Matter

    class ValidationCriteria(BaseModel):
        id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.matter.id, criteria.id),
                self._validate_field(self.matter.name, criteria.name),
                self._validate_field(self.matter.client, criteria.client),
                self._validate_field(self.matter.status, criteria.status),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddNewMatter":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            matter=Matter(**backend_event.data),
        )


class ViewMatterDetails(Event, BaseEventValidator):
    """Event triggered when matter details are viewed"""

    event_name: str = "VIEW_MATTER_DETAILS"
    matter: Matter

    class ValidationCriteria(BaseModel):
        id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.matter.id, criteria.id),
                self._validate_field(self.matter.name, criteria.name),
                self._validate_field(self.matter.client, criteria.client),
                self._validate_field(self.matter.status, criteria.status),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewMatterDetails":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            matter=Matter(**backend_event.data),
        )


class DeleteMatter(Event, BaseEventValidator):
    """Event triggered when a matter is deleted"""

    event_name: str = "DELETE_MATTER"
    matters: list[Matter] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        min_count: int | CriterionValue | None = None
        max_count: int | CriterionValue | None = None
        matter_ids: list[str] | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        matter_ids = {m.id for m in self.matters}
        return all(
            [
                self._validate_field(len(self.matters), criteria.min_count),
                self._validate_field(len(self.matters), criteria.max_count),
                (not criteria.matter_ids or any(id in matter_ids for id in criteria.matter_ids)),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteMatter":
        base_event = Event.parse(backend_event)
        matters = [Matter(**item) for item in backend_event.data]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            matters=matters,
        )


class ClientsSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Clients is clicked in sidebar"""

    event_name: str = "CLIENTS_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [self._validate_field(self.data.label, criteria.label), self._validate_field(self.data.href, criteria.href)],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ClientsSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class ViewClientDetails(Event, BaseEventValidator):
    """Event triggered when client details are viewed"""

    event_name: str = "VIEW_CLIENT_DETAILS"
    client: Client

    class ValidationCriteria(BaseModel):
        id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        matters: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.client.id, criteria.id),
                self._validate_field(self.client.name, criteria.name),
                self._validate_field(self.client.email, criteria.email),
                self._validate_field(self.client.matters, criteria.matters),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewClientDetails":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            client=Client(**backend_event.data),
        )


class SearchClient(Event, BaseEventValidator):
    """Event triggered when searching for clients"""

    event_name: str = "SEARCH_CLIENT"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        min_length: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [self._validate_field(self.query, criteria.query), (criteria.min_length is None or len(self.query) >= criteria.min_length)],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchClient":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=backend_event.data.get("query", ""),
        )


class DocumentsSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Documents is clicked in sidebar"""

    event_name: str = "DOCUMENTS_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [self._validate_field(self.data.label, criteria.label), self._validate_field(self.data.href, criteria.href)],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DocumentsSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class DocumentUploaded(Event, BaseEventValidator):
    """Event triggered when a document is uploaded"""

    event_name: str = "DOCUMENT_UPLOADED"
    document: Document

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        size: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.document.name, criteria.name),
                self._validate_field(self.document.size, criteria.size),
                self._validate_field(self.document.status, criteria.status),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DocumentUploaded":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            document=Document(**backend_event.data),
        )


class DocumentDeleted(Event, BaseEventValidator):
    """Event triggered when a document is deleted"""

    event_name: str = "DOCUMENT_DELETED"
    document: Document

    class ValidationCriteria(BaseModel):
        id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.document.id, criteria.id),
                self._validate_field(self.document.name, criteria.name),
                self._validate_field(self.document.status, criteria.status),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DocumentDeleted":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            document=Document(**backend_event.data),
        )


class CalendarSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Calendar is clicked in sidebar"""

    event_name: str = "CALENDAR_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([self._validate_field(self.data.label, criteria.label), self._validate_field(self.data.href, criteria.href)])

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CalendarSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class NewCalendarEventAdded(Event, BaseEventValidator):
    """Event triggered when a new calendar event is added"""

    event_name: str = "NEW_CALENDAR_EVENT_ADDED"
    event_data: CalendarEvent

    class ValidationCriteria(BaseModel):
        date: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        color: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.event_data.date, criteria.date),
                self._validate_field(self.event_data.time, criteria.time),
                self._validate_field(self.event_data.color, criteria.color),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "NewCalendarEventAdded":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            event_data=CalendarEvent(**backend_event.data),
        )


class TimeAndBillingSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Time & Billing is clicked in sidebar"""

    event_name: str = "TIME_AND_BILLING_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.data.label, criteria.label),
                self._validate_field(self.data.href, criteria.href),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TimeAndBillingSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class TimerStarted(Event, BaseEventValidator):
    """Event triggered when timer is started"""

    event_name: str = "TIMER_STARTED"
    started_at: datetime

    class ValidationCriteria(BaseModel):
        time_range: tuple[datetime, datetime] | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria or not criteria.time_range:
            return True
        start, end = criteria.time_range
        return start <= self.started_at <= end

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TimerStarted":
        base_event = Event.parse(backend_event)
        started_at = datetime.fromisoformat(backend_event.data["startedAt"])
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            started_at=started_at,
        )


class NewLogAdded(Event, BaseEventValidator):
    """Event triggered when a new time log is added"""

    event_name: str = "NEW_LOG_ADDED"
    log: TimeLog

    class ValidationCriteria(BaseModel):
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None
        min_hours: float | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.log.hours, criteria.hours),
                self._validate_field(self.log.status, criteria.status),
                (criteria.min_hours is None or self.log.hours >= criteria.min_hours),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "NewLogAdded":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            log=TimeLog(
                id=str(data["id"]),
                matter=data["matter"],
                client=data["client"],
                date=data["date"],
                hours=data["hours"],
                description=data["description"],
                status=data["status"],
            ),
        )


class TimerStopped(Event, BaseEventValidator):
    """Event triggered when timer is stopped"""

    event_name: str = "TIMER_STOPPED"
    duration: int
    log: TimeLog

    class ValidationCriteria(BaseModel):
        min_duration: int | CriterionValue | None = None
        max_duration: int | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                (criteria.min_duration is None or self.duration >= criteria.min_duration),
                (criteria.max_duration is None or self.duration <= criteria.max_duration),
                self._validate_field(self.log.status, criteria.status),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TimerStopped":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            duration=data["duration"],
            log=TimeLog(
                id=str(data["id"]),
                matter=data["matter"],
                client=data["client"],
                date=data["date"],
                hours=data["hours"],
                description=data["description"],
                status=data["status"],
            ),
        )


class LogDelete(Event, BaseEventValidator):
    """Event triggered when a time log is deleted"""

    event_name: str = "LOG_DELETE"
    log: TimeLog

    class ValidationCriteria(BaseModel):
        id: str | CriterionValue | None = None
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.log.id, criteria.id),
                self._validate_field(self.log.hours, criteria.hours),
                self._validate_field(self.log.status, criteria.status),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LogDelete":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            log=TimeLog(**backend_event.data),
        )


class SettingsSidebarClicked(Event, BaseEventValidator):
    """Event triggered when Settings is clicked in sidebar"""

    event_name: str = "SETTINGS_SIDEBAR_CLICKED"
    data: SidebarItem

    class ValidationCriteria(BaseModel):
        label: str | CriterionValue | None = None
        href: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.data.label, criteria.label),
                self._validate_field(self.data.href, criteria.href),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SettingsSidebarClicked":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            data=SidebarItem(**backend_event.data),
        )


class ChangeUserName(Event, BaseEventValidator):
    """Event triggered when user changes their name"""

    event_name: str = "CHANGE_USER_NAME"
    new_name: str

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        min_length: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.new_name, criteria.name),
                (criteria.min_length is None or len(self.new_name) >= criteria.min_length),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ChangeUserName":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            new_name=backend_event.data["name"],
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================

EVENTS = [
    MattersSidebarClicked,
    AddNewMatter,
    ViewMatterDetails,
    DeleteMatter,
    ClientsSidebarClicked,
    ViewClientDetails,
    SearchClient,
    DocumentsSidebarClicked,
    DocumentUploaded,
    DocumentDeleted,
    CalendarSidebarClicked,
    NewCalendarEventAdded,
    TimeAndBillingSidebarClicked,
    TimerStarted,
    NewLogAdded,
    TimerStopped,
    LogDelete,
    SettingsSidebarClicked,
    ChangeUserName,
]

BACKEND_EVENT_TYPES = {
    "MATTERS_SIDEBAR_CLICKED": MattersSidebarClicked,
    "ADD_NEW_MATTER": AddNewMatter,
    "VIEW_MATTER_DETAILS": ViewMatterDetails,
    "DELETE_MATTER": DeleteMatter,
    "CLIENTS_SIDEBAR_CLICKED": ClientsSidebarClicked,
    "VIEW_CLIENT_DETAILS": ViewClientDetails,
    "SEARCH_CLIENT": SearchClient,
    "DOCUMENTS_SIDEBAR_CLICKED": DocumentsSidebarClicked,
    "DOCUMENT_UPLOADED": DocumentUploaded,
    "DOCUMENT_DELETED": DocumentDeleted,
    "CALENDAR_SIDEBAR_CLICKED": CalendarSidebarClicked,
    "NEW_CALENDAR_EVENT_ADDED": NewCalendarEventAdded,
    "TIME_AND_BILLING_SIDEBAR_CLICKED": TimeAndBillingSidebarClicked,
    "TIMER_STARTED": TimerStarted,
    "NEW_LOG_ADDED": NewLogAdded,
    "TIMER_STOPPED": TimerStopped,
    "LOG_DELETE": LogDelete,
    "SETTINGS_SIDEBAR_CLICKED": SettingsSidebarClicked,
    "CHANGE_USER_NAME": ChangeUserName,
}
