from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path

from loguru import logger

from ...phases.sandbox import (
    compute_project_metrics,
    compute_seed_variability,
    detect_agent_memorization,
    find_trivial_tasks,
    find_unresolved_tasks,
    load_dataset,
)


def _format_entry(entry) -> str:
    return f"{entry.project_id} | {entry.use_case} | task={entry.task_id} | seed={entry.seed}"


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze sandbox dataset gathered from production miners/agents.")
    parser.add_argument("dataset", type=Path, help="Path to JSON/JSONL dataset file.")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("data") / "sandbox_analysis_report.json",
        help="Path to write the aggregated report.",
    )
    parser.add_argument(
        "--success-threshold",
        type=float,
        default=0.99,
        help="Score treated as success (default 0.99).",
    )
    parser.add_argument("--sample", type=int, default=5, help="How many flagged entries to print per category.")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    entries = load_dataset(args.dataset)
    logger.info("Loaded %d dataset entries from %s", len(entries), args.dataset)

    projects = compute_project_metrics(entries, success_threshold=args.success_threshold)
    unresolved = find_unresolved_tasks(entries, success_threshold=args.success_threshold)
    trivial = find_trivial_tasks(entries, success_threshold=args.success_threshold)
    agent_diversity = detect_agent_memorization(entries)
    seed_variability = compute_seed_variability(entries, success_threshold=args.success_threshold)

    report_payload = {
        "overview": projects,
        "unresolved_tasks": [_format_entry(e) for e in unresolved],
        "trivial_tasks": [_format_entry(e) for e in trivial],
        "agent_diversity": agent_diversity,
        "seed_variability": [
            {
                "project_id": item.project_id,
                "basis": item.basis,
                "seed_success": item.seed_success,
                "variance": round(item.variance, 5),
                "flagged": item.variance < 0.02,
            }
            for item in seed_variability
        ],
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report_payload, indent=2))
    logger.info("Sandbox analysis report saved to %s", args.report)

    def _preview(title: str, rows: list[str]):
        if not rows:
            return
        print(f"\n=== {title} ===")
        for row in rows[: args.sample]:
            print(row)

    _preview("Unresolved tasks (0% success)", report_payload["unresolved_tasks"])
    _preview("Trivial tasks (near 100% success / <3 actions)", report_payload["trivial_tasks"])

    flagged_agents = [f"{agent} (diversity={details['diversity_ratio']})" for agent, details in agent_diversity.items() if details["flagged"]]
    _preview("Agents with low action diversity (possible memorization)", flagged_agents)

    flagged_seed = [f"{item['project_id']} | {item['basis']} | variance={item['variance']} seeds={item['seed_success']}" for item in report_payload["seed_variability"] if item["flagged"]]
    _preview("Low seed variability (dynamic suspicious)", flagged_seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
