from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score

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
    parser = argparse.ArgumentParser(description="Train a baseline classifier on DOM+JS step features.")
    parser.add_argument("--steps-file", type=Path, default=Path("data/rm/features/dom_event_steps.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/rm/ckpts/dom_event_baseline.pkl"))
    return parser.parse_args()


def load_dataset(path: Path):
    xs = []
    ys = []
    if not path.exists():
        raise FileNotFoundError(f"Steps file not found: {path}")
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            xs.append([row.get(col, 0.0) or 0.0 for col in FEATURE_COLUMNS])
            ys.append(1 if row.get("success") else 0)
    if not xs:
        raise RuntimeError("Dataset is empty; run build_dom_event_features first.")
    return np.array(xs, dtype=float), np.array(ys, dtype=int)


def main() -> None:
    args = parse_args()
    X, y = load_dataset(args.steps_file)
    if len(set(y)) < 2:
        print("Not enough label diversity (need both success and failure). Collect more traces before training.")
        return
    model = GradientBoostingClassifier()
    model.fit(X, y)
    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds, zero_division=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS}, args.output)
    print(f"Saved baseline model to {args.output}")
    print(f"Train accuracy: {acc:.3f} | F1: {f1:.3f}")


if __name__ == "__main__":
    main()
