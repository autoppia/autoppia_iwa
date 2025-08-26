from datetime import datetime

from pydantic import BaseModel, Field

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autolodge_8.data import parse_datetime
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import validate_date_field


class AddTaskClickedEvent(Event, BaseEventValidator):
    """Event triggered when user clicks the add task button"""

    event_name: str = "AUTOLIST_ADD_TASK_CLICKED"


class SelectDateForTaskEvent(Event, BaseEventValidator):
    """Event triggered when user selects a date for a task"""

    event_name: str = "AUTOLIST_SELECT_DATE_FOR_TASK"
    date: datetime | None = None
    quick_option: str | None = None

    class ValidationCriteria(BaseModel):
        date: datetime | CriterionValue | None = None
        quick_option: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.date, criteria.date)
        return all(
            [
                date_valid,
                self._validate_field(self.quick_option, criteria.quick_option),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectDateForTaskEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=parse_datetime(data.get("selectedDate")),
            quick_option=data.get("quickOption"),
        )


class SelectTaskPriorityEvent(Event, BaseEventValidator):
    """Event triggered when user selects a priority for a task"""

    event_name: str = "AUTOLIST_SELECT_TASK_PRIORITY"
    priority: str
    # label: str

    class ValidationCriteria(BaseModel):
        priority: str | CriterionValue | None = None
        # label: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.priority, criteria.priority),
                # self._validate_field(self.label, criteria.label),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectTaskPriorityEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            priority=data.get("label", ""),
        )


class TaskAddedEvent(Event, BaseEventValidator):
    """Event triggered when a task is added or updated"""

    event_name: str = "AUTOLIST_TASK_ADDED"
    name: str
    description: str
    date: datetime | None = None
    priority: str

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        date: datetime | CriterionValue | None = None
        priority: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.date, criteria.date)
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.description, criteria.description),
                date_valid,
                self._validate_field(self.priority, criteria.priority),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TaskAddedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            date=parse_datetime(data.get("date")),
            priority=data.get("priority", ""),
        )


class EditTaskModalOpenedEvent(TaskAddedEvent):
    """Event triggered when the edit task modal is opened"""

    event_name: str = "AUTOLIST_EDIT_TASK_MODAL_OPENED"


class CompleteTaskEvent(TaskAddedEvent):
    """Event triggered when a task is marked as complete"""

    event_name: str = "AUTOLIST_COMPLETE_TASK"


class DeleteTaskEvent(TaskAddedEvent):
    """Event triggered when a task is deleted"""

    event_name: str = "AUTOLIST_DELETE_TASK"


class CancelTaskCreationEvent(Event, BaseEventValidator):
    """Event triggered when user cancels task creation"""

    event_name: str = "AUTOLIST_CANCEL_TASK_CREATION"
    name: str
    description: str
    date: datetime | None = None
    priority: int

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        date: datetime | CriterionValue | None = None
        priority: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.date, criteria.date)
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.description, criteria.description),
                date_valid,
                self._validate_field(self.priority, criteria.priority),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CancelTaskCreationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("currentName", ""),
            description=data.get("currentDescription", ""),
            date=parse_datetime(data.get("selectedDate")),
            priority=data.get("priority", 4),
        )


class AddTeamClickedEvent(Event):
    """Event triggered when user clicks the add team button"""

    event_name: str = "AUTOLIST_ADD_TEAM_CLICKED"


class TeamMembersAddedEvent(Event, BaseEventValidator):
    """Event triggered when team members are added"""

    event_name: str = "AUTOLIST_TEAM_MEMBERS_ADDED"
    member_count: int
    members: list[str]

    class ValidationCriteria(BaseModel):
        member_count: int | CriterionValue | None = None
        members: list[str] | CriterionValue | None = None

    def _validate_members(self, field_value, criterion):
        if criterion is None:
            return True
        if not isinstance(criterion, CriterionValue):
            return False

        op = criterion.operator
        val = criterion.value

        members = field_value if isinstance(field_value, list) else [str(field_value)]
        values = val if isinstance(val, list) else [val]

        if op == ComparisonOperator.CONTAINS:
            return any(v.lower() in member.lower() for v in values for member in members)
        elif op == ComparisonOperator.NOT_CONTAINS:
            return all(all(v.lower() not in member.lower() for v in values) for member in members)
        elif op == ComparisonOperator.IN_LIST:
            return any(member.lower() in [v.lower() for v in values] for member in members)
        elif op == ComparisonOperator.NOT_IN_LIST:
            return all(member.lower() not in [v.lower() for v in values] for member in members)
        return False

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.member_count, criteria.member_count),
                self._validate_members(self.members, criteria.members),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TeamMembersAddedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            member_count=data.get("memberCount", 0),
            members=data.get("members", []),
        )


class TeamRoleAssignedEvent(Event, BaseEventValidator):
    """Event triggered when a role is assigned to a team member"""

    event_name: str = "AUTOLIST_TEAM_ROLE_ASSIGNED"
    member: str
    role: str

    class ValidationCriteria(BaseModel):
        member: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.member, criteria.member),
                self._validate_field(self.role, criteria.role),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TeamRoleAssignedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            member=data.get("memberId", ""),
            role=data.get("role", ""),
        )


class TeamMember(BaseModel):
    id: str | None = None
    name: str | None = None
    role: str | None = None


class TeamCreatedEvent(Event, BaseEventValidator):
    """Event triggered when a team is created"""

    event_name: str = "AUTOLIST_TEAM_CREATED"
    name: str
    description: str | None = None
    members: list[TeamMember] | None = Field(default_factory=list)

    class ValidationCriteria(BaseModel):
        name: str | CriterionValue | None = None
        description: str | CriterionValue | None = None
        member: str | CriterionValue | None = None
        role: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.description, criteria.description),
                all(self._validate_field(member.name, criteria.member) and self._validate_field(member.role, criteria.role) for member in self.members) if criteria.member or criteria.role else True,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TeamCreatedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            name=data.get("teamName", ""),
            description=data.get("teamDescription"),
            members=[TeamMember(**m) for m in data.get("members", []) if data.get("members", [])],
        )


EVENTS = [
    AddTaskClickedEvent,
    SelectTaskPriorityEvent,
    SelectDateForTaskEvent,
    TaskAddedEvent,
    CancelTaskCreationEvent,
    EditTaskModalOpenedEvent,
    CompleteTaskEvent,
    DeleteTaskEvent,
    AddTeamClickedEvent,
    TeamMembersAddedEvent,
    TeamRoleAssignedEvent,
    TeamCreatedEvent,
]

BACKEND_EVENT_TYPES = {
    "AUTOLIST_ADD_TASK_CLICKED": AddTaskClickedEvent,
    "AUTOLIST_SELECT_DATE_FOR_TASK": SelectDateForTaskEvent,
    "AUTOLIST_SELECT_TASK_PRIORITY": SelectTaskPriorityEvent,
    "AUTOLIST_TASK_ADDED": TaskAddedEvent,
    "AUTOLIST_CANCEL_TASK_CREATION": CancelTaskCreationEvent,
    "AUTOLIST_EDIT_TASK_MODAL_OPENED": EditTaskModalOpenedEvent,
    "AUTOLIST_COMPLETE_TASK": CompleteTaskEvent,
    "AUTOLIST_DELETE_TASK": DeleteTaskEvent,
    "AUTOLIST_ADD_TEAM_CLICKED": AddTeamClickedEvent,
    "AUTOLIST_TEAM_MEMBERS_ADDED": TeamMembersAddedEvent,
    "AUTOLIST_TEAM_ROLE_ASSIGNED": TeamRoleAssignedEvent,
    "AUTOLIST_TEAM_CREATED": TeamCreatedEvent,
}
