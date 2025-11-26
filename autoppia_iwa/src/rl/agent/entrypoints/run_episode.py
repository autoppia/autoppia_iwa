#!/usr/bin/env python3
"""Roll out a single episode with a trained PPO policy for smoke testing."""

from __future__ import annotations

import argparse
from pathlib import Path

from autoppia_iwa.src.rl.agent.training import load_yaml, run_episode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", type=Path, required=True, help="Path to the saved PPO checkpoint.")
    parser.add_argument(
        "--env-config",
        type=Path,
        default=Path("autoppia_iwa/src/rl/agent/configs/ppo_smoke.yaml"),
        help="YAML file (env section) describing env overrides.",
    )
    parser.add_argument("--deterministic", action="store_true", help="Use deterministic policy during rollout.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_yaml(args.env_config)
    env_cfg = cfg.get("env", {})
    stats = run_episode(args.model_path, env_cfg=env_cfg, deterministic=args.deterministic)
    print("[run_episode] result:", stats)


if __name__ == "__main__":
    main()
