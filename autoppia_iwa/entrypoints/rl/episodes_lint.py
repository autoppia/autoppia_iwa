from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


def summarize_episodes(pattern: str) -> dict:
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No episode files match {pattern}")

    steps = 0
    null_actions = 0
    successes = invalids = loops = 0
    mask_len = None
    act_hist = Counter()

    for file_path in files:
        with Path(file_path).open() as handle:
            for line in handle:
                row = json.loads(line)
                steps += 1
                action = row.get("action")
                if action is None:
                    null_actions += 1
                else:
                    act_hist[action] += 1
                info = row.get("info", {}) or {}
                if info.get("success"):
                    successes += 1
                if info.get("invalid_action"):
                    invalids += 1
                if any(m == "loop_penalty" for m in info.get("milestones", []) or []):
                    loops += 1
                mask = row.get("mask")
                if mask is not None:
                    mask_len = mask_len or len(mask)
                    if len(mask) != mask_len:
                        raise AssertionError(f"Inconsistent mask length in {file_path}")

    return {
        "files": len(files),
        "steps": steps,
        "null_actions": null_actions,
        "success_steps": successes,
        "invalid_actions": invalids,
        "loop_penalties": loops,
        "mask_length": mask_len,
        "action_histogram": act_hist,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint RL episode JSONL dumps.")
    parser.add_argument(
        "--pattern",
        default="data/rl_episodes/*.jsonl",
        help="Glob for episode files (default: data/rl_episodes/*.jsonl)",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    stats = summarize_episodes(args.pattern)

    total_steps = max(stats["steps"], 1)
    null_pct = 100 * stats["null_actions"] / total_steps

    print(f"Files: {stats['files']}")
    print(f"Total steps: {stats['steps']}")
    print(f"Null-action steps: {stats['null_actions']} ({null_pct:.1f}%)")
    print(
        f"Any-success steps: {stats['success_steps']}, "
        f"invalid action flags: {stats['invalid_actions']}, "
        f"loop penalties: {stats['loop_penalties']}"
    )
    print(f"Mask length: {stats['mask_length']}")
    print(f"Top actions (by count): {stats['action_histogram'].most_common(10)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
