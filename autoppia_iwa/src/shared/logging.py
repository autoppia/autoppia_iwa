from __future__ import annotations

import sys
from contextlib import suppress
from pathlib import Path

from loguru import logger

EVALUATION_LEVEL_NUM = 25
TASK_GENERATION_LEVEL_NUM = 23


def _ensure_level(name: str, number: int, color: str) -> None:
    with suppress(ValueError):
        logger.level(name, number, color=color)


_ensure_level("EVALUATION", EVALUATION_LEVEL_NUM, "<blue>")
_ensure_level("TASK_GENERATION", TASK_GENERATION_LEVEL_NUM, "<magenta>")

_logging_initialized = False
_console_handler_id: int | None = None
_file_handler_id: int | None = None


def setup_iwa_logging(log_file: str, console_level: str = "INFO") -> None:
    """Configure console and file logging without wiping unrelated handlers."""
    global _logging_initialized, _console_handler_id, _file_handler_id

    time_fmt = "YYYY-MM-DD HH:mm:ss.SSS"
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if _console_handler_id is not None:
        with suppress(ValueError):
            logger.remove(_console_handler_id)
    if _file_handler_id is not None:
        with suppress(ValueError):
            logger.remove(_file_handler_id)

    _console_handler_id = logger.add(
        sys.stderr,
        level=console_level,
        format=f"<green>{{time:{time_fmt}}}</green> | <level>{{level: <8}}</level> | <cyan>{{name}}</cyan>:<cyan>{{function}}</cyan>:<cyan>{{line}}</cyan> - <level>{{message}}</level>",
        colorize=True,
        backtrace=False,
        diagnose=False,
        filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG", "EVALUATION", "TASK_GENERATION"],
    )

    _file_handler_id = logger.add(
        str(log_path),
        level="DEBUG",
        format=f"{{time:{time_fmt}}} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        enqueue=False,
    )

    if not _logging_initialized:
        _logging_initialized = True
        logger.info("IWA logging initialized")


def log_event(namespace: str, message: str, *, context: str | None = None, web_agent_id: str | None = None, level: str = "INFO") -> None:
    parts = [f"[{namespace}]"]
    if context:
        parts.append(f"[{context}]")
    if web_agent_id:
        parts.append(f"[agent={web_agent_id}]")
    logger.log(level, f"{' '.join(parts)} {message}")
