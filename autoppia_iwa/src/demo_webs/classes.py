from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


class UseCase(BaseModel):
    """Represents a use case in the application"""

    name: str
    description: str

    event: Type
    event_source_code: str
    examples: List[Dict]
    replace_func: Optional[Callable[[str], str]] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def apply_replacements(self, text: str, *args, **kwargs) -> str:
        if self.replace_func and isinstance(text, str):
            return self.replace_func(text, *args, **kwargs)
        return text

    def check_success(self, events: List[Any]) -> bool:
        """
        Check if the use case was successful based on the events that occurred
        """
        # Basic implementation - check if any event of the expected type exists
        return any(isinstance(event, self.event) for event in events)

    def get_example_prompts_from_use_case(self) -> List[str]:
        """
        Extract all prompt strings from the examples
        """
        return [example["prompt"] for example in self.examples if "prompt" in example]

    def get_example_prompts_str(self, separator="\n") -> str:
        """
        Get all example prompts as a single string with the specified separator
        """
        return separator.join(self.get_example_prompts_from_use_case())


class WebProject(BaseModel):
    id: str = Field(..., description="Unique identifier of the web project")
    name: str = Field(..., min_length=1, description="Name of the web project")
    backend_url: str = Field(..., description="URL of the backend server")
    frontend_url: str = Field(..., description="URL of the frontend application")
    is_web_real: bool = False
    urls: List[str] = []
    domain_analysis: Optional[DomainAnalysis] = None
    events: List[Type] = Field(default_factory=dict, description="Structured events information")
    # events: List[Any] = Field(default_factory=dict, description="Structured events information")
    relevant_data: Dict[str, Any] = Field(default_factory=dict, description="Structured additional information about the web project")
    models: List[Any] = []
    use_cases: List[UseCase] = None


class BackendEvent(BaseModel):
    """
    Represents a validated event payload with application-specific constraints.
    Enforces proper event-application relationships and provides rich metadata.
    """

    event_name: str
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    web_agent_id: Optional[str] = None
    timestamp: Optional[Any] = None
