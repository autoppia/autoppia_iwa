"""Neural reward model trained from preference data and success labels."""

from __future__ import annotations

import torch
import torch.nn as nn


class RewardModel(nn.Module):
    """Fuse observation embeddings into scalar reward and success probability."""

    def __init__(self, in_dim: int, hidden: int = 768):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.head_reward = nn.Linear(hidden, 1)
        self.head_success = nn.Sequential(nn.Linear(hidden, 1), nn.Sigmoid())
        self.head_score = nn.Sequential(nn.Linear(hidden, 1), nn.Sigmoid())

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:  # type: ignore[override]
        h = self.backbone(x)
        reward = self.head_reward(h).squeeze(-1)
        success = self.head_success(h).squeeze(-1)
        score = self.head_score(h).squeeze(-1)
        return {"R": reward, "p_success": success, "score": score}
