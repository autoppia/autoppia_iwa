from typing import List, Optional

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
    def parse(cls, backend_event) -> "Event":
        return cls()

    def parse_all(self, backend_events) -> List["Event"]:
        events = []
        for event in backend_events:
            events.append(Event.parse(event))
        return events

    @classmethod
    def code(cls) -> str:
        """Return the source code of the class"""
        import inspect

        return inspect.getsource(cls)
