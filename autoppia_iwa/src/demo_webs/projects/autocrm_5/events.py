from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

# =============================================================================
#                           BASE MODELS
# =============================================================================


class Matter(BaseModel):
    # id: str
    name: str
    client: str
    status: str
    updated: str


class Client(BaseModel):
    # id: str
    name: str
    email: str
    matters: int
    avatar: str = ""
    status: str
    last: str


class Document(BaseModel):
    # id: str
    name: str
    size: str
    version: str
    updated: str
    status: str


class CalendarEvent(BaseModel):
    # id: str
    date: str
    label: str
    time: str
    color: str


class TimeLog(BaseModel):
    # id: str
    matter: str
    client: str
    date: str
    hours: float
    description: str
    status: str


# =============================================================================
#                           EVENT CLASSES
# =============================================================================


class AddNewMatter(Event, BaseEventValidator):
    """Event triggered when a new matter is created"""

    event_name: str = "ADD_NEW_MATTER"
    matter: Matter

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
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
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None
        updated: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
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
    matter: list[Matter] = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None
        updated: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        return any(  # at least one of the deleted matters satisfies all criteria.
            all(
                [
                    self._validate_field(m.name, criteria.name),
                    self._validate_field(m.client, criteria.client),
                    self._validate_field(m.status, criteria.status),
                    self._validate_field(m.updated, criteria.updated),
                ]
            )
            for m in self.deleted
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteMatter":
        base_event = Event.parse(backend_event)
        deleted_matters = [Matter(**m) for m in backend_event.data.get("deleted", [])]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            matter=deleted_matters,
        )


class ArchiveMatter(Event, BaseEventValidator):
    """Event triggered when a matter is archived"""

    event_name: str = "ARCHIVE_MATTER"
    matters: list[Matter] = Field(default_factory=list)
    # matter: Matter

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return any(  # at least one of the deleted matters satisfies all criteria.
            all(
                [
                    self._validate_field(m.name, criteria.name),
                    self._validate_field(m.client, criteria.client),
                    self._validate_field(m.status, criteria.status),
                    # self._validate_field(m.updated, criteria.updated),
                ]
            )
            for m in self.deleted
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ArchiveMatter":
        base_event = Event.parse(backend_event)
        # archived_matters = [Matter(**m) for m in backend_event.data.get("archived", [])]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # matter=archived_matters,
        )


class ViewClientDetails(Event, BaseEventValidator):
    """Event triggered when client details are viewed"""

    event_name: str = "VIEW_CLIENT_DETAILS"
    client: Client

    class ValidationCriteria(BaseModel):
        # id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        matters: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.client.id, criteria.id),
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
        # min_length: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [self._validate_field(self.query, criteria.query)],
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


class DocumentDeleted(Event, BaseEventValidator):
    """Event triggered when a document is deleted"""

    event_name: str = "DOCUMENT_DELETED"
    document: Document

    class ValidationCriteria(BaseModel):
        # id: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.document.id, criteria.id),
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


class NewLogAdded(Event, BaseEventValidator):
    """Event triggered when a new time log is added"""

    event_name: str = "NEW_LOG_ADDED"
    log: TimeLog

    class ValidationCriteria(BaseModel):
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.log.hours, criteria.hours),
                self._validate_field(self.log.status, criteria.status),
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
                # id=str(data["id"]),
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
        # id: str | CriterionValue | None = None
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                # self._validate_field(self.log.id, criteria.id),
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


class ChangeUserName(Event, BaseEventValidator):
    """Event triggered when the user changes their name"""

    event_name: str = "CHANGE_USER_NAME"
    new_name: str

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None

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
    ArchiveMatter,
    AddNewMatter,
    ViewMatterDetails,
    DeleteMatter,
    ViewClientDetails,
    SearchClient,
    DocumentDeleted,
    NewCalendarEventAdded,
    NewLogAdded,
    LogDelete,
    ChangeUserName,
]

BACKEND_EVENT_TYPES = {
    "ADD_NEW_MATTER": AddNewMatter,
    "ArchiveMatter": ArchiveMatter,
    "VIEW_MATTER_DETAILS": ViewMatterDetails,
    "DELETE_MATTER": DeleteMatter,
    "VIEW_CLIENT_DETAILS": ViewClientDetails,
    "SEARCH_CLIENT": SearchClient,
    "DOCUMENT_DELETED": DocumentDeleted,
    "NEW_CALENDAR_EVENT_ADDED": NewCalendarEventAdded,
    "NEW_LOG_ADDED": NewLogAdded,
    "LOG_DELETE": LogDelete,
    "CHANGE_USER_NAME": ChangeUserName,
}
