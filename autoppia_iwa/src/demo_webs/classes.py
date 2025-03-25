from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


class UseCase(BaseModel):
    """Represents a use case in the application"""

    name: str
    description: str

    event: type[Event]
    event_source_code: str
    examples: list[dict]
    replace_func: Callable[[str], str] | None = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def apply_replacements(self, text: str, *args, **kwargs) -> str:
        if self.replace_func and isinstance(text, str):
            return self.replace_func(text, *args, **kwargs)
        return text

    def check_success(self, events: list[Any]) -> bool:
        """
        Check if the use case was successful based on the events that occurred
        """
        # Basic implementation - check if any event of the expected type exists
        return any(isinstance(event, self.event) for event in events)

    def get_example_prompts_from_use_case(self) -> list[str]:
        """
        Extract all prompt strings from the examples
        """
        return [example["prompt_for_task_generation"] for example in self.examples if "prompt_for_task_generation" in example]

    def get_example_prompts_str(self, separator="\n") -> str:
        """
        Get all example prompts as a single string with the specified separator
        """
        return separator.join(self.get_example_prompts_from_use_case())

    def serialize(self) -> dict:
        """Serialize a UseCase object to a dictionary."""
        serialized = self.model_dump()
        serialized["event"] = self.event.__name__
        if "event_source_code" in serialized:
            serialized["event_source_code"] = True
        return serialized

    @classmethod
    def deserialize(cls, data: dict) -> "UseCase":
        """Deserialize a dictionary to a UseCase object."""
        from autoppia_iwa.src.demo_webs.projects.base_events import EventRegistry

        event_class_name = data.get("event")

        try:
            if not event_class_name:
                raise ValueError("Event class name is missing in the data")

            event_class = EventRegistry.get_event_class(event_class_name)

            data["event"] = event_class
            if "event_source_code" in data:
                data["event_source_code"] = event_class.get_source_code_of_class()

            return cls(**data)
        except KeyError as e:
            raise ValueError(f"Event class '{event_class_name}' not found in the registry") from e
        except ValidationError as e:
            raise ValueError(f"Invalid data for UseCase deserialization: {e}") from e


class WebProject(BaseModel):
    id: str = Field(..., description="Unique identifier of the web project")
    name: str = Field(..., min_length=1, description="Name of the web project")
    backend_url: str = Field(..., description="URL of the backend server")
    frontend_url: str = Field(..., description="URL of the frontend application")
    is_web_real: bool = False
    urls: list[str] = []
    domain_analysis: DomainAnalysis | None = None
    events: list[type] = Field(default_factory=dict, description="Structured events information")
    relevant_data: dict[str, Any] = Field(default_factory=dict, description="Structured additional information about the web project")
    models: list[Any] = []
    use_cases: list[UseCase] = None


class BackendEvent(BaseModel):
    """
    Represents a validated event payload with application-specific constraints.
    Enforces proper event-application relationships and provides rich metadata.
    """

    event_name: str
    data: dict[str, Any] | None = None
    user_id: int | None = None
    web_agent_id: str | None = None
    timestamp: Any | None = None
