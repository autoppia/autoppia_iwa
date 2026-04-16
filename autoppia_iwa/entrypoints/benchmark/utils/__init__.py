"""Backward-compatible benchmark utils facade."""

from autoppia_iwa.src.evaluation.benchmark.utils import (
    TimingMetrics,
    compute_statistics,
    get_projects_by_ids,
    save_results_to_json,
    setup_logging,
)

__all__ = [
    "TimingMetrics",
    "compute_statistics",
    "get_projects_by_ids",
    "save_results_to_json",
    "setup_logging",
]
