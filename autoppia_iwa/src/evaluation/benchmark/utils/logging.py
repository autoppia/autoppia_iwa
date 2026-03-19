from loguru import logger
from autoppia_iwa.src.shared.logging import log_event, setup_iwa_logging

def evaluation_level(record):
    """Custom level for evaluation logs"""
    return record["level"].name == "EVALUATION"

# ==================================
# ======= LOGGING SETUP ============
# ==================================

def setup_logging(log_file: str, console_level: str = "INFO"):
    """Benchmark wrapper around the shared IWA logger configuration."""
    setup_iwa_logging(log_file, console_level=console_level)


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
    log_event("EVALUATION", message, context="ACTION EXECUTION")


def log_evaluation_event(message: str, context: str = "GENERAL"):
    """Log generic evaluation events with INFO level"""
    log_event("EVALUATION", message, context=None if context == "GENERAL" else context)


def get_task_generation_logger(context: str):
    """
    Get a logger with TASK_GENERATION level and specific context.
    """
    return logger.bind(task_generation_context=context)


def log_task_generation_event(message: str, context: str = "TASK_GENERATION"):
    """Log task generation events with INFO level"""
    log_event("TASK_GENERATION", message, context=None if context == "TASK_GENERATION" else context)


def log_gif_creation(message: str):
    """Log GIF creation with INFO level"""
    log_event("EVALUATION", message, context="GIF CREATION")


def log_backend_test(message: str):
    """Log backend test with INFO level"""
    log_event("EVALUATION", message, context="GET BACKEND TEST")
