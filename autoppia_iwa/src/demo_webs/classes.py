import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class UseCase(BaseModel):
    """Represents a use case in the application"""

    model_config = {"arbitrary_types_allowed": True}

    name: str
    description: str

    event: Any = Field(..., description="Event class (type[Event])")
    event_source_code: str
    examples: list[dict]
    replace_func: Callable | Coroutine | None = Field(default=None, exclude=True)

    # Only one field for constraints - the structured data
    constraints: list[dict[str, Any]] | None = Field(default=None)
    constraints_generator: Callable | None | bool = Field(
        default=None,
        exclude=True,
        description="An optional callable function that dynamically generates a list of constraint dictionaries. "
        "Default to 'None'. Set 'False' when no dynamic constraints are needed and hence no events_criteria in CheckEventTest is generated.",
    )
    additional_prompt_info: str | None = Field(default=None)

    def apply_replacements(self, text: str, *args, **kwargs) -> str:
        if self.replace_func and isinstance(text, str):
            result = self.replace_func(text, *args, **kwargs)
            # Support both sync and async replace functions
            if asyncio.iscoroutine(result):
                # If called in sync context, run to completion
                try:
                    return asyncio.run(result)
                except RuntimeError:
                    # Fallback: cannot run new loop in running loop; skip async here
                    return text
            return result

        # Also replace constraints_info if needed
        if isinstance(text, str) and "<constraints_info>" in text and self.constraints:
            text = text.replace("<constraints_info>", self.constraints_to_str())

        return text

    async def apply_replacements_async(self, text: str, *args, **kwargs) -> str:
        """Async version that awaits async replace functions when provided."""
        if self.replace_func and isinstance(text, str):
            result = self.replace_func(text, *args, **kwargs)
            if asyncio.iscoroutine(result):
                return await result
            return result

        # Also replace constraints_info if needed
        if isinstance(text, str) and "<constraints_info>" in text and self.constraints:
            text = text.replace("<constraints_info>", self.constraints_to_str())

        return text

    def generate_constraints(self):
        """
        Generates constraints using the specific generator for this use case.
        """
        if self.constraints_generator:
            result = self.constraints_generator()
            # Support both sync and async generators
            if asyncio.iscoroutine(result):
                # If called in sync context, run to completion
                try:
                    self.constraints = asyncio.run(result)
                except RuntimeError:
                    # Fallback: cannot run new loop in running loop; skip async here
                    self.constraints = None
            else:
                self.constraints = result
        return self.constraints_to_str() if self.constraints else ""

    async def generate_constraints_async(self, task_url: str | None = None, dataset: list[dict] | None = None):
        """
        Async version that awaits async constraints generators when provided.

        Args:
            task_url: Optional task URL to extract seed values from
            dataset: Optional pre-loaded dataset to pass to generators (avoids redundant API calls)
        """
        if self.constraints_generator:
            # If constraints_generator accepts parameters, pass them
            import inspect

            sig = inspect.signature(self.constraints_generator)

            # Build kwargs dynamically based on what the generator accepts
            kwargs = {}
            if "task_url" in sig.parameters:
                kwargs["task_url"] = task_url
            if "dataset" in sig.parameters:
                kwargs["dataset"] = dataset

            # Call generator with appropriate parameters
            result = self.constraints_generator(**kwargs) if kwargs else self.constraints_generator()

            if asyncio.iscoroutine(result):
                self.constraints = await result
            else:
                self.constraints = result
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
    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": False,
        "from_attributes": True,
    }

    id: str = Field(..., description="Unique identifier of the web project")
    name: str = Field(..., min_length=1, description="Name of the web project")
    backend_url: str = Field(..., description="URL of the backend server")
    frontend_url: str = Field(..., description="URL of the frontend application")
    is_web_real: bool = False
    sandbox_mode: bool = Field(default=False, description="True if the project must run in sandbox mode")
    version: str | None = Field(default=None, description="Version of the web project (e.g., from package.json)")
    urls: list[str] = []
    events: list[type] = Field(default_factory=list, description="Structured events information")
    use_cases: list[UseCase] | None = Field(default=None, description="Optional list of canonical use cases for this project")
    relevant_data: dict[str, Any] = Field(default_factory=dict, description="Structured additional information about the web project")


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
