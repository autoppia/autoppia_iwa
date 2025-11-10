#!/usr/bin/env python3
"""CLI entrypoint to build preference pairs from evaluation dumps."""

from __future__ import annotations

import argparse

from ..datasets.build_from_evaluations import build_preference_pairs


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build preference pairs from evaluation dumps")
    parser.add_argument(
        "--inputs",
        "-i",
        nargs="+",
        help=(
            "Optional list of evaluation files or glob patterns to ingest. "
            "Defaults to all JSONL files under data/rm/raw_evaluations/."
        ),
    )
    parser.add_argument(
        "--recent-steps",
        type=int,
        default=3,
        help="Number of trailing steps from each episode to consider when forming pairs",
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=50_000,
        help="Maximum number of preference pairs to generate",
    )
    args = parser.parse_args(argv)
    build_preference_pairs(args.recent_steps, args.max_pairs, args.inputs)


if __name__ == "__main__":
    main()
