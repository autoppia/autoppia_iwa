"""Backward-compatible benchmark task generation exports."""

from autoppia_iwa.src.evaluation.benchmark.utils.task_generation import (
    generate_tasks_for_project,
    get_cache_filename,
    get_projects_by_ids,
    load_tasks_from_json,
    save_tasks_to_json,
)

__all__ = [
    "generate_tasks_for_project",
    "get_cache_filename",
    "get_projects_by_ids",
    "load_tasks_from_json",
    "save_tasks_to_json",
]
