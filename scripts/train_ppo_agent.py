#!/usr/bin/env python3
"""
Quick-start script for training PPO agent with Score Model.

Usage:
    # PPO only (no BC):
    python train_ppo_agent.py

    # PPO with BC warm-start:
    python train_ppo_agent.py --with-bc

    # Custom config:
    python train_ppo_agent.py --config path/to/config.yaml

    # Skip BC even if enabled in config:
    python train_ppo_agent.py --with-bc --skip-bc
"""

import argparse
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autoppia_iwa.src.rl.agent.entrypoints.train_ppo_with_score_model import main as train_main


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to training config YAML (default: ppo_with_score_model.yaml or ppo_with_bc.yaml if --with-bc)",
    )

    parser.add_argument(
        "--with-bc",
        action="store_true",
        help="Use BC warm-start (uses ppo_with_bc.yaml config by default)",
    )

    parser.add_argument(
        "--skip-bc",
        action="store_true",
        help="Skip BC warm-start even if enabled in config",
    )

    parser.add_argument(
        "--tensorboard-log",
        type=str,
        default="data/rl/tensorboard",
        help="TensorBoard log directory",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Determine config file
    if args.config:
        config_path = args.config
    elif args.with_bc:
        config_path = Path("autoppia_iwa/src/rl/agent/configs/ppo_with_bc.yaml")
    else:
        config_path = Path("autoppia_iwa/src/rl/agent/configs/ppo_with_score_model.yaml")

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        print("\nAvailable configs:")
        configs_dir = Path("autoppia_iwa/src/rl/agent/configs")
        if configs_dir.exists():
            for cfg in configs_dir.glob("*.yaml"):
                print(f"  - {cfg}")
        sys.exit(1)

    print("=" * 70)
    print("PPO TRAINING WITH SCORE MODEL")
    print("=" * 70)
    print(f"Config: {config_path}")
    print(f"BC warm-start: {'Yes' if args.with_bc else 'No'}")
    if args.skip_bc:
        print("BC will be skipped (--skip-bc flag)")
    print(f"TensorBoard: {args.tensorboard_log}")
    print("=" * 70)
    print()

    # Prepare sys.argv for train_main
    sys.argv = [
        "train_ppo_with_score_model.py",
        "--config",
        str(config_path),
        "--tensorboard-log",
        args.tensorboard_log,
    ]

    if args.skip_bc:
        sys.argv.append("--skip-bc")

    # Run training
    try:
        train_main()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nTraining failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
