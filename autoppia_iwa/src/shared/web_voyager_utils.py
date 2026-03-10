import hashlib
import json
import logging
import uuid
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


def load_real_tasks(num_of_urls: int = 0, task: dict | None = None, by_indices: list | None = None) -> list[TaskData]:
    """Load real tasks, excluding impossible ones."""

    if task.get("url") and task.get("prompt"):
        unique_id = str(uuid.uuid4())
        unique_name = f"custom_web_{unique_id[:8]}"
        return [TaskData(web=task["url"], ques=task["prompt"], id=unique_id, web_name=unique_name)]

    if not num_of_urls and not by_indices:
        raise ValueError("Either num_of_urls or by_indices must be provided and non-zero.")

    # Prefer dataset colocated with judge_benchmark; fallback to global data directory
    primary_dir = PROJECT_BASE_DIR / "entrypoints" / "judge_benchmark" / "web_voyager_tasks"
    fallback_dir = PROJECT_BASE_DIR.parent / "data" / "web_voyager_tasks"

    print("Loading real tasks...")
    dataset_dir = primary_dir if (primary_dir / "web_voyager_data.jsonl").exists() else fallback_dir

    original_tasks = load_jsonl_file(dataset_dir / "web_voyager_data.jsonl")
    impossible_raw = load_jsonl_file(dataset_dir / "web_voyager_impossible_tasks.json")
    try:
        impossible_tasks_ids = set(impossible_raw)
    except TypeError:
        # If file contains list of dicts or invalid content, ignore gracefully
        impossible_tasks_ids = set()
    if by_indices:
        return [TaskData(**original_tasks[i]) for i in by_indices if i < len(original_tasks) and original_tasks[i]["id"] not in impossible_tasks_ids]
    return [TaskData(**task) for task in original_tasks if task.get("id") not in impossible_tasks_ids][:num_of_urls]


def generate_hash(input_string: str) -> str:
    """Generate a SHA-256 hash of the input string."""
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()
