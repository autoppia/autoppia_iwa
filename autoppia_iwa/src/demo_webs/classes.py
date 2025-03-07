from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field

from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


class UseCase(BaseModel):
    """Represents a use case in the application"""

    name: str
    description: str
    prompt_template: str
    prompt_examples: List[str]
    event: Type
    event_source_code: str
    examples: List[Tuple[str, dict]]

    def get_prompt(self, **kwargs) -> str:
        """
        Generate a concrete prompt by filling in the template
        with the provided arguments
        """
        return self.prompt_template.format(**kwargs)

    def check_success(self, events: List[Any]) -> bool:
        """
        Check if the use case was successful based on the events that occurred
        """
        # Basic implementation - check if any event of the expected type exists
        return any(isinstance(event, self.event) for event in events)


class WebProject(BaseModel):
    id: str = Field(..., description="Unique identifier of the web project")
    name: str = Field(..., min_length=1, description="Name of the web project")
    backend_url: str = Field(..., description="URL of the backend server")
    frontend_url: str = Field(..., description="URL of the frontend application")
    is_web_real: bool = False
    urls: List[str] = []
    domain_analysis: Optional[DomainAnalysis] = None
    events: List[Type] = Field(default_factory=dict, description="Structured events information")
    relevant_data: Dict[str, Any] = Field(default_factory=dict, description="Structured additional information about the web project")
    models: List[Any] = []
    use_cases: List[UseCase] = None
    random_generation_function: Callable[[Any], Any] = None


class BackendEvent(BaseModel):
    """
    Represents a validated event payload with application-specific constraints.
    Enforces proper event-application relationships and provides rich metadata.
    """

    event_name: str
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    created_at: datetime = datetime.now()

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump['created_at'] = self.created_at.isoformat()
        return base_dump
