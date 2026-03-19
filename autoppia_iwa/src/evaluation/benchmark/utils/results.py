import json
import os
from datetime import datetime
from typing import Any

from autoppia_iwa.src.evaluation.benchmark.reporting import (
    build_legacy_performance_report,
    build_legacy_results_payload,
    has_zero_score,
)

from .metrics import TimingMetrics


def save_results_to_json(results, agents, timing_metrics: TimingMetrics, output_dir: str) -> dict[str, str | float | dict[Any, Any]]:
    """
    Save comprehensive results to a JSON file and return the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "r-" if has_zero_score(results) else ""
    filename = os.path.join(output_dir, f"{prefix}benchmark_results_{timestamp}.json")
    output_data = build_legacy_results_payload(results, agents, timing_metrics)

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nDetailed results saved to '{filename}'")
    return output_data


def print_performance_statistics(results, agents, timing_metrics: TimingMetrics):
    """
    Print performance stats (scores, timings) for each agent.
    """
    print(build_legacy_performance_report(results, agents, timing_metrics))


def _has_zero_score(results: dict) -> bool:
    return has_zero_score(results)
