from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import defaultdict

from ..features.dom_event_features import episode_feature_row, step_feature_row


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract DOM+JS event features from raw trace JSONL files.")
    parser.add_argument("--traces-dir", type=Path, default=Path("data/rm/raw_traces"), help="Directory containing trace JSONL files")
    parser.add_argument("--output-dir", type=Path, default=Path("data/rm/features"), help="Where to store feature JSONL files")
    parser.add_argument("--split-dir", type=Path, default=Path("data/rm/splits"), help="Directory with train/val/test episode lists")
    parser.add_argument("--steps-file", type=str, default="dom_event_steps.jsonl", help="Filename for per-step features")
    parser.add_argument("--episodes-file", type=str, default="dom_event_episodes.jsonl", help="Filename for per-episode features")
    return parser.parse_args()


def iter_trace_files(base_dir: Path):
    if not base_dir.exists():
        return []
    return sorted(p for p in base_dir.rglob("*.jsonl") if p.is_file())


def load_trace(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_split(root: Path, split_name: str):
    path = root / f"{split_name}.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    # handle list of ids or list of dicts with 'episode_id'
    if isinstance(data, list):
        if data and isinstance(data[0], dict) and "episode_id" in data[0]:
            return {row["episode_id"] for row in data}
        return set(data)
    return set()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.split_dir.mkdir(parents=True, exist_ok=True)

    splits = {name: load_split(args.split_dir, name) for name in ("train", "val", "test")}

    step_rows_by_split = defaultdict(list)
    episode_rows_by_split = defaultdict(list)

    for trace_path in iter_trace_files(args.traces_dir):
        rows = load_trace(trace_path)
        if not rows:
            continue
        episode_id = f"{trace_path.parent.name}:{trace_path.name}"
        split_name = next((name for name, ids in splits.items() if episode_id in ids), "train")
        episode_step_rows = []
        for i, raw_step in enumerate(rows):
            feature_row = step_feature_row(trace_path, raw_step, episode_id, i)
            feature_row["split"] = split_name
            step_rows_by_split[split_name].append(feature_row)
            episode_step_rows.append(feature_row)
        episode_row = episode_feature_row(episode_id, episode_step_rows)
        episode_row["split"] = split_name
        episode_rows_by_split[split_name].append(episode_row)
    for split_name, rows in step_rows_by_split.items():
        steps_out = args.output_dir / f"{split_name}_{args.steps_file}"
        with steps_out.open("w", encoding="utf-8") as fp:
            for row in rows:
                fp.write(json.dumps(row) + "\n")
        print(f"[{split_name}] steps: {len(rows)} -> {steps_out}")

    for split_name, rows in episode_rows_by_split.items():
        episodes_out = args.output_dir / f"{split_name}_{args.episodes_file}"
        with episodes_out.open("w", encoding="utf-8") as fp:
            for row in rows:
                fp.write(json.dumps(row) + "\n")
        print(f"[{split_name}] episodes: {len(rows)} -> {episodes_out}")


if __name__ == "__main__":
    main()
