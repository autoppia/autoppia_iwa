#!/usr/bin/env python3
"""CLI shim for semantic encoder training."""

from __future__ import annotations

import argparse
from pathlib import Path

from autoppia_rm.training.train_semantic_encoder import main as train_main
from autoppia_rm.utils import config_path as get_config_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train semantic encoder")
    parser.add_argument(
        "--config",
        type=Path,
        default=get_config_path("semantic_encoder.yaml"),
        help="Path to YAML config",
    )
    args = parser.parse_args(argv)
    train_main(args.config)


if __name__ == "__main__":
    main()
