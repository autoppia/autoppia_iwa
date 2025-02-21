import json
import logging
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO, handlers=[logging.StreamHandler()])


def load_jsonl_file(file_path: Path) -> List[Dict]:
    """Load tasks from a JSONL file."""
    if not file_path.exists():
        logging.warning(f"File {file_path} not found.")
        return []

    tasks = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError as e:
                logging.warning(f"Skipping invalid JSON line in {file_path}: {e}")
    return tasks
