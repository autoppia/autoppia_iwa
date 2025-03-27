from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue, validate_criterion


class AttendanceCreateEvent(Event):
    """Event triggered when an attendance record is created"""

    event_name: str = "ATTENDANCE_CREATE"
    attendance_id: str
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating attendance create events"""

        attendance_id: str | CriterionValue | None = None
        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.attendance_id is not None and not validate_criterion(self.attendance_id, criteria.attendance_id):
            return False
        return not (criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AttendanceCreateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            attendance_id=data.get("attendance_id", ""),
            employee_id=data.get("employee_id", ""),
        )


class AttendanceUpdateEvent(Event):
    """Event triggered when an attendance record is updated"""

    event_name: str = "ATTENDANCE_UPDATE"
    attendance_id: str
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating attendance update events"""

        attendance_id: str | CriterionValue | None = None
        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.attendance_id is not None and not validate_criterion(self.attendance_id, criteria.attendance_id):
            return False
        return not (criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AttendanceUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            attendance_id=data.get("attendance_id", ""),
            employee_id=data.get("employee_id", ""),
        )


class AttendanceDeleteEvent(Event):
    """Event triggered when an attendance record is deleted"""

    event_name: str = "ATTENDANCE_DELETE"
    attendance_id: str
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating attendance delete events"""

        attendance_id: str | CriterionValue | None = None
        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.attendance_id is not None and not validate_criterion(self.attendance_id, criteria.attendance_id):
            return False
        return not (criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AttendanceDeleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            attendance_id=data.get("attendance_id", ""),
            employee_id=data.get("employee_id", ""),
        )


class DepartmentCreateEvent(Event):
    """Event triggered when a department is created"""

    event_name: str = "DEPARTMENT_CREATE"
    department_id: str
    department_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating department create events"""

        department_id: str | CriterionValue | None = None
        department_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.department_id is not None and not validate_criterion(self.department_id, criteria.department_id):
            return False
        return not (criteria.department_name is not None and not validate_criterion(self.department_name, criteria.department_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DepartmentCreateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            department_id=data.get("department_id", ""),
            department_name=data.get("department_name", ""),
        )


class DepartmentUpdateEvent(Event):
    """Event triggered when a department is updated"""

    event_name: str = "DEPARTMENT_UPDATE"
    department_id: str
    department_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating department update events"""

        department_id: str | CriterionValue | None = None
        department_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.department_id is not None and not validate_criterion(self.department_id, criteria.department_id):
            return False
        return not (criteria.department_name is not None and not validate_criterion(self.department_name, criteria.department_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DepartmentUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            department_id=data.get("department_id", ""),
            department_name=data.get("department_name", ""),
        )


class DepartmentDeleteEvent(Event):
    """Event triggered when a department is deleted"""

    event_name: str = "DEPARTMENT_DELETE"
    department_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating department delete events"""

        department_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.department_id is not None:
            return validate_criterion(self.department_id, criteria.department_id)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DepartmentDeleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            department_id=data.get("department_id", ""),
        )


class EmployeeCreateEvent(Event):
    """Event triggered when an employee is created"""

    event_name: str = "EMPLOYEE_CREATE"
    employee_id: str
    employee_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating employee create events"""

        employee_id: str | CriterionValue | None = None
        employee_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id):
            return False
        return not (criteria.employee_name is not None and not validate_criterion(self.employee_name, criteria.employee_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmployeeCreateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
        )


class EmployeeUpdateEvent(Event):
    """Event triggered when an employee is updated"""

    event_name: str = "EMPLOYEE_UPDATE"
    employee_id: str
    employee_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating employee update events"""

        employee_id: str | CriterionValue | None = None
        employee_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id):
            return False
        return not (criteria.employee_name is not None and not validate_criterion(self.employee_name, criteria.employee_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmployeeUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            employee_id=data.get("employee_id", ""),
            employee_name=data.get("employee_name", ""),
        )


class EmployeeDeleteEvent(Event):
    """Event triggered when an employee is deleted"""

    event_name: str = "EMPLOYEE_DELETE"
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating employee delete events"""

        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.employee_id is not None:
            return validate_criterion(self.employee_id, criteria.employee_id)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmployeeDeleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            employee_id=data.get("employee_id", ""),
        )


class PayrollCreateEvent(Event):
    """Event triggered when a payroll record is created"""

    event_name: str = "PAYROLL_CREATE"
    payroll_id: str
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating payroll create events"""

        payroll_id: str | CriterionValue | None = None
        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.payroll_id is not None and not validate_criterion(self.payroll_id, criteria.payroll_id):
            return False
        return not (criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PayrollCreateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            payroll_id=data.get("payroll_id", ""),
            employee_id=data.get("employee_id", ""),
        )


class PayrollUpdateEvent(Event):
    """Event triggered when a payroll record is updated"""

    event_name: str = "PAYROLL_UPDATE"
    payroll_id: str
    employee_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating payroll update events"""

        payroll_id: str | CriterionValue | None = None
        employee_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.payroll_id is not None and not validate_criterion(self.payroll_id, criteria.payroll_id):
            return False
        return not (criteria.employee_id is not None and not validate_criterion(self.employee_id, criteria.employee_id))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PayrollUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            payroll_id=data.get("payroll_id", ""),
            employee_id=data.get("employee_id", ""),
        )


class PayrollDeleteEvent(Event):
    """Event triggered when a payroll record is deleted"""

    event_name: str = "PAYROLL_DELETE"
    payroll_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating payroll delete events"""

        payroll_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.payroll_id is not None:
            return validate_criterion(self.payroll_id, criteria.payroll_id)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PayrollDeleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            payroll_id=data.get("payroll_id", ""),
        )


class PositionCreateEvent(Event):
    """Event triggered when a position is created"""

    event_name: str = "POSITION_CREATE"
    position_id: str
    position_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating position create events"""

        position_id: str | CriterionValue | None = None
        position_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.position_id is not None and not validate_criterion(self.position_id, criteria.position_id):
            return False
        return not (criteria.position_name is not None and not validate_criterion(self.position_name, criteria.position_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PositionCreateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            position_id=data.get("position_id", ""),
            position_name=data.get("position_name", ""),
        )


class PositionUpdateEvent(Event):
    """Event triggered when a position is updated"""

    event_name: str = "POSITION_UPDATE"
    position_id: str
    position_name: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating position update events"""

        position_id: str | CriterionValue | None = None
        position_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.position_id is not None and not validate_criterion(self.position_id, criteria.position_id):
            return False
        return not (criteria.position_name is not None and not validate_criterion(self.position_name, criteria.position_name))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PositionUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            position_id=data.get("position_id", ""),
            position_name=data.get("position_name", ""),
        )


class PositionDeleteEvent(Event):
    """Event triggered when a position is deleted"""

    event_name: str = "POSITION_DELETE"
    position_id: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating position delete events"""

        position_id: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.position_id is not None:
            return validate_criterion(self.position_id, criteria.position_id)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "PositionDeleteEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            position_id=data.get("position_id", ""),
        )


class UserViewEvent(Event):
    """Event triggered when a user views something"""

    event_name: str = "USER_VIEW"
    viewed_item: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating user view events"""

        viewed_item: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.viewed_item is not None:
            return validate_criterion(self.viewed_item, criteria.viewed_item)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UserViewEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            viewed_item=data.get("viewed_item", ""),
        )


class UserUpdateEvent(Event):
    """Event triggered when a user updates their profile"""

    event_name: str = "USER_UPDATE"
    user_id: int
    updated_fields: list[str]

    class ValidationCriteria(BaseModel):
        """Criteria for validating user update events"""

        user_id: str | CriterionValue | None = None
        updated_fields: list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.user_id is not None and not validate_criterion(self.user_id, criteria.user_id):
            return False
        return not (criteria.updated_fields is not None and not validate_criterion(self.updated_fields, criteria.updated_fields))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UserUpdateEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            updated_fields=data.get("updated_fields", []),
        )


class UserRedirectEvent(Event):
    """Event triggered when a user is redirected"""

    event_name: str = "USER_REDIRECT"
    from_path: str
    to_path: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating user redirect events"""

        from_path: str | CriterionValue | None = None
        to_path: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.from_path is not None and not validate_criterion(self.from_path, criteria.from_path):
            return False
        return not (criteria.to_path is not None and not validate_criterion(self.to_path, criteria.to_path))

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "UserRedirectEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            from_path=data.get("from_path", ""),
            to_path=data.get("to_path", ""),
        )


# =============================================================================
#                    AVAILABLE EVENTS AND USE CASES
# =============================================================================

EVENTS = [
    AttendanceCreateEvent,
    AttendanceUpdateEvent,
    AttendanceDeleteEvent,
    DepartmentCreateEvent,
    DepartmentUpdateEvent,
    DepartmentDeleteEvent,
    EmployeeCreateEvent,
    EmployeeUpdateEvent,
    EmployeeDeleteEvent,
    PayrollCreateEvent,
    PayrollUpdateEvent,
    PayrollDeleteEvent,
    PositionCreateEvent,
    PositionUpdateEvent,
    PositionDeleteEvent,
    UserViewEvent,
    UserUpdateEvent,
    UserRedirectEvent,
]

BACKEND_EVENT_TYPES = {
    "ATTENDANCE_CREATE": AttendanceCreateEvent,
    "ATTENDANCE_UPDATE": AttendanceUpdateEvent,
    "ATTENDANCE_DELETE": AttendanceDeleteEvent,
    "DEPARTMENT_CREATE": DepartmentCreateEvent,
    "DEPARTMENT_UPDATE": DepartmentUpdateEvent,
    "DEPARTMENT_DELETE": DepartmentDeleteEvent,
    "EMPLOYEE_CREATE": EmployeeCreateEvent,
    "EMPLOYEE_UPDATE": EmployeeUpdateEvent,
    "EMPLOYEE_DELETE": EmployeeDeleteEvent,
    "PAYROLL_CREATE": PayrollCreateEvent,
    "PAYROLL_UPDATE": PayrollUpdateEvent,
    "PAYROLL_DELETE": PayrollDeleteEvent,
    "POSITION_CREATE": PositionCreateEvent,
    "POSITION_UPDATE": PositionUpdateEvent,
    "POSITION_DELETE": PositionDeleteEvent,
    "USER_VIEW": UserViewEvent,
    "USER_UPDATE": UserUpdateEvent,
    "USER_REDIRECT": UserRedirectEvent,
}
