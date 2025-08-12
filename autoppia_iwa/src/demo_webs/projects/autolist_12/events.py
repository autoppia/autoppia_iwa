from datetime import datetime

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autolodge_8.data import parse_datetime
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import validate_date_field


class AddTaskClickedEvent(Event, BaseEventValidator):
    """Event triggered when user clicks the add task button"""

    event_name: str = "ADD_TASK_CLICKED"
    source: str

    class ValidationCriteria(BaseModel):
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.source, criteria.source)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddTaskClickedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            source=data.get("source", ""),
        )


class SelectDateForTaskEvent(Event, BaseEventValidator):
    """Event triggered when user selects a date for a task"""

    event_name: str = "SELECT_DATE_FOR_TASK"
    selected_date: datetime | None = None
    was_previously_selected: bool

    class ValidationCriteria(BaseModel):
        selectedDate: datetime | CriterionValue | None = None
        wasPreviouslySelected: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.selected_date, criteria.selectedDate)
        return all(
            [
                date_valid,
                self._validate_field(self.was_previously_selected, criteria.wasPreviouslySelected),
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
            selected_date=parse_datetime(data.get("selectedDate")),
            was_previously_selected=data.get("wasPreviouslySelected", False),
        )


class SelectTaskPriorityEvent(Event, BaseEventValidator):
    """Event triggered when user selects a priority for a task"""

    event_name: str = "SELECT_TASK_PRIORITY"
    priority: int
    label: str

    class ValidationCriteria(BaseModel):
        priority: int | CriterionValue | None = None
        label: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.priority, criteria.priority),
                self._validate_field(self.label, criteria.label),
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
            priority=data.get("priority", 4),
            label=data.get("label", ""),
        )


class TaskAddedEvent(Event, BaseEventValidator):
    """Event triggered when a task is added or updated"""

    event_name: str = "TASK_ADDED"
    action: str
    name: str
    description: str
    date: datetime | None = None
    priority: int

    class ValidationCriteria(BaseModel):
        action: str | CriterionValue | None = None
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
                self._validate_field(self.action, criteria.action),
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
            action=data.get("action", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            date=parse_datetime(data.get("date")),
            priority=data.get("priority", 4),
        )


class CancelTaskCreationEvent(Event, BaseEventValidator):
    """Event triggered when user cancels task creation"""

    event_name: str = "CANCEL_TASK_CREATION"
    current_name: str
    current_description: str
    selected_date: datetime | None = None
    priority: int
    is_editing: bool

    class ValidationCriteria(BaseModel):
        currentName: str | CriterionValue | None = None
        currentDescription: str | CriterionValue | None = None
        selectedDate: datetime | CriterionValue | None = None
        priority: int | CriterionValue | None = None
        isEditing: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.selected_date, criteria.selectedDate)
        return all(
            [
                self._validate_field(self.current_name, criteria.currentName),
                self._validate_field(self.current_description, criteria.currentDescription),
                date_valid,
                self._validate_field(self.priority, criteria.priority),
                self._validate_field(self.is_editing, criteria.isEditing),
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
            current_name=data.get("currentName", ""),
            current_description=data.get("currentDescription", ""),
            selected_date=parse_datetime(data.get("selectedDate")),
            priority=data.get("priority", 4),
            is_editing=data.get("isEditing", False),
        )


class EditTaskModalOpenedEvent(Event, BaseEventValidator):
    """Event triggered when the edit task modal is opened"""

    event_name: str = "EDIT_TASK_MODAL_OPENED"
    # task_id: str
    name: str
    description: str
    date: datetime | None = None
    priority: int

    class ValidationCriteria(BaseModel):
        # taskId: str | CriterionValue | None = None
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
                # self._validate_field(self.task_id, criteria.taskId),
                self._validate_field(self.name, criteria.name),
                self._validate_field(self.description, criteria.description),
                date_valid,
                self._validate_field(self.priority, criteria.priority),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EditTaskModalOpenedEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # task_id=data.get("taskId", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            date=parse_datetime(data.get("date")),
            priority=data.get("priority", 4),
        )


class CompleteTaskEvent(Event, BaseEventValidator):
    """Event triggered when a task is marked as complete"""

    event_name: str = "COMPLETE_TASK"
    # task_id: str
    name: str
    completed_at: datetime | None = None

    class ValidationCriteria(BaseModel):
        # taskId: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        completedAt: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.completed_at, criteria.completedAt)
        return all(
            [
                # self._validate_field(self.task_id, criteria.taskId),
                self._validate_field(self.name, criteria.name),
                date_valid,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CompleteTaskEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # task_id=data.get("taskId", ""),
            name=data.get("name", ""),
            completed_at=parse_datetime(data.get("completedAt")),
        )


class DeleteTaskEvent(Event, BaseEventValidator):
    """Event triggered when a task is deleted"""

    event_name: str = "DELETE_TASK"
    # task_id: str
    name: str
    deleted_at: datetime | None = None

    class ValidationCriteria(BaseModel):
        # taskId: str | CriterionValue | None = None
        name: str | CriterionValue | None = None
        deletedAt: datetime | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        date_valid = validate_date_field(self.deleted_at, criteria.deletedAt)
        return all(
            [
                # self._validate_field(self.task_id, criteria.taskId),
                self._validate_field(self.name, criteria.name),
                date_valid,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteTaskEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # task_id=data.get("taskId", ""),
            name=data.get("name", ""),
            deleted_at=parse_datetime(data.get("deletedAt")),
        )


EVENTS = [
    AddTaskClickedEvent,
    SelectTaskPriorityEvent,
    SelectDateForTaskEvent,
    TaskAddedEvent,
    CancelTaskCreationEvent,
    EditTaskModalOpenedEvent,
    CancelTaskCreationEvent,
    DeleteTaskEvent,
]

BACKEND_EVENT_TYPES = {
    "ADD_TASK_CLICKED": AddTaskClickedEvent,
    "SELECT_DATE_FOR_TASK": SelectDateForTaskEvent,
    "SELECT_TASK_PRIORITY": SelectTaskPriorityEvent,
    "TASK_ADDED": TaskAddedEvent,
    "CANCEL_TASK_CREATION": CancelTaskCreationEvent,
    "EDIT_TASK_MODAL_OPENED": EditTaskModalOpenedEvent,
    "COMPLETE_TASK": CompleteTaskEvent,
    "DELETE_TASK": DeleteTaskEvent,
}
