from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue

# =============================================================================
#                           BASE MODELS
# =============================================================================


class Matter(BaseModel):
    name: str
    client: str
    status: str
    updated: str


class Client(BaseModel):
    name: str
    email: str
    matters: int
    avatar: str = ""
    status: str
    last: str


class Document(BaseModel):
    name: str
    size: str
    version: str
    updated: str
    status: str


class CalendarEvent(BaseModel):
    date: str
    label: str
    time: str
    event_type: str


class TimeLog(BaseModel):
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
                self._validate_field(self.matter.updated, criteria.updated),
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
            for m in self.matters
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
            matters=deleted_matters,
        )


class ArchiveMatter(Event, BaseEventValidator):
    """Event triggered when a matter is archived"""

    event_name: str = "ARCHIVE_MATTER"
    matters: list[Matter] = Field(default_factory=list)

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
            for m in self.matters
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ArchiveMatter":
        base_event = Event.parse(backend_event)
        archived_matters = [Matter(**m) for m in backend_event.data.get("archived", [])]
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            matters=archived_matters,
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
        size: str | CriterionValue | None = None
        version: str | CriterionValue | None = None
        # updated: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.document.name, criteria.name),
                self._validate_size_field(self.document.size, criteria.size),
                self._validate_field(self.document.version, criteria.version),
                # self._validate_field(self.document.updated, criteria.updated),
                self._validate_field(self.document.status, criteria.status),
            ],
        )

    def _parse_size_to_kb(self, val: Any) -> float | None:
        """
        Parse various size representations into KB as float.
        Accepts int/float (assumed KB), strings like '490 KB', '1.5 MB', '1024B', or plain numbers.
        Returns None when parsing fails.
        """
        if val is None:
            return None
        if isinstance(val, int | float):
            return float(val)  # assume KB
        if not isinstance(val, str):
            return None

        s = val.strip().upper().replace(",", "")
        try:
            if s.endswith("KB"):
                return float(s[:-2].strip())
            if s.endswith("MB"):
                return float(s[:-2].strip()) * 1024.0
            if s.endswith("B"):
                # bytes -> KB
                return float(s[:-1].strip()) / 1024.0
            # no unit, assume KB
            return float(s)
        except Exception:
            return None

    def _validate_size_field(self, actual: str, criterion: str | CriterionValue | None) -> bool:
        """
        Custom validator for document size that understands units and numeric operators.
        - If criterion is a plain string: equality check.
        - If criterion is CriterionValue with numeric-parsable value: convert both to KB and compare.
        """
        if criterion is None:
            return True

        if isinstance(criterion, str):
            return actual == criterion

        if isinstance(criterion, CriterionValue):
            op = criterion.operator
            crit_val = criterion.value

            actual_kb = self._parse_size_to_kb(actual)
            crit_kb = self._parse_size_to_kb(crit_val)

            if actual_kb is not None and crit_kb is not None:
                if op == ComparisonOperator.EQUALS:
                    return actual_kb == crit_kb
                if op == ComparisonOperator.NOT_EQUALS:
                    return actual_kb != crit_kb
                if op == ComparisonOperator.GREATER_THAN:
                    return actual_kb > crit_kb
                if op == ComparisonOperator.LESS_THAN:
                    return actual_kb < crit_kb
                if op == ComparisonOperator.GREATER_EQUAL:
                    return actual_kb >= crit_kb
                if op == ComparisonOperator.LESS_EQUAL:
                    return actual_kb <= crit_kb

        return False

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
        label: str | CriterionValue | None = None
        date: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        event_type: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.event_data.label, criteria.label),
                self._validate_field(self.event_data.date, criteria.date),
                self._validate_field(self.event_data.time, criteria.time),
                self._validate_field(self.event_data.event_type, criteria.event_type),
            ],
        )

    def _validate_field(self, actual: str, criterion: str | CriterionValue | None) -> bool:
        if criterion is None:
            return True

        if isinstance(criterion, str):
            return actual == criterion

        if isinstance(criterion, CriterionValue):
            op = criterion.operator
            value = criterion.value

            # Check for date
            if self._is_date(actual) and self._is_date(value):
                actual_date = date.fromisoformat(actual)
                value_date = date.fromisoformat(value)
                return self._apply_operator(actual_date, value_date, op)

            # Check for time
            if self._is_time(actual) and self._is_time(value):
                actual_time = self._parse_time(actual)
                value_time = self._parse_time(value)
                return self._apply_operator(actual_time, value_time, op)

            # Fallback: string-based comparisons
            if op == ComparisonOperator.EQUALS:
                return actual == value
            elif op == ComparisonOperator.NOT_EQUALS:
                return actual != value
            elif op == ComparisonOperator.CONTAINS:
                return value in actual
            elif op == ComparisonOperator.NOT_CONTAINS:
                return value not in actual
            elif op == ComparisonOperator.GREATER_EQUAL:
                return actual >= value
            elif op == ComparisonOperator.LESS_EQUAL:
                return actual <= value
        return False

    def _apply_operator(self, actual, value, op: ComparisonOperator) -> bool:
        if op == ComparisonOperator.EQUALS:
            return actual == value
        elif op == ComparisonOperator.NOT_EQUALS:
            return actual != value
        elif op == ComparisonOperator.GREATER_EQUAL:
            return actual >= value
        elif op == ComparisonOperator.LESS_EQUAL:
            return actual <= value
        elif op == ComparisonOperator.GREATER_THAN:
            return actual > value
        elif op == ComparisonOperator.LESS_THAN:
            return actual < value
        elif op == ComparisonOperator.CONTAINS:
            return str(value) in str(actual)
        elif op == ComparisonOperator.NOT_CONTAINS:
            return str(value) not in str(actual)
        return False

    def _is_date(self, val: str) -> bool:
        try:
            date.fromisoformat(val)
            return True
        except ValueError:
            return False

    def _is_time(self, val: str) -> bool:
        try:
            self._parse_time(val)
            return True
        except ValueError:
            return False

    def _parse_time(self, val: str) -> time:
        val = val.strip().lower()
        try:
            return datetime.strptime(val, "%H:%M").time()
        except ValueError:
            pass
        try:
            return datetime.strptime(val, "%I:%M%p").time()
        except ValueError as ve:
            raise ValueError(f"Invalid time format: {val}") from ve

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "NewCalendarEventAdded":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            event_data=CalendarEvent(
                label=data.get("label", ""),
                date=data.get("date", ""),
                time=data.get("time", ""),
                event_type=data.get("color", ""),
            ),
        )


class NewLogAdded(Event, BaseEventValidator):
    """Event triggered when a new time log is added"""

    event_name: str = "NEW_LOG_ADDED"
    log: TimeLog

    class ValidationCriteria(BaseModel):
        matter: str | CriterionValue | None = None
        # client: str | CriterionValue | None = None
        # date: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        hours: float | CriterionValue | None = None
        # status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.log.matter, criteria.matter),
                # self._validate_field(self.log.client, criteria.client),
                # self._validate_field(self.log.date, criteria.date),
                self._validate_field(self.log.description, criteria.description),
                self._validate_field(self.log.hours, criteria.hours),
                # self._validate_field(self.log.status, criteria.status),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "NewLogAdded":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            log=TimeLog(**backend_event.data),
        )


class LogDelete(Event, BaseEventValidator):
    """Event triggered when a time log is deleted"""

    event_name: str = "LOG_DELETE"
    log: TimeLog

    class ValidationCriteria(BaseModel):
        matter: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        # date: str|CriterionValue|None = None
        # description: str | CriterionValue | None = None
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.log.matter, criteria.matter),
                self._validate_field(self.log.client, criteria.client),
                # self._validate_field(self.log.date, criteria.date),
                # self._validate_field(self.log.description, criteria.description),
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
