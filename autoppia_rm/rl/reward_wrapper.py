"""Blend binary test reward with learned reward model outputs for PPO."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import torch

from autoppia_rm.features.snapshot_encoder import clean_dom, tokenize_url
from autoppia_rm.models.reward_model import RewardModel
from autoppia_rm.utils.text import encode_text


class RewardBlender:
    """Potential-based reward shaping using the learned reward model."""

    def __init__(self, checkpoint_path: str | Path, *, alpha: float = 0.5, beta: float = 0.5, gamma: float = 0.995, obs_dim: int = 384, sem_dim: int = 384):
        self.checkpoint_path = Path(checkpoint_path)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.obs_dim = obs_dim
        self.sem_dim = sem_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = RewardModel(in_dim=obs_dim + sem_dim).to(self.device)
        state = torch.load(self.checkpoint_path, map_location=self.device)
        self.model.load_state_dict(state)
        self.model.eval()
        self.prev_phi = 0.0

    @torch.no_grad()
    def _encode(self, url: str, html_text: str, semantic_json: Optional[dict] = None) -> torch.Tensor:
        dom = clean_dom(html_text)
        obs_vec = encode_text(dom, tokenize_url(url))
        sem_payload = semantic_json or {}
        sem_json = json.dumps(sem_payload, ensure_ascii=False)
        sem_vec = encode_text(sem_json)
        return torch.tensor(obs_vec + sem_vec, dtype=torch.float32, device=self.device)

    @torch.no_grad()
    def step_reward(self, url: str, html_text: str, binary_reward: float, semantic_hint: Optional[dict] = None) -> float:
        """Return shaped reward using learned model and potential function."""

        vec = self._encode(url, html_text, semantic_hint)
        outputs = self.model(vec)
        reward = outputs["R"].item()
        phi = outputs["p_success"].item()
        shaped = binary_reward + self.alpha * reward + self.beta * (self.gamma * phi - self.prev_phi)
        self.prev_phi = phi
        return float(shaped)

    def compute(self, *, url: str, html_text: str, binary_reward: float, semantic_hint: Optional[dict] = None) -> float:
        """Backward-compatible alias for :meth:`step_reward`."""

        return self.step_reward(url, html_text, binary_reward, semantic_hint)

    def reset(self) -> None:
        self.prev_phi = 0.0
