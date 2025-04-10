from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel


class Event(BaseModel):
    """Base event class for all event types"""

    event_name: str
    timestamp: int
    web_agent_id: str
    user_id: int | None = None

    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses in the ActionRegistry."""
        super().__init_subclass__(**kwargs)
        EventRegistry.register(cls)

    class ValidationCriteria(BaseModel):
        pass

    def validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria and hasattr(criteria, "model_fields"):
            for field_name in criteria.model_fields:
                field_value = getattr(criteria, field_name)

                if hasattr(field_value, "value"):
                    if isinstance(field_value.value, str):
                        replaced_value = field_value.value.replace("<web_agent_id>", self.web_agent_id)
                        field_value.value = replaced_value
                elif isinstance(field_value, str):
                    replaced_value = field_value.replace("<web_agent_id>", self.web_agent_id)
                    setattr(criteria, field_name, replaced_value)

        return self._validate_criteria(criteria)

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        """Check if this event meets the validation criteria"""
        return True

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "Event":
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
    def parse_all(backend_events: list["BackendEvent"]) -> list["Event"]:
        """Parse all backend events and return appropriate typed events"""
        events: list[Event] = []
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


# Registry class for Event subclasses
class EventRegistry:
    """Registry for storing and managing Event subclasses."""

    _registry: ClassVar[dict[str, type[Event]]] = {}

    @classmethod
    def register(cls, event_class: type[Event]) -> None:
        """Register an Event subclass."""
        if not issubclass(event_class, Event):
            raise ValueError(f"{event_class.__name__} is not a subclass of Event")
        cls._registry[event_class.__name__] = event_class

    @classmethod
    def get_event_class(cls, event_name: str) -> type[Event]:
        """Retrieve an Event subclass by its name."""
        if event_name not in cls._registry:
            raise ValueError(f"Event class '{event_name}' is not registered")
        return cls._registry[event_name]
