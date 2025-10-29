#!/usr/bin/env python3
"""Generate train/val/test splits and final-step metadata from evaluation dumps."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable

RAW_DIR = Path("data/rm/raw_evaluations")
SPLIT_DIR = Path("data/rm/splits")
FEATURE_DIR = Path("data/rm/features")

SPLIT_DIR.mkdir(parents=True, exist_ok=True)
FEATURE_DIR.mkdir(parents=True, exist_ok=True)


def _iter_episodes() -> Iterable[dict]:
    for path in RAW_DIR.glob("*.jsonl"):
        with path.open() as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                yield json.loads(line)


def _collect_by_id() -> Dict[str, dict]:
    episodes = {}
    for episode in _iter_episodes():
        eid = episode.get("episode_id")
        if not eid:
            continue
        episodes[eid] = episode
    return episodes


def _write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def make_splits(seed: int = 1337, train_p: float = 0.8, val_p: float = 0.1) -> None:
    episodes = _collect_by_id()
    ids = list(episodes.keys())
    if not ids:
        raise RuntimeError("No evaluation episodes found in data/rm/raw_evaluations/")

    random.seed(seed)
    random.shuffle(ids)

    total = len(ids)
    n_train = int(total * train_p)
    n_val = int(total * val_p)

    split_map = {
        "train": ids[:n_train],
        "val": ids[n_train : n_train + n_val],
        "test": ids[n_train + n_val :],
    }

    # Persist episode ID splits
    for split, split_ids in split_map.items():
        _write_json(SPLIT_DIR / f"{split}.json", split_ids)

    # Semantic splits: all step row-ids per split
    for split, split_ids in split_map.items():
        semantic_ids = []
        for eid in split_ids:
            episode = episodes[eid]
            for step in episode.get("steps", []):
                idx = step.get("index")
                if idx is None:
                    continue
                semantic_ids.append(f"{eid}_{idx}")
        _write_json(SPLIT_DIR / f"semantic_{split}.json", semantic_ids)

    # Reward metadata: last step per episode with success label
    for split, split_ids in split_map.items():
        rows = []
        for eid in split_ids:
            episode = episodes[eid]
            steps = episode.get("steps", [])
            if not steps:
                continue
            last_idx = steps[-1].get("index")
            if last_idx is None:
                continue
            rid = f"{eid}_{last_idx}"
            y_success = 1 if float(episode.get("final_score", 0.0)) > 0.5 else 0
            rows.append({"rid": rid, "y_success": y_success})
        _write_json(FEATURE_DIR / f"{split}_finals.json", rows)


def main() -> None:
    make_splits()


if __name__ == "__main__":
    main()
