"""Backward-compatible benchmark logging exports."""

from autoppia_iwa.src.evaluation.benchmark.utils.logging import (
    evaluation_level,
    get_evaluation_logger,
    get_task_generation_logger,
    log_action_execution,
    log_backend_test,
    log_evaluation_event,
    log_gif_creation,
    log_task_generation_event,
    setup_logging,
)

__all__ = [
    "evaluation_level",
    "get_evaluation_logger",
    "get_task_generation_logger",
    "log_action_execution",
    "log_backend_test",
    "log_evaluation_event",
    "log_gif_creation",
    "log_task_generation_event",
    "setup_logging",
]
