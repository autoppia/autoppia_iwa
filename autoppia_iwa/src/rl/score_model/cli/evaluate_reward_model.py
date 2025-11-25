#!/usr/bin/env python3
"""Offline benchmark utilities for the partial-score / reward model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader

try:  # pragma: no cover
    from tqdm import tqdm
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "tqdm is required for evaluate_reward_model. Install it in your environment (pip install tqdm)."
    ) from exc

from ..datasets.loaders import FEATURE_DIR, PAIRS_PATH, RewardDataset, _load_vector
from ..training.train_reward_model import RewardConfig, RewardModel, load_config
from ..utils import config_path as get_config_path


def _load_model(cfg: RewardConfig, checkpoint: Path) -> RewardModel:
    model = RewardModel(cfg.in_dim)
    state = torch.load(checkpoint, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    return model


def _evaluate_success_head(model: RewardModel, dataset: RewardDataset, batch_size: int) -> dict[str, float]:
    if len(dataset) == 0:
        return {}

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    probs: list[float] = []
    labels: list[float] = []
    scores_true: list[float] = []
    scores_pred: list[float] = []

    with torch.no_grad():
        for batch in loader:
            out = model(batch["x"])
            probs.extend(out["p_success"].cpu().numpy().tolist())
            labels.extend(batch["y_success"].cpu().numpy().tolist())
            if "y_score" in batch:
                scores_true.extend(batch["y_score"].cpu().numpy().tolist())
                scores_pred.extend(out["score"].cpu().numpy().tolist())

    y_true = np.asarray(labels, dtype=float)
    y_prob = np.asarray(probs, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)

    metrics: dict[str, float] = {}
    if len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
        metrics["avg_precision"] = average_precision_score(y_true, y_prob)
    else:
        metrics["roc_auc"] = float("nan")
        metrics["avg_precision"] = float("nan")
    metrics["brier"] = brier_score_loss(y_true, y_prob)
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    metrics["recall"] = tp / max(1, tp + fn)
    metrics["precision"] = tp / max(1, tp + fp)

    if scores_true:
        y_score_true = np.asarray(scores_true, dtype=float)
        y_score_pred = np.asarray(scores_pred, dtype=float)
        metrics["score_mae"] = mean_absolute_error(y_score_true, y_score_pred)
        mse = mean_squared_error(y_score_true, y_score_pred)
        metrics["score_rmse"] = float(np.sqrt(mse))
        if np.var(y_score_true) > 1e-6 and np.var(y_score_pred) > 1e-6:
            metrics["score_r2"] = r2_score(y_score_true, y_score_pred)
            corr = np.corrcoef(y_score_true, y_score_pred)[0, 1]
            metrics["score_pearson"] = float(corr)
        else:
            metrics["score_r2"] = float("nan")
            metrics["score_pearson"] = float("nan")

    return metrics


def _evaluate_preference_head(model: RewardModel, cfg: RewardConfig, pairs_path: Path | None = None) -> dict[str, float]:
    target_path = pairs_path or PAIRS_PATH
    if not target_path.exists():
        return {}

    rows = [json.loads(line) for line in target_path.read_text().splitlines() if line.strip()]
    if not rows:
        return {}

    train_pairs = cfg.pref_pairs_per_epoch
    eval_rows = rows[train_pairs:] if len(rows) > train_pairs else rows
    if not eval_rows:
        eval_rows = rows

    iterator = tqdm(eval_rows, desc="Pref eval", unit="pair") if tqdm is not None else eval_rows
    win = 0
    total = 0
    with torch.no_grad():
        for row in iterator:
            x_pos = _load_vector(row["pos_id"])
            x_neg = _load_vector(row["neg_id"])
            out_pos = model(x_pos.unsqueeze(0))
            out_neg = model(x_neg.unsqueeze(0))
            win += int(out_pos["R"].item() > out_neg["R"].item())
            total += 1

    return {"pref_win_rate": win / max(1, total), "pairs_evaluated": total}


def evaluate(config_path: Path, checkpoint: Path | None, pairs_path: Path | None = None) -> None:
    cfg = load_config(config_path)
    checkpoint = checkpoint if checkpoint is not None else cfg.ckpt_path
    model = _load_model(cfg, checkpoint)

    print(f"Using checkpoint: {checkpoint}")

    for split in ("val", "test"):
        try:
            dataset = RewardDataset(cfg, split=split)
        except FileNotFoundError:
            print(f"[warn] Missing reward dataset for split '{split}' – skipping.")
            continue

        metrics = _evaluate_success_head(model, dataset, batch_size=cfg.batch)
        if metrics:
            print(f"\nSuccess-head metrics ({split}):")
            for name in sorted(metrics.keys()):
                value = metrics[name]
                print(f"  {name:>12}: {value:.4f}")

    pref_metrics = _evaluate_preference_head(model, cfg, pairs_path)
    if pref_metrics:
        print("\nPreference-head metrics:")
        for name, value in pref_metrics.items():
            if isinstance(value, float):
                print(f"  {name:>16}: {value:.4f}")
            else:
                print(f"  {name:>16}: {value}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate reward / partial-score model performance.")
    parser.add_argument(
        "--config",
        type=Path,
        default=get_config_path("rm_train.yaml"),
        help="Path to reward-model YAML config.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="Override checkpoint path (defaults to cfg.ckpt_path).",
    )
    parser.add_argument(
        "--pairs",
        type=Path,
        default=None,
        help="Optional path to preference pairs JSONL (defaults to SCORE_MODEL_PAIRS_PATH env).",
    )
    args = parser.parse_args(argv)
    evaluate(args.config, args.checkpoint, args.pairs)


if __name__ == "__main__":
    main()
