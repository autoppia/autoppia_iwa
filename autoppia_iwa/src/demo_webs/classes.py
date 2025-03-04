from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from autoppia_iwa.src.web_analysis.domain.analysis_classes import DomainAnalysis


class WebProject(BaseModel):
    id: str = Field(..., description="Unique identifier of the web project")
    name: str = Field(..., min_length=1, description="Name of the web project")
    backend_url: str = Field(..., description="URL of the backend server")
    frontend_url: str = Field(..., description="URL of the frontend application")
    is_web_real: bool = False
    urls: List[str] = []
    domain_analysis: Optional[DomainAnalysis] = None
    events: Dict[str, Any] = Field(default_factory=dict, description="Structured events information")
    relevant_data: Dict[str, Any] = Field(default_factory=dict, description="Structured additional information about the web project")
    models: List[Any] = []
    use_cases:Dict[Any] = None
    random_generation_function: Callable[[Any], Any] = None


class BackendEvent(BaseModel):
    """
    Represents a validated event payload with application-specific constraints.
    Enforces proper event-application relationships and provides rich metadata.
    """

    event_type: str
    description: str
    data: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    created_at: datetime = datetime.now()

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        base_dump = super().model_dump(*args, **kwargs)
        base_dump['created_at'] = self.created_at.isoformat()
        return base_dump
