"""Convert leaderboard samples into training-ready artifacts."""

from __future__ import annotations

import argparse
import json
import random
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from loguru import logger

try:  # pragma: no cover - optional progress bar
    from tqdm import tqdm
except Exception:  # pragma: no cover
    tqdm = None

from ...utils.text import encode_text


@dataclass
class Sample:
    task_id: str
    solution_id: str | None
    website: str | None
    use_case: str | None
    intent: str | None
    start_url: str | None
    required_url: str | None
    score: float | None
    passed: bool | None
    num_actions: int
    actions: list[dict]
    trajectory: list[dict]

    @property
    def row_id(self) -> str:
        suffix = self.solution_id or "solution"
        safe_suffix = re.sub(r"[^a-zA-Z0-9_-]", "_", suffix)
        safe_task = re.sub(r"[^a-zA-Z0-9_-]", "_", self.task_id)
        return f"{safe_task}_{safe_suffix}"


def _iter_samples(dataset_path: Path) -> Iterable[Sample]:
    with dataset_path.open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            yield Sample(
                task_id=data.get("task_id"),
                solution_id=data.get("solution_id"),
                website=data.get("website"),
                use_case=data.get("use_case"),
                intent=data.get("intent"),
                start_url=data.get("start_url"),
                required_url=data.get("required_url"),
                score=data.get("score"),
                passed=data.get("passed"),
                num_actions=data.get("num_actions", 0),
                actions=data.get("actions", []),
                trajectory=data.get("trajectory", []),
            )


def _summarize_actions(actions: list[dict]) -> str:
    chunks: list[str] = []
    for action in actions:
        action_type = action.get("type")
        attrs = action.get("attributes") or {}
        selector = attrs.get("selector") or {}
        selector_value = selector.get("value") or ""
        text = attrs.get("text")
        if selector_value:
            chunks.append(f"{action_type}:{selector_value}")
        elif text:
            chunks.append(f"{action_type}:{text}")
        else:
            chunks.append(action_type or "action")
    return " | ".join(chunks)


def _build_obs(sample: Sample) -> dict:
    intent = sample.intent or ""
    action_summary = _summarize_actions(sample.actions)
    context_parts = [
        f"website={sample.website or 'unknown'}",
        f"use_case={sample.use_case or 'unknown'}",
        f"intent={intent}",
        f"actions={action_summary}",
    ]
    if sample.required_url:
        context_parts.append(f"required={sample.required_url}")
    context_text = " ".join(context_parts)
    url_tokens = (sample.start_url or "").split("/")
    return {"dom_excerpt": context_text[:8000], "url_tokens": url_tokens}


def _build_sem(sample: Sample) -> dict:
    progress = 1.0 if sample.passed else 0.0
    affordances = {
        "num_actions": sample.num_actions,
        "has_trajectory": bool(sample.trajectory),
    }
    return {
        "page_type": (sample.use_case or "unknown")[:64],
        "goal_progress": progress,
        "affordances": affordances,
    }


def _encode_vector(obs: dict, sem: dict) -> list[float]:
    obs_vec = encode_text(obs.get("dom_excerpt", ""), obs.get("url_tokens", []))
    sem_vec = encode_text(json.dumps(sem, ensure_ascii=False))
    return obs_vec + sem_vec


def _split_samples(samples: list[Sample], train_ratio: float, val_ratio: float) -> dict[str, list[Sample]]:
    random.shuffle(samples)
    total = len(samples)
    train_end = max(1, int(total * train_ratio))
    val_end = max(train_end + 1, int(total * (train_ratio + val_ratio)))
    return {
        "train": samples[:train_end],
        "val": samples[train_end:val_end],
        "test": samples[val_end:],
    }


def _write_metadata(split_samples: dict[str, list[Sample]], features_dir: Path) -> None:
    features_dir.mkdir(parents=True, exist_ok=True)
    for split, items in split_samples.items():
        rows = [
            {
                "rid": sample.row_id,
                "y_success": 1 if sample.passed else 0,
                "final_score": sample.score if sample.score is not None else (1 if sample.passed else 0),
            }
            for sample in items
        ]
        (features_dir / f"{split}_finals.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))


def _write_pairs(samples: list[Sample], output_path: Path, max_pairs: int) -> None:
    positives = [s for s in samples if s.passed]
    negatives = [s for s in samples if s.passed is False]
    if not positives or not negatives:
        logger.warning("Not enough positives/negatives to build preference pairs.")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    random.shuffle(positives)
    pairs_written = 0
    with output_path.open("w", encoding="utf-8") as handle:
        idx = 0
        while pairs_written < max_pairs and positives and negatives:
            pos = positives[idx % len(positives)]
            neg = random.choice(negatives)
            handle.write(json.dumps({"pos_id": pos.row_id, "neg_id": neg.row_id}, ensure_ascii=False))
            handle.write("\n")
            pairs_written += 1
            idx += 1
    logger.info("Wrote {} preference pairs to {}", pairs_written, output_path)


def _write_obs_sem(samples: list[Sample], features_dir: Path) -> None:
    vector_dir = features_dir / "vectors"
    vector_dir.mkdir(parents=True, exist_ok=True)
    iterator = tqdm(samples, desc="Writing features", unit="sample") if tqdm else samples
    for sample in iterator:
        obs = _build_obs(sample)
        sem = _build_sem(sample)
        (features_dir / f"{sample.row_id}.obs.json").write_text(json.dumps(obs, ensure_ascii=False))
        (features_dir / f"{sample.row_id}.sem.json").write_text(json.dumps(sem, ensure_ascii=False))
        vec = np.asarray(_encode_vector(obs, sem), dtype=np.float32)
        np.save(vector_dir / f"{sample.row_id}.npy", vec, allow_pickle=False)


def build_artifacts(dataset_path: Path, output_dir: Path, train_ratio: float, val_ratio: float, max_pairs: int) -> None:
    samples = list(_iter_samples(dataset_path))
    if not samples:
        raise ValueError(f"No samples found in {dataset_path}")
    logger.info("Loaded {} samples from {}", len(samples), dataset_path)

    splits = _split_samples(samples, train_ratio, val_ratio)
    features_dir = output_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)

    _write_obs_sem(samples, features_dir)
    _write_metadata(splits, features_dir)

    pairs_path = output_dir / "pairs" / "pairs.jsonl"
    _write_pairs(splits["train"], pairs_path, max_pairs)

    (output_dir / "config.json").write_text(
        json.dumps(
            {
                "dataset": str(dataset_path),
                "total_samples": len(samples),
                "split_counts": {k: len(v) for k, v in splits.items()},
                "train_ratio": train_ratio,
                "val_ratio": val_ratio,
                "max_pairs": max_pairs,
            },
            indent=2,
        )
    )
    logger.info("Artifacts written under {}", output_dir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True, help="Path to leaderboard dataset JSONL.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Destination directory for artifacts.")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Training split ratio.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio.")
    parser.add_argument("--max-pairs", type=int, default=50000, help="Maximum preference pairs to create.")
    parser.add_argument("--seed", type=int, default=1337, help="Random seed.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    random.seed(args.seed)
    build_artifacts(
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        max_pairs=args.max_pairs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
