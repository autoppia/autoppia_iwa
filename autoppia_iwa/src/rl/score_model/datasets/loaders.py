"""PyTorch dataset helpers for reward-model training."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from ..utils.text import encode_text

FEATURE_DIR = Path(os.getenv("SCORE_MODEL_FEATURE_DIR", "inputs/reward_model/features"))
VECTOR_DIR = Path(os.getenv("SCORE_MODEL_VECTOR_DIR", FEATURE_DIR / "vectors"))
PAIRS_PATH = Path(os.getenv("SCORE_MODEL_PAIRS_PATH", "inputs/reward_model/pairs/pairs.jsonl"))
SPLITS_DIR = Path(os.getenv("SCORE_MODEL_SPLITS_DIR", "inputs/reward_model/splits"))


@lru_cache(maxsize=65_536)
def _load_vector_cache(row_id: str) -> np.ndarray:
    """Return cached feature vector, preferring precomputed tensors."""

    vec_path = VECTOR_DIR / f"{row_id}.npy"
    if vec_path.exists():
        return np.load(vec_path, allow_pickle=False)

    obs_path = FEATURE_DIR / f"{row_id}.obs.json"
    sem_path = FEATURE_DIR / f"{row_id}.sem.json"
    if not obs_path.exists() or not sem_path.exists():
        raise FileNotFoundError(f"Missing features for {row_id}")

    obs = json.loads(obs_path.read_text())
    sem = json.loads(sem_path.read_text())
    obs_vec = encode_text(obs.get("dom_excerpt", ""), obs.get("url_tokens", []))
    sem_vec = encode_text(json.dumps(sem, ensure_ascii=False))
    data = np.asarray(obs_vec + sem_vec, dtype=np.float32)
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    np.save(vec_path, data, allow_pickle=False)
    return data


def _load_vector(row_id: str) -> torch.Tensor:
    data = _load_vector_cache(row_id)
    return torch.tensor(data, dtype=torch.float32)


class PrefPairDataset(Dataset):
    def __init__(self, *, limit: int | None = None):
        if not PAIRS_PATH.exists():
            raise FileNotFoundError("Preference pairs file missing. Run build_preference_pairs().")
        rows = [json.loads(line) for line in PAIRS_PATH.read_text().splitlines() if line]
        self.rows = rows[:limit] if limit else rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        x_pos = _load_vector(row["pos_id"])
        x_neg = _load_vector(row["neg_id"])
        return {"x_pos": x_pos, "x_neg": x_neg}


class RewardDataset(Dataset):
    """Dataset supervising success probability head with final episode outcomes."""

    def __init__(self, cfg: object | None = None, split: str = "train"):
        meta_path = FEATURE_DIR / f"{split}_finals.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Missing metadata {meta_path}. Expected list of {{'rid': str, 'y_success': int}}.")
        self.rows: list[dict[str, object]] = json.loads(meta_path.read_text())

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        vec = _load_vector(row["rid"])  # type: ignore[arg-type]
        success = torch.tensor(float(row.get("y_success", 0)), dtype=torch.float32)
        payload: dict[str, torch.Tensor] = {"x": vec, "y_success": success}

        if "final_score" in row:
            payload["y_score"] = torch.tensor(float(row.get("final_score", 0.0)), dtype=torch.float32)
        elif "raw_score" in row:
            payload["y_score"] = torch.tensor(float(row.get("raw_score", 0.0)), dtype=torch.float32)

        if "tests_passed" in row and "tests_total" in row:
            tests_passed = float(row.get("tests_passed", 0))
            tests_total = float(row.get("tests_total", 0))
            payload["tests_passed"] = torch.tensor(tests_passed, dtype=torch.float32)
            payload["tests_total"] = torch.tensor(tests_total, dtype=torch.float32)
            if tests_total > 0:
                payload["tests_ratio"] = torch.tensor(tests_passed / tests_total, dtype=torch.float32)

        return payload


class SemanticDataset(Dataset):
    """Dataset combining obs vectors with LLM labels for distillation."""

    def __init__(self, split: str = "train"):
        split_path = SPLITS_DIR / f"semantic_{split}.json"
        if not split_path.exists():
            raise FileNotFoundError(f"Missing split file {split_path}. Provide a JSON list of row ids for the split.")
        self.ids: list[str] = json.loads(split_path.read_text())

    def __len__(self) -> int:
        return len(self.ids)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row_id = self.ids[index]
        vec = _load_vector(row_id)
        sem_path = FEATURE_DIR / f"{row_id}.sem.json"
        sem = json.loads(sem_path.read_text())

        page_type = sem.get("page_type", "unknown")
        page_idx = (
            ["listing", "product", "cart", "home", "search", "unknown"].index(page_type)
            if page_type
            in {
                "listing",
                "product",
                "cart",
                "home",
                "search",
                "unknown",
            }
            else 5
        )
        progress = float(sem.get("goal_progress", 0.0))
        affordances = sem.get("affordances", {})
        # Map affordances to fixed ordering (sorted for determinism)
        aff_keys = sorted(affordances.keys())[:16]
        aff_vec = torch.zeros(16, dtype=torch.float32)
        for idx, key in enumerate(aff_keys):
            aff_vec[idx] = float(bool(affordances[key]))

        return {
            "x": vec,
            "y_page": torch.tensor(page_idx, dtype=torch.long),
            "y_prog": torch.tensor(progress, dtype=torch.float32),
            "y_aff": aff_vec,
        }
