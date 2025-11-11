#!/usr/bin/env python3
"""CLI to train MaskablePPO on the IWA environment."""

from __future__ import annotations

import argparse
from pathlib import Path

from autoppia_iwa.src.rl.agent.training import load_yaml, train_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("autoppia_iwa/src/rl/agent/configs/ppo_smoke.yaml"),
        help="YAML config describing env/train params.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_yaml(args.config)
    train_agent(cfg)


if __name__ == "__main__":
    main()
