"""Compatibility layer for benchmark logging utilities.

Canonical benchmark logging helpers live in:
    autoppia_iwa.src.evaluation.benchmark.utils.logging
"""

from loguru import logger

from autoppia_iwa.src.evaluation.benchmark.utils import logging as canonical_logging

# Re-export canonical symbols with object identity preserved for legacy tests/imports.
evaluation_level = canonical_logging.evaluation_level
setup_logging = canonical_logging.setup_logging
get_evaluation_logger = canonical_logging.get_evaluation_logger
log_action_execution = canonical_logging.log_action_execution
log_evaluation_event = canonical_logging.log_evaluation_event
get_task_generation_logger = canonical_logging.get_task_generation_logger
log_task_generation_event = canonical_logging.log_task_generation_event
log_gif_creation = canonical_logging.log_gif_creation
log_backend_test = canonical_logging.log_backend_test


def _fmt(v: object) -> str:
    """Format value for structured log; None -> empty string."""
    if v is None:
        return ""
    return str(v)


def log_task_start(
    project_id: str,
    task_id: str,
    agent_id: str,
    run_index: int,
) -> None:
    """Emit a single parseable line for task evaluation start (key=value)."""
    try:
        project_id = _fmt(project_id) or "unknown"
        task_id = _fmt(task_id) or "unknown"
        agent_id = _fmt(agent_id) or "unknown"
        logger.info(f"event=task_start project={project_id} task_id={task_id} agent_id={agent_id} run_index={run_index}")
    except Exception:
        logger.warning("event=task_start error=format_failed")


def log_task_end(
    project_id: str,
    task_id: str,
    agent_id: str,
    run_index: int,
    score: float,
    solution_time_s: float,
    evaluation_time_s: float,
    cost_usd: float | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> None:
    """Emit a single parseable line for task evaluation end (key=value)."""
    try:
        project_id = _fmt(project_id) or "unknown"
        task_id = _fmt(task_id) or "unknown"
        agent_id = _fmt(agent_id) or "unknown"
        parts = [
            f"event=task_end project={project_id} task_id={task_id} agent_id={agent_id} run_index={run_index}",
            f"score={score}",
            f"solution_time_s={solution_time_s}",
            f"evaluation_time_s={evaluation_time_s}",
        ]
        if cost_usd is not None:
            parts.append(f"cost_usd={cost_usd}")
        if input_tokens is not None:
            parts.append(f"input_tokens={input_tokens}")
        if output_tokens is not None:
            parts.append(f"output_tokens={output_tokens}")
        logger.info(" ".join(parts))
    except Exception:
        logger.warning("event=task_end error=format_failed")


def log_step(agent_id: str, task_id: str, step_index: int, actions_count: int) -> None:
    """Emit a single parseable line for stateful step (key=value)."""
    try:
        agent_id = _fmt(agent_id) or "unknown"
        task_id = _fmt(task_id) or "unknown"
        logger.info(f"event=step agent_id={agent_id} task_id={task_id} step_index={step_index} actions_count={actions_count}")
    except Exception:
        logger.warning("event=step error=format_failed")


__all__ = [
    "evaluation_level",
    "get_evaluation_logger",
    "get_task_generation_logger",
    "log_action_execution",
    "log_backend_test",
    "log_evaluation_event",
    "log_gif_creation",
    "log_step",
    "log_task_end",
    "log_task_generation_event",
    "log_task_start",
    "setup_logging",
]
