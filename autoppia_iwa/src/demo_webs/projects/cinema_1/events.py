from typing import Any, Dict, Optional

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.events import Event

# ================ Event Classes with Nested Validation Criteria ================


class RegistrationEvent(Event):
    """Event triggered when a user registration is completed"""

    username: str

    class ValidationCriteria(BaseModel):
        expected_username: Optional[str] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """Validate if this registration event meets the criteria"""
        if not criteria:
            return True

        if criteria.expected_username:
            return self.username == criteria.expected_username

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "RegistrationEvent":
        """Parse a registration event from backend data"""
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LoginEvent(Event):
    """Event triggered when a user logs in"""

    username: str

    class ValidationCriteria(BaseModel):
        expected_username: Optional[str] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """Validate if this login event meets the criteria"""
        if not criteria:
            return True

        if criteria.expected_username:
            return self.username == criteria.expected_username

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "LoginEvent":
        """Parse a login event from backend data"""
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


class LogoutEvent(Event):
    """Event triggered when a user logs out"""

    username: str

    class ValidationCriteria(BaseModel):
        expected_username: Optional[str] = None

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """Validate if this logout event meets the criteria"""
        if not criteria:
            return True

        if criteria.expected_username:
            return self.username == criteria.expected_username

        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "LogoutEvent":
        """Parse a logout event from backend data"""
        base_event = super().parse(backend_event)

        # Extract username from data field
        data = backend_event.get('data', {})
        username = data.get('username', '')

        return cls(event_name=base_event.event_name, timestamp=base_event.timestamp, web_agent_id=base_event.web_agent_id, user_id=base_event.user_id, username=username)


# ================ Available Events and Use Cases ================
EVENTS = [
    RegistrationEvent,
    LoginEvent,
    LogoutEvent,
]

BACKEND_EVENT_TYPES = {
    'LOGIN': LoginEvent,
    'LOGOUT': LogoutEvent,
    'REGISTRATION': RegistrationEvent,
}
