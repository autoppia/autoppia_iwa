import sys

from loguru import logger

# Add custom EVALUATION level
EVALUATION_LEVEL_NUM = 25  # Between INFO (20) and WARNING (30)
TASK_GENERATION_LEVEL_NUM = 23  # Between INFO and EVALUATION


def evaluation_level(record):
    """Custom level for evaluation logs"""
    return record["level"].no >= EVALUATION_LEVEL_NUM


# Add the custom level to loguru
logger.level("EVALUATION", EVALUATION_LEVEL_NUM, color="<blue>")
logger.level("TASK_GENERATION", TASK_GENERATION_LEVEL_NUM, color="<magenta>")

# ==================================
# ======= LOGGING SETUP ============
# ==================================


def setup_logging(log_file: str):
    """Configure loguru logger with enhanced formatting"""
    logger.remove()

    # Console logging with colors and better formatting
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG", "EVALUATION"],
    )

    # File logging with more detail
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=True,  # Thread-safe logging
    )

    # Log startup message
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
