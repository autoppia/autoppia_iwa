"""PyTorch dataset helpers for reward-model training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import torch
from torch.utils.data import Dataset

from autoppia_rm.utils.text import encode_text


FEATURE_DIR = Path("data/rm/features")
PAIRS_PATH = Path("data/rm/pairs/pairs.jsonl")
SPLITS_DIR = Path("data/rm/splits")


def _load_vector(row_id: str) -> torch.Tensor:
    obs_path = FEATURE_DIR / f"{row_id}.obs.json"
    sem_path = FEATURE_DIR / f"{row_id}.sem.json"
    if not obs_path.exists() or not sem_path.exists():
        raise FileNotFoundError(f"Missing features for {row_id}")

    obs = json.loads(obs_path.read_text())
    sem = json.loads(sem_path.read_text())

    obs_vec = encode_text(obs.get("dom_excerpt", ""), obs.get("url_tokens", []))
    sem_vec = encode_text(json.dumps(sem, ensure_ascii=False))
    return torch.tensor(obs_vec + sem_vec, dtype=torch.float32)


class PrefPairDataset(Dataset):
    def __init__(self, *, limit: int | None = None):
        if not PAIRS_PATH.exists():
            raise FileNotFoundError("Preference pairs file missing. Run build_preference_pairs().")
        rows = [json.loads(line) for line in PAIRS_PATH.read_text().splitlines() if line]
        self.rows = rows[:limit] if limit else rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        row = self.rows[index]
        x_pos = _load_vector(row["pos_id"])
        x_neg = _load_vector(row["neg_id"])
        return {"x_pos": x_pos, "x_neg": x_neg}


class RewardDataset(Dataset):
    """Dataset supervising success probability head with final episode outcomes."""

    def __init__(self, cfg: Optional[object] = None, split: str = "train"):
        meta_path = FEATURE_DIR / f"{split}_finals.json"
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Missing metadata {meta_path}. Expected list of {{'rid': str, 'y_success': int}}."
            )
        self.rows: List[Dict[str, object]] = json.loads(meta_path.read_text())

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        row = self.rows[index]
        vec = _load_vector(row["rid"])  # type: ignore[arg-type]
        success = torch.tensor(float(row.get("y_success", 0)), dtype=torch.float32)
        return {"x": vec, "y_success": success}


class SemanticDataset(Dataset):
    """Dataset combining obs vectors with LLM labels for distillation."""

    def __init__(self, split: str = "train"):
        split_path = SPLITS_DIR / f"semantic_{split}.json"
        if not split_path.exists():
            raise FileNotFoundError(
                f"Missing split file {split_path}. Provide a JSON list of row ids for the split."
            )
        self.ids: List[str] = json.loads(split_path.read_text())

    def __len__(self) -> int:
        return len(self.ids)

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        row_id = self.ids[index]
        vec = _load_vector(row_id)
        sem_path = FEATURE_DIR / f"{row_id}.sem.json"
        sem = json.loads(sem_path.read_text())

        page_type = sem.get("page_type", "unknown")
        page_idx = ["listing", "product", "cart", "home", "search", "unknown"].index(page_type) if page_type in {
            "listing",
            "product",
            "cart",
            "home",
            "search",
            "unknown",
        } else 5
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
