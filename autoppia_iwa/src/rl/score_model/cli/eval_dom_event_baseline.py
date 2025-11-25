from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

FEATURE_COLUMNS = [
    "html_length",
    "dom_length",
    "num_inputs",
    "num_buttons",
    "num_links",
    "num_forms",
    "js_event_total",
    "backend_event_count_before",
    "backend_event_count_after",
    "backend_event_delta",
    "action_x",
    "action_y",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the DOM-event baseline model on val/test splits.")
    parser.add_argument("--model", type=Path, default=Path("data/inputs/reward_model/ckpts/dom_event_baseline.pkl"))
    parser.add_argument("--split", choices=["val", "test"], default="val")
    parser.add_argument("--features-dir", type=Path, default=Path("data/inputs/reward_model/features"))
    return parser.parse_args()


def load_dataset(path: Path):
    xs, ys = [], []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            xs.append([row.get(col, 0.0) or 0.0 for col in FEATURE_COLUMNS])
            ys.append(1 if row.get("success") else 0)
    if not xs:
        raise RuntimeError(f"No rows found in {path}")
    return np.array(xs, dtype=float), np.array(ys, dtype=int)


def main() -> None:
    args = parse_args()
    dataset_path = args.features_dir / f"{args.split}_dom_event_steps.jsonl"
    X, y = load_dataset(dataset_path)
    bundle = joblib.load(args.model)
    model = bundle.get("model")
    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="binary", zero_division=0)
    print(f"Eval split={args.split} | accuracy={acc:.3f} | precision={precision:.3f} | recall={recall:.3f} | f1={f1:.3f}")


if __name__ == "__main__":
    main()
