from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, RootModel


class ProposedTestDefinition(BaseModel):
    """
    Represents a single test definition returned by the LLM.
    'fields' may contain extra details (e.g., keywords, description, etc.).
    """
    test_type: str
    fields: Dict[str, Any] = Field(default_factory=dict)

    # Optional fields (top-level for clarity)
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    event_name: Optional[str] = None
    page_view_url: Optional[str] = None


class ProposedTestList(RootModel[List[ProposedTestDefinition]]):
    """
    A container for an array (root-level) of ProposedTestDefinition objects.
    Access items via `.root`.
    """
    pass


class FilterResponse(BaseModel):
    """
    Used if/when you have a separate LLM step that filters or explains decisions.
    {
    "filtering_decisions": [...],
    "valid_tests": [ {ProposedTestDefinition}, ... ]
    }
    """
    filtering_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    valid_tests: List[ProposedTestDefinition] = Field(default_factory=list)
