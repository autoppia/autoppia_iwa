from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from autoppia_iwa.src.shared.web_voyager_utils import load_jsonl_file

# Constants
SRC_PATH = Path("autoppia_iwa/judge_tests_usage_logs.jsonl")


def calculate_metrics_by_test_type(data: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """
    Calculates metrics grouped by test type and final test result.

    Args:
        data (List[Dict[str, Any]]): List of parsed JSON objects.

    Returns:
        Dict[str, Dict[str, float]]: Dictionary containing metrics grouped by test type and final test result.
    """
    metrics_by_test_type = {}

    for item in data:
        test_type = item.get("test_type", "Unknown")
        final_result = item.get("final_test_result", False)

        if test_type not in metrics_by_test_type:
            metrics_by_test_type[test_type] = {
                "total_tasks": 0,
                "total_cost": 0.0,
                "total_duration": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
            }

        metrics = metrics_by_test_type[test_type]
        metrics["total_tasks"] += 1
        metrics["total_cost"] += item.get("total_cost", 0.0)
        metrics["total_duration"] += item.get("duration_seconds", 0.0)
        metrics["total_input_tokens"] += item.get("input_tokens", 0)
        metrics["total_output_tokens"] += item.get("output_tokens", 0)

        if final_result:
            metrics["successful_tasks"] += 1
        else:
            metrics["failed_tasks"] += 1

    # Calculate averages for each test type
    for _, metrics in metrics_by_test_type.items():
        total_tasks = metrics["total_tasks"]
        metrics["avg_cost"] = metrics["total_cost"] / total_tasks if total_tasks > 0 else 0
        metrics["avg_duration"] = metrics["total_duration"] / total_tasks if total_tasks > 0 else 0
        metrics["avg_input_tokens"] = metrics["total_input_tokens"] / total_tasks if total_tasks > 0 else 0
        metrics["avg_output_tokens"] = metrics["total_output_tokens"] / total_tasks if total_tasks > 0 else 0

    return metrics_by_test_type


def display_metrics_by_test_type(metrics_by_test_type: dict[str, dict[str, float]]):
    """
    Displays metrics grouped by test type in a rich table.

    Args:
        metrics_by_test_type (Dict[str, Dict[str, float]]): Dictionary containing metrics grouped by test type.
    """
    console = Console()

    for test_type, metrics in metrics_by_test_type.items():
        table = Table(title=f"Metrics for Test Type: {test_type}", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", justify="left")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Tasks", f"{metrics['total_tasks']}")
        table.add_row("Successful Tasks", f"{metrics['successful_tasks']}")
        table.add_row("Failed Tasks", f"{metrics['failed_tasks']}")
        table.add_row("Total Cost ($)", f"{metrics['total_cost']:.6f}")
        table.add_row("Total Duration (s)", f"{metrics['total_duration']:.4f}")
        table.add_row("Total Input Tokens", f"{metrics['total_input_tokens']}")
        table.add_row("Total Output Tokens", f"{metrics['total_output_tokens']}")
        table.add_row("Average Cost ($)", f"{metrics['avg_cost']:.6f}")
        table.add_row("Average Duration (s)", f"{metrics['avg_duration']:.4f}")
        table.add_row("Average Input Tokens", f"{metrics['avg_input_tokens']:.2f}")
        table.add_row("Average Output Tokens", f"{metrics['avg_output_tokens']:.2f}")

        console.print(table)
        console.print("\n")  # Add spacing between tables


def main():
    """Main function to load data, calculate metrics, and display results."""
    data = load_jsonl_file(SRC_PATH)
    if not data:
        print("No valid data found in the file.")
        return

    metrics_by_test_type = calculate_metrics_by_test_type(data)
    display_metrics_by_test_type(metrics_by_test_type)


if __name__ == "__main__":
    main()
