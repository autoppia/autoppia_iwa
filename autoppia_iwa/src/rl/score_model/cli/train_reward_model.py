#!/usr/bin/env python3
"""CLI shim for reward-model training."""

from __future__ import annotations

import argparse
from pathlib import Path

from ..training.train_reward_model import main as train_main
from ..utils import config_path as get_config_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train reward model")
    parser.add_argument(
        "--config",
        type=Path,
        default=get_config_path("rm_train.yaml"),
        help="Path to YAML config",
    )
    args = parser.parse_args(argv)
    train_main(args.config)


if __name__ == "__main__":
    main()
