from datetime import datetime
from typing import ClassVar

from loguru import logger
from pydantic import BaseModel, ValidationError


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
                logger.debug(f"Before: {field_value}. self_web_agent_id: {self.web_agent_id}")

                if hasattr(field_value, "value") and isinstance(field_value.value, str):
                    field_value.value = field_value.value.replace("<web_agent_id>", self.web_agent_id)
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

        event = cls(
            event_name=backend_event.event_name,
            timestamp=timestamp,
            web_agent_id=backend_event.web_agent_id or "",
            user_id=backend_event.user_id or None,
        )
        return event

    @staticmethod
    def parse_all(backend_events: list["BackendEvent"]) -> list["Event"]:
        """
        Parse multiple backend events into typed event instances.

        Args:
            backend_events: List of raw event data from the backend

        Returns:
            List of parsed event instances
        """
        events: list[Event] = []
        if not backend_events:
            logger.warning("No backend events provided for parsing.")
            return events

        # Dynamic import of event mappings to avoid circular imports
        try:
            from autoppia_iwa.src.demo_webs.projects.cinema_1.events import BACKEND_EVENT_TYPES as web_1_backend_types
            from autoppia_iwa.src.demo_webs.projects.personal_management_2.events import BACKEND_EVENT_TYPES as personal_management_2_backend_types
        except ImportError as e:
            logger.error(f"Error importing event type mappings: {e}")
            web_1_backend_types = {}
            personal_management_2_backend_types = {}

        event_class_map = {**web_1_backend_types, **personal_management_2_backend_types}

        for event_data in backend_events:
            try:
                event_class = event_class_map.get(event_data.event_name, Event)
                events.append(event_class.parse(event_data))
            except ValidationError as ve:
                logger.error(f"Validation error for event {event_data.event_name}: {ve}")
                events.append(Event.parse(event_data))
            except Exception as e:
                logger.exception(f"Unexpected error parsing event {event_data.event_name}: {e}")
                continue

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
