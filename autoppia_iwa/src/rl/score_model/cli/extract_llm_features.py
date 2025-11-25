#!/usr/bin/env python3
"""CLI entrypoint to build observations and LLM labels from evaluation dumps."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..datasets.build_from_evaluations import build_obs_and_labels
from ..utils import config_path


def main(argv: list[str] | None = None) -> None:
    default_config = config_path("llm_labeler.yaml")

    parser = argparse.ArgumentParser(description="Extract observations and LLM labels")
    parser.add_argument(
        "--config",
        type=Path,
        default=default_config,
        help="Path to LLM labeler YAML config",
    )
    parser.add_argument(
        "--inputs",
        "-i",
        nargs="+",
        help=(
            "Optional list of evaluation files or glob patterns to ingest. "
            "Defaults to all JSONL files under data/rm/raw_evaluations/."
        ),
    )
    args = parser.parse_args(argv)
    _ = build_obs_and_labels(args.config, args.inputs)


if __name__ == "__main__":
    main()
