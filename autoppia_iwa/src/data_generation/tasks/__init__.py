"""
Task generation pipelines and data models.
"""

from autoppia_iwa.src.data_generation.tasks.classes import (
    BrowserSpecification,
    Task,
    TaskGenerationConfig,
)
try:  # pragma: no cover - optional dependency guard
    from autoppia_iwa.src.data_generation.tasks.pipeline import TaskGenerationPipeline
except ModuleNotFoundError:  # pragma: no cover
    TaskGenerationPipeline = None

__all__ = [
    "BrowserSpecification",
    "Task",
    "TaskGenerationConfig",
    "TaskGenerationPipeline",
]
