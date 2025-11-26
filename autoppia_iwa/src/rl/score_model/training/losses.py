"""Loss helpers for reward-model training."""

from __future__ import annotations

import torch


def preference_loss(r_pos: torch.Tensor, r_neg: torch.Tensor) -> torch.Tensor:
    """Bradley-Terry preference loss."""

    return -torch.log(torch.sigmoid(r_pos - r_neg) + 1e-8).mean()


def alignment_loss(r: torch.Tensor, p_success: torch.Tensor) -> torch.Tensor:
    """Encourage agreement between scalar reward and success probability."""

    r_norm = (r - r.mean()) / (r.std() + 1e-6)
    logits = torch.logit(torch.clamp(p_success, 1e-4, 1 - 1e-4))
    logits_norm = (logits - logits.mean()) / (logits.std() + 1e-6)
    return torch.mean((r_norm - logits_norm) ** 2)
