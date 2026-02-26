from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

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


class BillingSearchPayload(BaseModel):
    query: str
    date_filter: str | None = None
    custom_date: date | None = None


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


class ClientPayload(BaseModel):
    id: str | None = None
    name: str
    email: str
    matters: int
    status: str
    last: str


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
                return BaseEventValidator._validate_field(actual_kb, CriterionValue(value=crit_kb, operator=op))

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


class DocumentRenamedEvent(Event, BaseEventValidator):
    """Event triggered when a document is renamed."""

    event_name: str = "DOCUMENT_RENAMED"
    previous_name: str
    new_name: str

    class ValidationCriteria(BaseModel):
        previous_name: str | CriterionValue | None = None
        new_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.document.previous_name, criteria.previous_name),
                self._validate_field(self.new_name, criteria.new_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DocumentRenamedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        new_name = data.get("newName") or data.get("new_name")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            previous_name=data.get("previousName"),
            new_name=new_name,
        )


class AddClientEvent(Event, BaseEventValidator):
    """Event triggered when a client is added."""

    event_name: str = "ADD_CLIENT"
    client: ClientPayload

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        status: str | CriterionValue | None = None
        matters: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.client.name, criteria.name),
                self._validate_field(self.client.email, criteria.email),
                self._validate_field(self.client.status, criteria.status),
                self._validate_field(self.client.matters, criteria.matters),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddClientEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            client=ClientPayload(**backend_event.data),
        )


class DeleteClientEvent(Event, BaseEventValidator):
    """Event triggered when a client is deleted."""

    event_name: str = "DELETE_CLIENT"
    client: ClientPayload

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        email: str | CriterionValue | None = None
        status: str | CriterionValue | None = None
        matters: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.client.name, criteria.name),
                self._validate_field(self.client.email, criteria.email),
                self._validate_field(self.client.status, criteria.status),
                self._validate_field(self.client.matters, criteria.matters),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteClientEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            client=ClientPayload(**backend_event.data),
        )


class FilterClientsEvent(Event, BaseEventValidator):
    """Event for client filtering."""

    event_name: str = "FILTER_CLIENTS"
    status: str | None = None
    matters: str | None = None

    class ValidationCriteria(BaseModel):
        status: str | CriterionValue | None = None
        matters: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.status, criteria.status),
                self._validate_field(self.matters, criteria.matters),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FilterClientsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            status=data.get("status"),
            matters=data.get("matters"),
        )


class HelpViewedEvent(Event, BaseEventValidator):
    """Event when help page is viewed."""

    event_name: str = "HELP_VIEWED"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "HelpViewedEvent":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
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

    def _validate_field(self, actual: Any, criterion: str | CriterionValue | None) -> bool:
        if criterion is None:
            return True

        if isinstance(criterion, str):
            if self._is_time(str(actual)) and self._is_time(criterion):
                try:
                    actual_time = self._parse_time(str(actual))
                    criterion_time = self._parse_time(criterion)
                    return actual_time == criterion_time
                except ValueError:
                    return str(actual) == criterion

            if self._is_date(str(actual)) and self._is_date(criterion):
                try:
                    actual_date = self._parse_date(str(actual))
                    criterion_date = self._parse_date(criterion)
                    return actual_date == criterion_date
                except ValueError:
                    return str(actual) == criterion

            return str(actual) == criterion

        if isinstance(criterion, CriterionValue):
            op = criterion.operator
            value = criterion.value

            if self._is_date(str(actual)) and self._is_date(str(value)):
                try:
                    actual_date = self._parse_date(str(actual))
                    value_date = self._parse_date(str(value))
                    return BaseEventValidator._validate_field(actual_date, CriterionValue(value=value_date, operator=op))
                except ValueError:
                    pass

            if self._is_time(str(actual)) and self._is_time(str(value)):
                try:
                    actual_time = self._parse_time(str(actual))
                    value_time = self._parse_time(str(value))
                    return BaseEventValidator._validate_field(actual_time, CriterionValue(value=value_time, operator=op))
                except ValueError:
                    pass

            return BaseEventValidator._validate_field(actual, criterion)

        return False

    def _is_date(self, val: str) -> bool:
        try:
            self._parse_date(val)
            return True
        except ValueError:
            return False

    def _is_time(self, val: str) -> bool:
        try:
            self._parse_time(val)
            return True
        except ValueError:
            return False

    def _parse_date(self, val: str) -> date:
        """Parse date string in various formats"""
        val = val.strip()

        # Try ISO format first (YYYY-MM-DD)
        try:
            return date.fromisoformat(val)
        except ValueError:
            pass

        # Try other common formats
        formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Invalid date format: {val}")

    def _parse_time(self, val: str) -> time:
        val = val.strip().lower()
        try:
            return datetime.strptime(val, "%H:%M").time()
        except ValueError:
            pass

        # Try 12-hour format with AM/PM
        try:
            # Handle both "am/pm" and "a.m./p.m." formats
            val_clean = val.replace(".", "").replace(" ", "")
            return datetime.strptime(val_clean, "%I:%M%p").time()
        except ValueError:
            pass

        # Try with space between time and AM/PM
        try:
            return datetime.strptime(val, "%I:%M %p").time()
        except ValueError:
            pass

        raise ValueError(f"Invalid time format: {val}")

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


class LogEdited(Event, BaseEventValidator):
    """Event triggered when a time log is edited"""

    event_name: str = "LOG_EDITED"
    after: TimeLog

    class ValidationCriteria(BaseModel):
        matter: str | CriterionValue | None = None
        client: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        hours: float | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.after.matter, criteria.matter),
                self._validate_field(self.after.client, criteria.client),
                self._validate_field(self.after.description, criteria.description),
                self._validate_field(self.after.hours, criteria.hours),
                self._validate_field(self.after.status, criteria.status),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LogEdited":
        base_event = Event.parse(backend_event)
        after_log = TimeLog(**backend_event.data.get("after", {}))
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            after=after_log,
        )


class BillingSearchEvent(Event, BaseEventValidator):
    """Event triggered when billing entries are searched or filtered."""

    event_name: str = "BILLING_SEARCH"
    payload: BillingSearchPayload

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None
        date_filter: str | CriterionValue | None = None
        custom_date: date | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.payload.query, criteria.query),
                self._validate_field(self.payload.date_filter, criteria.date_filter),
                self._validate_field(self.payload.custom_date, criteria.custom_date),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "BillingSearchEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        payload = data.get("payload") or data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            payload=BillingSearchPayload(
                query=payload.get("query", ""),
                date_filter=payload.get("date_filter"),
                custom_date=payload.get("custom_date"),
            ),
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


class SearchMatter(Event, BaseEventValidator):
    """Event triggered when searching for matters"""

    event_name: str = "SEARCH_MATTER"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.query, criteria.query),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchMatter":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            query=backend_event.data.get("query", ""),
        )


class FilterMatterStatus(Event, BaseEventValidator):
    """Event triggered when filtering matters by status"""

    event_name: str = "FILTER_MATTER_STATUS"
    status: str

    class ValidationCriteria(BaseModel):
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.status, criteria.status)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "FilterMatterStatus":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            status=backend_event.data.get("status", ""),
        )


class SortMatterByCreatedAt(Event, BaseEventValidator):
    """Event triggered when sorting matters by created date"""

    event_name: str = "SORT_MATTER_BY_CREATED_AT"
    direction: str

    class ValidationCriteria(BaseModel):
        direction: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.direction, criteria.direction)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SortMatterByCreatedAt":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            direction=backend_event.data.get("direction", ""),
        )


class UpdateMatter(Event, BaseEventValidator):
    """Event triggered when a matter is updated"""

    event_name: str = "UPDATE_MATTER"
    after: Matter

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
                self._validate_field(self.after.name, criteria.name),
                self._validate_field(self.after.client, criteria.client),
                self._validate_field(self.after.status, criteria.status),
                self._validate_field(self.after.updated, criteria.updated),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UpdateMatter":
        base_event = Event.parse(backend_event)
        after_matter = Matter(**backend_event.data.get("after", {}))
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            after=after_matter,
        )


class ViewPendingEvents(Event, BaseEventValidator):
    """Event triggered when viewing pending calendar events"""

    event_name: str = "VIEW_PENDING_EVENTS"
    earliest: str | None = None

    class ValidationCriteria(BaseModel):
        earliest: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.earliest, criteria.earliest),
            ],
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewPendingEvents":
        base_event = Event.parse(backend_event)
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            earliest=backend_event.data.get("earliest"),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================

EVENTS = [
    AddNewMatter,
    ViewMatterDetails,
    SearchMatter,
    FilterMatterStatus,
    SortMatterByCreatedAt,
    UpdateMatter,
    DeleteMatter,
    ArchiveMatter,
    ViewClientDetails,
    SearchClient,
    DocumentDeleted,
    DocumentRenamedEvent,
    NewCalendarEventAdded,
    ViewPendingEvents,
    NewLogAdded,
    LogEdited,
    BillingSearchEvent,
    LogDelete,
    ChangeUserName,
    AddClientEvent,
    DeleteClientEvent,
    FilterClientsEvent,
    HelpViewedEvent,
]

BACKEND_EVENT_TYPES = {
    "ADD_NEW_MATTER": AddNewMatter,
    "ARCHIVE_MATTER": ArchiveMatter,
    "VIEW_MATTER_DETAILS": ViewMatterDetails,
    "DELETE_MATTER": DeleteMatter,
    "VIEW_CLIENT_DETAILS": ViewClientDetails,
    "SEARCH_CLIENT": SearchClient,
    "DOCUMENT_DELETED": DocumentDeleted,
    "DOCUMENT_RENAMED": DocumentRenamedEvent,
    "NEW_CALENDAR_EVENT_ADDED": NewCalendarEventAdded,
    "NEW_LOG_ADDED": NewLogAdded,
    "LOG_EDITED": LogEdited,
    "BILLING_SEARCH": BillingSearchEvent,
    "LOG_DELETE": LogDelete,
    "CHANGE_USER_NAME": ChangeUserName,
    "SEARCH_MATTER": SearchMatter,
    "FILTER_MATTER_STATUS": FilterMatterStatus,
    "SORT_MATTER_BY_CREATED_AT": SortMatterByCreatedAt,
    "UPDATE_MATTER": UpdateMatter,
    "VIEW_PENDING_EVENTS": ViewPendingEvents,
    "ADD_CLIENT": AddClientEvent,
    "DELETE_CLIENT": DeleteClientEvent,
    "FILTER_CLIENTS": FilterClientsEvent,
    "HELP_VIEWED": HelpViewedEvent,
}
