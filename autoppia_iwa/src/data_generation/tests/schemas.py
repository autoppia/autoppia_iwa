from pydantic import BaseModel, Field


class ScreenshotTestResponse(BaseModel):
    """Represents the evaluation result for a screenshot-based test."""

    evaluation_result: bool = Field(..., description="Indicates whether the task execution was successful.")
    justification: str | None = Field(None, description="Optional explanation supporting the evaluation decision.")


class HTMLBasedTestResponse(BaseModel):
    """Represents the evaluation result for an HTML-based test."""

    evaluation_result: bool = Field(..., description="Indicates whether the task execution was successful.")
    justification: str | None = Field(None, description="Optional explanation supporting the evaluation decision.")
