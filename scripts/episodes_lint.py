import glob
import json
from collections import Counter


def main(pattern: str = "data/rl_episodes/*.jsonl"):
    files = glob.glob(pattern)
    assert files, f"No episode files match {pattern}"
    steps = 0
    null_actions = 0
    succ = invalids = loops = 0
    mask_len = None
    act_hist = Counter()
    for p in files:
        with open(p) as f:
            for line in f:
                row = json.loads(line)
                steps += 1
                a = row.get("action")
                if a is None:
                    null_actions += 1
                else:
                    act_hist[a] += 1
                info = row.get("info", {}) or {}
                if info.get("success"):
                    succ += 1
                if info.get("invalid_action"):
                    invalids += 1
                if any(m == "loop_penalty" for m in info.get("milestones", []) or []):
                    loops += 1
                m = row.get("mask")
                if m is not None:
                    mask_len = mask_len or len(m)
                    if len(m) != mask_len:
                        raise AssertionError(f"Inconsistent mask length in {p}")
    print(f"Files: {len(files)}")
    print(f"Total steps: {steps}")
    print(f"Null-action steps: {null_actions} ({100*null_actions/max(steps,1):.1f}%)")
    print(f"Any-success steps: {succ}, invalid action flags: {invalids}, loop penalties: {loops}")
    print(f"Mask length: {mask_len}")
    print(f"Top actions (by count): {act_hist.most_common(10)}")


if __name__ == "__main__":
    main()

