import asyncio
import inspect
import json
import re
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from hashlib import sha1
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.actions.base import BaseAction

# Constants
CONSTRAINTS_INFO_PLACEHOLDER = "<constraints_info>"


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
    # When constraint generator returns a dict with "question_fields_and_values", used for LLM prompt (entity identifier).
    question_fields_and_values: dict[str, Any] | None = Field(default=None, exclude=True)

    # ============================================================================
    # TEXT REPLACEMENT
    # ============================================================================

    def apply_replacements(self, text: str, *args, **kwargs) -> str:
        if self.replace_func and isinstance(text, str):
            kwargs_for_replace = {**kwargs}
            if "constraints" in inspect.signature(self.replace_func).parameters:
                kwargs_for_replace["constraints"] = self.constraints
            result = self.replace_func(text, *args, **kwargs_for_replace)
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
        if isinstance(text, str) and CONSTRAINTS_INFO_PLACEHOLDER in text and self.constraints:
            text = text.replace(CONSTRAINTS_INFO_PLACEHOLDER, self.constraints_to_str())

        return text

    async def apply_replacements_async(self, text: str, *args, **kwargs) -> str:
        """Async version that awaits async replace functions when provided."""
        if self.replace_func and isinstance(text, str):
            kwargs_for_replace = {**kwargs}
            if "constraints" in inspect.signature(self.replace_func).parameters:
                kwargs_for_replace["constraints"] = self.constraints
            result = self.replace_func(text, *args, **kwargs_for_replace)
            if asyncio.iscoroutine(result):
                return await result
            return result

        # Also replace constraints_info if needed
        if isinstance(text, str) and CONSTRAINTS_INFO_PLACEHOLDER in text and self.constraints:
            text = text.replace(CONSTRAINTS_INFO_PLACEHOLDER, self.constraints_to_str())

        return text

    # ============================================================================
    # CONSTRAINTS GENERATION
    # ============================================================================

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

    async def generate_constraints_async(
        self,
        task_url: str | None = None,
        dataset: dict[str, list[dict]] | None = None,
        test_types: str | None = None,
    ):
        """
        Async version that awaits async constraints generators when provided.

        Args:
            task_url: Optional task URL to pass to the generator (for seed extraction, etc.)
            dataset: Dataset dictionary with all entities (e.g., {"films": [...], "users": [...]})
                    to pass to the generator. Each constraint generator receives the full dataset
                    and extracts the relevant entity list it needs.
            test_types: Optional test type ("event_only" or "data_extraction_only") for
                    generators that branch on data-extraction mode.
        """
        self.question_fields_and_values = None
        if self.constraints_generator:
            # Inspect the generator function signature to see what parameters it accepts
            sig = inspect.signature(self.constraints_generator)
            params = sig.parameters

            # Check if function accepts task_url and dataset parameters
            has_task_url_param = "task_url" in params
            has_dataset_param = "dataset" in params
            has_test_types_param = "test_types" in params

            # Check if first parameter (excluding self) might be dataset
            param_names = [p for p in params if p != "self"]
            first_param_is_dataset = False
            if param_names:
                first_param = params[param_names[0]]
                # If first param has no default and might be dataset (positional)
                if first_param.default is inspect.Parameter.empty and len(param_names) == 1:
                    first_param_is_dataset = True

            # Build kwargs based on what the function accepts
            kwargs = {}
            if has_task_url_param:
                kwargs["task_url"] = task_url
            if has_dataset_param:
                kwargs["dataset"] = dataset
            if has_test_types_param and test_types is not None:
                kwargs["test_types"] = test_types

            # Call generator with appropriate parameters
            if kwargs:
                result = self.constraints_generator(**kwargs)
            elif first_param_is_dataset:
                # First positional parameter is likely dataset
                result = self.constraints_generator(dataset)
            else:
                # Function doesn't accept dataset or task_url, call without arguments
                result = self.constraints_generator()

            if asyncio.iscoroutine(result):
                result = await result

            # Generator may return a dict for data-extraction mode: {"constraints": [...], "question_fields_and_values": {...}}
            if isinstance(result, dict):
                self.constraints = result.get("constraints")
                self.question_fields_and_values = result.get("question_fields_and_values")
            else:
                self.constraints = result
        return self.constraints_to_str() if self.constraints else ""

    # ============================================================================
    # CONSTRAINTS FORMATTING
    # ============================================================================

    def constraints_to_str(self) -> str:
        """
        Converts the constraints list to a human-readable string.
        Example: "1) year equals 2014 AND 2) genres contains Sci-Fi"
        """
        if not self.constraints:
            return ""

        # Mapping to natural language for better prompt generation
        op_map = {
            "equals": "equals",
            "not_equals": "not equals",
            "contains": "contains",
            "not_contains": "not contains",
            "greater_than": "greater than",
            "less_than": "less than",
            "greater_equal": "greater equal",
            "less_equal": "less equal",
            "in_list": "is one of",
            "not_in_list": "is not one of",
        }

        parts = []
        for idx, constraint in enumerate(self.constraints, start=1):
            field = constraint["field"]
            op = constraint["operator"]
            value = constraint["value"]

            # Use natural language if available, otherwise use raw value
            op_str = op.value if hasattr(op, "value") else str(op)
            op_label = op_map.get(op_str, op_str)

            # Special formatting for lists
            value_str = f"[{', '.join(map(str, value))}]" if isinstance(value, list) else str(value)

            parts.append(f"{idx}) {field} {op_label} {value_str}")

        return " AND ".join(parts)

    # ============================================================================
    # EXAMPLES
    # ============================================================================

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

    # ============================================================================
    # SERIALIZATION
    # ============================================================================

    def serialize(self) -> dict:
        """Serialize a UseCase object to a dictionary."""
        from autoppia_iwa.src.data_generation.tests.simple.utils import enum_to_raw_recursive

        serialized = self.model_dump()
        serialized["event"] = self.event.__name__
        if "event_source_code" in serialized:
            serialized["event_source_code"] = True
        # Explicitly ensure constraints are included (they're needed for validation)
        # Convert ComparisonOperator enums to strings for JSON serialization
        if self.constraints is not None:
            serialized["constraints"] = enum_to_raw_recursive(self.constraints)
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
    data_extraction_use_cases: list[str] | None = Field(default=None, description="Optional list of dedicated data-extraction use case names for DE task generation.")


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


@dataclass
class DataExtractionTrajectory:
    """
    Deterministic data-extraction flow bound to a fixed seed and expected answer.
    Kept separate from event-based ``Trajectory`` so legacy flows remain unchanged.
    """

    web_project_id: str
    seed: int
    use_case: str | None
    question: str
    expected_answer: str | list[str]
    actions: list[BaseAction] | None
    id: str | None = None

    def __post_init__(self) -> None:
        if not self.id:
            self.id = self._build_auto_id()

    @staticmethod
    def _to_step_tool_call(action: BaseAction) -> dict[str, Any]:
        tool_call = action.to_tool_call()
        name = str(tool_call.get("name") or "").strip()
        arguments = dict(tool_call.get("arguments") or {})
        if name.startswith("browser.") or name.startswith("user."):
            return {"name": name, "arguments": arguments}
        namespaced = "user.request_input" if name == "request_user_input" else f"browser.{name}"
        return {"name": namespaced, "arguments": arguments}

    @staticmethod
    def _slug(value: str | None) -> str:
        raw = str(value or "").strip().lower()
        slug = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
        return slug or "unknown"

    def _build_auto_id(self) -> str:
        payload = {
            "web_project_id": self.web_project_id,
            "seed": int(self.seed),
            "use_case": self.use_case,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "actions": [self._to_step_tool_call(action) for action in (self.actions or [])],
        }
        fingerprint = sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:10]
        return f"{self.web_project_id}.de.seed{self.seed}.{self._slug(self.use_case)}.{fingerprint}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "web_project_id": self.web_project_id,
            "seed": self.seed,
            "use_case": self.use_case,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "actions": [self._to_step_tool_call(action) for action in (self.actions or [])],
            "trajectory_type": "data_extraction",
        }

    def to_step_tool_calls_trajectory(self) -> dict[str, Any]:
        actions = self.actions or []
        url: str | None = None
        for action in actions:
            if isinstance(action, NavigateAction) and getattr(action, "url", None):
                url = action.url
                break

        tool_actions = [self._to_step_tool_call(x) for x in actions]
        return {
            "id": self.id,
            "web_project_id": self.web_project_id,
            "seed": self.seed,
            "use_case": self.use_case,
            "url": url,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "actions": tool_actions,
            "has_success": bool(tool_actions),
            "action_format": "step_tool_calls",
            "trajectory_type": "data_extraction",
        }
