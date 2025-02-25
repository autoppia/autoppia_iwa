from typing import Any, Dict
from pydantic import BaseModel, Field


class TestEvaluationResult(BaseModel):
    """
    Model for LLM response when evaluating a specific test type for a task
    """
    applicable: bool = Field(
        ..., 
        description="Whether this test type is applicable for the task"
    )
    reason: str = Field(
        ..., 
        description="Explanation for why this test is or is not applicable"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="If applicable=true, the parameters to use when creating the test instance"
    )
