from typing import List, Optional

from pydantic import BaseModel, RootModel

###############################################################################
# Pydantic Schemas for LLM JSON responses
###############################################################################


class DraftTask(BaseModel):
    """Schema for the output of Phase 1 draft tasks."""

    prompt: str
    success_criteria: Optional[str] = None


class DraftTaskList(RootModel[List[DraftTask]]):
    """A container for a list of draft tasks."""

    # Access items via self.root (a List[DraftTask])


class FilterTask(BaseModel):
    """Schema for the output of Phase 2 filter tasks."""

    decision: str  # "keep" or "discard"
    prompt: str
    success_criteria: Optional[str] = None


class FilterTaskList(RootModel[List[FilterTask]]):
    """A container for a list of filtered tasks."""

    # Access items via self.root (a List[FilterTask])
