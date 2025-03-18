import hashlib
import json
import logging
from pathlib import Path

from pydantic import BaseModel

from autoppia_iwa.config.config import PROJECT_BASE_DIR


class TaskData(BaseModel):
    """Data model for tasks."""

    id: str
    web: str
    ques: str
    web_name: str


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO, handlers=[logging.StreamHandler()])


def load_jsonl_file(file_path: Path) -> list[dict]:
    """Load tasks from a JSONL file."""
    if not file_path.exists():
        logging.warning(f"File {file_path} not found.")
        return []

    tasks = []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            if file_path.suffix == ".json":
                return json.load(f)
            elif file_path.suffix == ".jsonl":
                for line in f:
                    try:
                        tasks.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logging.warning(f"Skipping invalid JSON line in {file_path}: {e}")
            else:
                logging.warning(f"Unsupported file format: {file_path.suffix}. Expected .json or .jsonl.")
                return []
    except Exception as e:
        logging.error(f"Failed to read or parse {file_path}: {e}")
        return []

    return tasks


def load_real_tasks(num_of_urls: int) -> list[TaskData]:
    """Load real tasks, excluding impossible ones."""
    data_dir = PROJECT_BASE_DIR.parent / "data"
    print("Loading real tasks...")
    original_tasks = load_jsonl_file(data_dir / "web_voyager_tasks/web_voyager_data.jsonl")
    impossible_tasks_ids = set(load_jsonl_file(data_dir / "web_voyager_tasks/web_voyager_impossible_tasks.json"))
    return [TaskData(**task) for task in original_tasks if task["id"] not in impossible_tasks_ids][:num_of_urls]


def generate_hash(input_string: str) -> str:
    """Generate a SHA-256 hash of the input string."""
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()
