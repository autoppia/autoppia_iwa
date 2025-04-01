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

    # Only one field for constraints - the structured data
    constraints: list[dict[str, Any]] | None = Field(default=None)
    constraints_generator: Callable | None = Field(default=None, exclude=True)
    additional_prompt_info: str | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def apply_replacements(self, text: str, *args, **kwargs) -> str:
        if self.replace_func and isinstance(text, str):
            return self.replace_func(text, *args, **kwargs)

        # Also replace constraints_info if needed
        if isinstance(text, str) and "<constraints_info>" in text and self.constraints:
            text = text.replace("<constraints_info>", self.constraints_to_str())

        return text

    def generate_constraints(self):
        """
        Generates constraints using the specific generator for this use case.
        """
        if self.constraints_generator:
            self.constraints = self.constraints_generator()
        return self.constraints_to_str() if self.constraints else ""

    def constraints_to_str(self) -> str:
        """
        Converts the constraints list to a human-readable string.
        Example: "1) year equals 2014 AND 2) genres contains Sci-Fi"
        """
        if not self.constraints:
            return ""

        parts = []
        for idx, constraint in enumerate(self.constraints, start=1):
            field = constraint["field"]
            op = constraint["operator"]
            value = constraint["value"]

            # Special formatting for lists
            value_str = f"[{', '.join(map(str, value))}]" if isinstance(value, list) else str(value)

            parts.append(f"{idx}) {field} {op.value} {value_str}")

        return " AND ".join(parts)

    def add_constraints(self, constraints: list[dict[str, Any]]) -> None:
        """
        Adds constraints to the use case and an example that uses these constraints
        """
        self.constraints = constraints

        # Create an example that uses the constraints
        if constraints:
            # Get the string representation of constraints
            constraints_str = self.constraints_to_str()

            # Create a generic constraint example
            prompt = f"Show me items with these criteria: {constraints_str}"
            prompt_template = "Show me items with these criteria: <constraints_info>"

            constraint_example = {
                "prompt": prompt,
                "prompt_for_task_generation": prompt_template,
                "test": {
                    "type": "CheckEventTest",
                    "event_name": self.event.__name__,
                    "event_criteria": {c["field"]: {"value": c["value"], "operator": c["operator"]} for c in constraints},
                    "reasoning": "Validates that constraints are correctly processed and used for filtering.",
                },
            }

            self.examples.append(constraint_example)

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
