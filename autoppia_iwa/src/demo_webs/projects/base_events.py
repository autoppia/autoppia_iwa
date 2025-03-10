from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent


class Event(BaseModel):
    """Base event class for all event types"""

    event_name: str
    timestamp: int
    web_agent_id: str
    user_id: Optional[int] = None

    class ValidationCriteria(BaseModel):
        pass

    def validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        if criteria and hasattr(criteria, "model_fields"):
            for field_name in criteria.model_fields:
                field_value = getattr(criteria, field_name)
                if isinstance(field_value, str):
                    replaced_value = field_value.replace('<web_agent_id>', self.web_agent_id)
                    setattr(criteria, field_name, replaced_value)
        return self._validate_criteria(criteria)

    def _validate_criteria(self, criteria: Optional[ValidationCriteria] = None) -> bool:
        """Check if this event meets the validation criteria"""
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "Event":
        """Base parse method for all events"""
        # Convert Django timestamp to Unix timestamp if needed
        if isinstance(backend_event.timestamp, str):
            try:
                dt = datetime.fromisoformat(backend_event.timestamp)
                timestamp = int(dt.timestamp())
            except (ValueError, TypeError):
                timestamp = int(datetime.now().timestamp())
        else:
            timestamp = int(datetime.now().timestamp())

        # Extract user_id from user object if it exists
        user_id = backend_event.user_id or None
        web_agent_id = backend_event.web_agent_id or None
        return cls(event_name=backend_event.event_name, timestamp=timestamp, web_agent_id=web_agent_id, user_id=user_id)

    @staticmethod
    def parse_all(backend_events: List[BackendEvent]) -> List["Event"]:
        """Parse all backend events and return appropriate typed events"""
        events: List[Event] = []
        # TODO: If we have more types we should include here
        # TODO: Moving (ALL_BACKEND_EVENT_TYPES) here to resolve circular import error
        from autoppia_iwa.src.demo_webs.projects.cinema_1.events import BACKEND_EVENT_TYPES as web_1_backend_types

        ALL_BACKEND_EVENT_TYPES = web_1_backend_types

        event_class_map = ALL_BACKEND_EVENT_TYPES

        for event_data in backend_events:
            event_name = event_data.event_name
            event_class = event_class_map.get(event_name, Event)
            try:
                events.append(event_class.parse(event_data))
            except Exception as e:
                print(f"Error parsing event {event_name}: {e}")
                # Fallback to base Event class if specific parsing fails
                events.append(Event.parse(event_data))

        return events

    @classmethod
    def get_source_code_of_class(cls) -> str:
        """Return the source code of the class"""
        import inspect

        return inspect.getsource(cls)

    @classmethod
    def get_event_type(cls) -> str:
        # Si la clase tiene definido event_type, se usa; sino, se deriva del nombre quitando "Event"
        return getattr(cls, "event_type", cls.__name__.replace("Event", "").upper())
