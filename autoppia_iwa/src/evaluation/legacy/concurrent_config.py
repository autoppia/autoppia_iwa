from pydantic import BaseModel, Field


class EvaluatorConfig(BaseModel):
    """Legacy concurrent-evaluator configuration."""

    task_delay_in_seconds: float = Field(default=0.1, gt=0)
    chunk_size: int = Field(default=20, gt=0)
    browser_timeout: float = Field(default=10000, gt=0)
    enable_grouping_tasks: bool = Field(default=True)
    normalize_scores: bool = Field(default=True)
    verbose_logging: bool = Field(default=False)
    debug_mode: bool = Field(default=False)
    should_record_gif: bool = Field(default=False, description="Record evaluation on browser executions.")
    max_consecutive_action_failures: int = Field(default=2, gt=0, description="Maximum consecutive action failures before marking task as failed. Default: 2")
    headless: bool | None = Field(default=None, description="Override browser headless. None = use EVALUATOR_HEADLESS env.")
