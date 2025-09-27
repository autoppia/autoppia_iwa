import sys

from loguru import logger

# ==================================
# ======= LOGGING SETUP ============
# ==================================


def setup_logging(log_file: str):
    """Configure loguru logger with enhanced formatting"""
    logger.remove()

    # Console logging with colors
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # File logging
    logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}", rotation="10 MB", retention="7 days")
