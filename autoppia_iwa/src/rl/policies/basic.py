from __future__ import annotations

import random
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim

MACRO_ACTIONS: list[dict[str, Any]] = [
    {"type": "WaitAction", "time_seconds": 0.2},
    {"type": "ScrollAction", "down": True, "value": None},
    {"type": "ScrollAction", "up": True, "value": None},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Search"}},
    {"type": "TypeAction", "selector": {"type": "attributeValueSelector", "attribute": "placeholder", "value": "Search"}, "text": "italian"},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Date"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Time"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "People"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Country"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Occasion"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Menu"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Book"}},
    {"type": "ClickAction", "selector": {"type": "tagContainsSelector", "value": "Complete"}},
]


def _featurize(obs: dict[str, Any]) -> torch.Tensor:
    url = (obs.get("url") or "")[:256].lower()
    prompt = (obs.get("task_prompt") or "")[:512].lower()
    step = int(obs.get("step") or 0)
    feats = [
        "search" in prompt or "search" in url,
        "book" in prompt,
        "menu" in prompt,
        "complete" in prompt,
        "restaurant" in prompt,
    ]
    return torch.tensor([float(x) for x in feats] + [float(step)], dtype=torch.float32)


class BasicPolicyNet(nn.Module):
    def __init__(self, num_actions: int, hidden: int = 32):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(6, hidden), nn.ReLU(), nn.Linear(hidden, num_actions))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class BasicPolicy:
    def __init__(self, lr: float = 3e-3, seed: int = 0, device: str = "cpu"):
        random.seed(seed)
        torch.manual_seed(seed)
        self.device = device
        self.actions = MACRO_ACTIONS
        self.model = BasicPolicyNet(num_actions=len(self.actions)).to(device)
        self.opt = optim.Adam(self.model.parameters(), lr=lr)

    async def act(self, obs: dict[str, Any]) -> dict[str, Any] | str:
        x = _featurize(obs).to(self.device)
        logits = self.model(x)
        probs = torch.softmax(logits, dim=-1)
        idx = torch.distributions.Categorical(probs).sample().item()
        return self.actions[idx]

    def update(self, batch_trajectories: list[dict[str, Any]], gamma: float = 0.99) -> dict[str, float]:
        losses = []
        total_return = 0.0
        total_len = 0
        for traj in batch_trajectories:
            obs_seq, act_idx, rews = traj["obs"], traj["acts"], traj["rews"]
            G = 0.0
            returns = []
            for r in reversed(rews):
                G = r + gamma * G
                returns.append(G)
            returns.reverse()
            R = torch.tensor(returns, dtype=torch.float32, device=self.device)
            if len(R) > 1:
                R = (R - R.mean()) / (R.std() + 1e-6)
            logps = []
            for ob, ai in zip(obs_seq, act_idx, strict=False):
                x = _featurize(ob).to(self.device)
                logits = self.model(x)
                logp = torch.log_softmax(logits, dim=-1)[ai]
                logps.append(logp)
            logps = torch.stack(logps)
            loss = -(logps * R).sum()
            losses.append(loss)
            total_return += float(sum(rews))
            total_len += len(rews)
        if not losses:
            return {"loss": 0.0, "avg_return": 0.0, "avg_len": 0.0}
        L = torch.stack(losses).mean()
        self.opt.zero_grad()
        L.backward()
        self.opt.step()
        return {"loss": float(L.detach().cpu()), "avg_return": total_return / max(1, len(batch_trajectories)), "avg_len": total_len / max(1, len(batch_trajectories))}

    def action_index(self, action_dict: dict[str, Any]) -> int:
        for i, a in enumerate(self.actions):
            if a.get("type") == action_dict.get("type"):
                return i
        return 0
