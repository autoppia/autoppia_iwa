from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Event(BaseModel):
    """Base event class for all event types"""

    event_name: str
    timestamp: int
    web_agent_id: int
    user_id: Optional[int] = None

    class ValidationCriteria(BaseModel):
        pass

    def validate_criteria(self) -> bool:
        """Check if this event meets the validation criteria"""
        return True

    @classmethod
    def parse(cls, backend_event: Dict[str, Any]) -> "Event":
        """Base parse method for all events"""
        # Convert Django timestamp to Unix timestamp if needed
        if isinstance(backend_event.get('timestamp'), str):
            try:
                dt = datetime.fromisoformat(backend_event.get('timestamp').replace('Z', '+00:00'))
                timestamp = int(dt.timestamp())
            except (ValueError, TypeError):
                timestamp = int(datetime.now().timestamp())
        else:
            timestamp = int(datetime.now().timestamp())

        # Extract user_id from user object if it exists
        user_id = backend_event.get('user', None)
        return cls(event_name=backend_event.get('event_name', ''), timestamp=timestamp, web_agent_id=backend_event.get('web_agent_id', 0), user_id=user_id)

    @staticmethod
    def parse_all(backend_events: List[Dict[str, Any]]) -> List["Event"]:
        """Parse all backend events and return appropriate typed events"""
        events: List[Event] = []
        # TODO: If we have more types we should include here
        # TODO: Moving (ALL_BACKEND_EVENT_TYPES) here to resolve circular import error
        from autoppia_iwa.src.demo_webs.projects.cinema_1.events import BACKEND_EVENT_TYPES as web_1_backend_types

        ALL_BACKEND_EVENT_TYPES = web_1_backend_types

        event_class_map = ALL_BACKEND_EVENT_TYPES

        for event_data in backend_events:
            event_name = event_data.get('event_name', '')
            event_class = event_class_map.get(event_name, Event)
            try:
                events.append(event_class.parse(event_data))
            except Exception as e:
                print(f"Error parsing event {event_name}: {e}")
                # Fallback to base Event class if specific parsing fails
                events.append(Event.parse(event_data))

        return events

    @classmethod
    def code(cls) -> str:
        """Return the source code of the class"""
        import inspect

        return inspect.getsource(cls)
