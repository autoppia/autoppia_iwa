import sys

from loguru import logger

# Add custom EVALUATION level
EVALUATION_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
TASK_GENERATION_LEVEL_NUM = 23  # Between INFO and EVALUATION


def evaluation_level(record):
    """Custom level for evaluation logs"""
    return record["level"].no >= EVALUATION_LEVEL_NUM


# Add custom levels to loguru if they are not already registered.
try:
    logger.level("EVALUATION")
except ValueError:
    logger.level("EVALUATION", EVALUATION_LEVEL_NUM, color="<blue>")

try:
    logger.level("TASK_GENERATION")
except ValueError:
    logger.level("TASK_GENERATION", TASK_GENERATION_LEVEL_NUM, color="<magenta>")

# ==================================
# ======= LOGGING SETUP ============
# ==================================

_logging_initialized = False


def setup_logging(log_file: str, console_level: str = "INFO"):
    """Configure loguru logger with enhanced formatting.

    Args:
        log_file: Path to the log file.
        console_level: Console handler level (e.g. "INFO" or "DEBUG" for verbose).
    """
    global _logging_initialized
    logger.remove()

    # Uniform timestamp format (with milliseconds) for all logs
    time_fmt = "YYYY-MM-DD HH:mm:ss.SSS"

    # Console logging with colors and better formatting
    logger.add(
        sys.stderr,
        level=console_level,
        format=f"<green>{{time:{time_fmt}}}</green> | <level>{{level: <8}}</level> | <cyan>{{name}}</cyan>:<cyan>{{function}}</cyan>:<cyan>{{line}}</cyan> - <level>{{message}}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG", "EVALUATION"],
    )

    # File logging with more detail (same timestamp format)
    logger.add(
        log_file,
        level="DEBUG",
        format=f"{{time:{time_fmt}}} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,  # Thread-safe logging
    )

    # Log startup message only once per process (avoid duplicate when main + Benchmark both call setup_logging)
    if not _logging_initialized:
        _logging_initialized = True
        logger.info("Benchmark logging initialized")


# ==================================
# ======= EVALUATION LOGGERS ======
# ==================================


def get_evaluation_logger(context: str):
    """
    Get a logger with EVALUATION level and specific context.

    Args:
        context: One of "ACTION_EXECUTION", "GIF_CREATION", "GET_BACKEND_TEST"

    Returns:
        Logger with evaluation context
    """
    return logger.bind(evaluation_context=context)


def log_action_execution(message: str):
    """Log action execution with INFO level"""
    logger.info(f"[EVALUATION] [ACTION EXECUTION] {message}")


def log_evaluation_event(message: str, context: str = "GENERAL"):
    """Log generic evaluation events with INFO level"""
    if context == "GENERAL":
        logger.info(f"[EVALUATION] {message}")
    else:
        logger.info(f"[EVALUATION] [{context}] {message}")


def get_task_generation_logger(context: str):
    """
    Get a logger with TASK_GENERATION level and specific context.
    """
    return logger.bind(task_generation_context=context)


def log_task_generation_event(message: str, context: str = "TASK_GENERATION"):
    """Log task generation events with INFO level"""
    if context == "TASK_GENERATION":
        logger.info(f"[TASK_GENERATION] {message}")
    else:
        logger.info(f"[TASK_GENERATION] [{context}] {message}")


def log_gif_creation(message: str):
    """Log GIF creation with INFO level"""
    logger.info(f"[EVALUATION] [GIF CREATION] {message}")


def log_backend_test(message: str):
    """Log backend test with INFO level"""
    logger.info(f"[EVALUATION] [GET BACKEND TEST] {message}")


# ==================================
# ======= STRUCTURED BENCHMARK LOGS =
# ==================================


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
