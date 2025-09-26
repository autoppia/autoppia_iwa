"""
Behavior Cloning (supervised) policy on top of simple obs features (url/prompt/step).
We predict a discrete action from a learned vocabulary of action JSON strings.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim


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


class ActionVocab:
    """Maps action JSON strings to integer ids and back."""

    def __init__(self, actions: Iterable[dict[str, Any]]):
        uniq = []
        seen = set()
        for a in actions:
            s = json.dumps(a, sort_keys=True, separators=(",", ":"))
            if s not in seen:
                uniq.append(s)
                seen.add(s)
        self._itos = uniq
        self._stoi = {s: i for i, s in enumerate(self._itos)}

    def __len__(self):
        return len(self._itos)

    def encode(self, a: dict[str, Any]) -> int:
        s = json.dumps(a, sort_keys=True, separators=(",", ":"))
        return self._stoi[s]

    def decode(self, idx: int) -> dict[str, Any]:
        return json.loads(self._itos[idx])


class BCNet(nn.Module):
    def __init__(self, num_actions: int, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, num_actions),
        )

    def forward(self, x):
        return self.net(x)


class BCPolicy:
    """
    - fit(dataset): supervised cross-entropy
    - act(obs): returns action dict (decoded from vocab)
    """

    def __init__(self, vocab: ActionVocab, lr: float = 3e-3, device: str = "cpu"):
        self.vocab = vocab
        self.model = BCNet(num_actions=len(vocab)).to(device)
        self.opt = optim.Adam(self.model.parameters(), lr=lr)
        self.device = device

    def fit(self, obs_list: list[dict[str, Any]], act_list: list[dict[str, Any]], epochs: int = 5, batch_size: int = 64) -> dict[str, float]:
        X = torch.stack([_featurize(o) for o in obs_list]).to(self.device)
        y = torch.tensor([self.vocab.encode(a) for a in act_list], dtype=torch.long, device=self.device)

        ds = torch.utils.data.TensorDataset(X, y)
        dl = torch.utils.data.DataLoader(ds, batch_size=batch_size, shuffle=True)

        ce = nn.CrossEntropyLoss()
        last = 0.0
        for _ in range(epochs):
            for xb, yb in dl:
                logits = self.model(xb)
                loss = ce(logits, yb)
                self.opt.zero_grad()
                loss.backward()
                self.opt.step()
                last = float(loss.detach().cpu())
        return {"final_loss": last}

    async def act(self, obs: dict[str, Any]) -> dict[str, Any] | str:
        self.model.eval()
        with torch.no_grad():
            x = _featurize(obs).to(self.device)
            logits = self.model(x)
            idx = int(torch.argmax(logits).item())
        return self.vocab.decode(idx)

    # utils for save/load
    def state_dict(self):
        return self.model.state_dict()

    def load_state_dict(self, sd):
        self.model.load_state_dict(sd)
