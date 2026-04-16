"""Compatibility wrapper for canonical benchmark result utilities."""

from autoppia_iwa.src.evaluation.benchmark.utils.results import (
    _has_zero_score,
    print_performance_statistics,
    save_results_to_json,
)

__all__ = ["_has_zero_score", "print_performance_statistics", "save_results_to_json"]
