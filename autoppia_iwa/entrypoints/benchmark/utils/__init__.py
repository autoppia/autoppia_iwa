"""Backward-compatible benchmark utils facade."""

from autoppia_iwa.entrypoints.benchmark.utils.logging import setup_logging
from autoppia_iwa.entrypoints.benchmark.utils.metrics import TimingMetrics, compute_statistics
from autoppia_iwa.entrypoints.benchmark.utils.results import save_results_to_json
from autoppia_iwa.entrypoints.benchmark.utils.task_generation import get_projects_by_ids

__all__ = [
    "TimingMetrics",
    "compute_statistics",
    "get_projects_by_ids",
    "save_results_to_json",
    "setup_logging",
]
