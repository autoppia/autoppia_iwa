"""Lightweight network to distil LLM-provided semantic labels."""

from __future__ import annotations

import torch
import torch.nn as nn


class SemanticEncoder(nn.Module):
    """Predict semantic attributes from observation embeddings.

    The module expects a flattened feature vector produced by upstream text/image
    encoders. It outputs logits for page-type classification, goal-progress
    regression, and affordance multi-label predictions.
    """

    def __init__(self, in_dim: int, num_page_types: int = 6, affordance_dim: int = 16, hidden: int = 512):
        super().__init__()
        self.trunk = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.head_page = nn.Linear(hidden, num_page_types)
        self.head_progress = nn.Sequential(nn.Linear(hidden, 1), nn.Sigmoid())
        self.head_affordances = nn.Linear(hidden, affordance_dim)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:  # type: ignore[override]
        h = self.trunk(x)
        return {
            "page_logits": self.head_page(h),
            "goal_progress": self.head_progress(h),
            "affordances": self.head_affordances(h),
        }
