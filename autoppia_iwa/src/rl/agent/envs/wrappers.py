from __future__ import annotations

from typing import Any, Dict

import gymnasium as gym
import numpy as np


def _flatten_obs(obs: Dict[str, np.ndarray], space: gym.spaces.Dict) -> np.ndarray:
    """Normalize/flatten Dict obs into a single float32 vector.

    - Box spaces are normalized by their high when sensible.
    - Int arrays are cast to float32.
    """
    outs: list[np.ndarray] = []
    for k, v in obs.items():
        sp = space.spaces[k]
        arr = v.astype(np.float32).ravel()
        try:
            high = np.array(sp.high, dtype=np.float32).ravel()
            if high.size == arr.size and np.all(high > 0):
                arr = np.clip(arr / (high + 1e-6), 0.0, 1.0)
        except Exception:
            pass
        outs.append(arr)
    return np.concatenate(outs, axis=0) if outs else np.zeros((0,), dtype=np.float32)


class RNDIntrinsicRewardWrapper(gym.Wrapper):
    """Adds beta * intrinsic curiosity reward (RND) on top of the env reward.

    Trains a predictor online to match a fixed random target on flattened obs.
    The prediction error is used as novelty (intrinsic reward).

    Torch is imported lazily at runtime inside __init__, so importing this module
    doesn't require torch to be installed until you actually construct the wrapper.
    """

    def __init__(
        self,
        env: gym.Env,
        beta: float = 0.05,
        hid: int = 256,
        feat_dim: int = 128,
        lr: float = 1e-3,
    ):
        super().__init__(env)

        # --- Lazy import of PyTorch (runtime only) ---
        try:
            import torch  # noqa: F401
            from torch import nn  # noqa: F401
            from torch import optim  # noqa: F401
        except Exception as e:
            raise RuntimeError(
                "PyTorch is required for RNDIntrinsicRewardWrapper but could not be imported. "
                "Install it with: pip install torch --index-url https://download.pytorch.org/whl/cpu "
                "(or the appropriate CUDA build)."
            ) from e

        # Keep explicit handles to torch APIs on the instance to use later
        self._torch = __import__("torch")
        self._nn = self._torch.nn
        self._optim = self._torch.optim

        # Helper to build a small MLP without needing a top-level torch subclass
        def _build_mlp(in_dim: int, hidden: int, out_dim: int):
            return self._nn.Sequential(
                self._nn.Linear(in_dim, hidden),
                self._nn.ReLU(),
                self._nn.Linear(hidden, hidden),
                self._nn.ReLU(),
                self._nn.Linear(hidden, out_dim),
            )

        # Probe observation shape
        obs, _ = env.reset()
        flat = _flatten_obs(obs, env.observation_space)
        in_dim = int(flat.shape[0]) if flat.ndim == 1 else int(np.prod(flat.shape))

        # Models + optimizer
        self.beta = float(beta)
        self.target = _build_mlp(in_dim, hid, feat_dim).eval()
        for p in self.target.parameters():
            p.requires_grad_(False)

        self.predictor = _build_mlp(in_dim, hid, feat_dim)
        self.opt = self._optim.Adam(self.predictor.parameters(), lr=lr)

        # Device + move
        self._device = self._torch.device("cuda" if self._torch.cuda.is_available() else "cpu")
        self.target.to(self._device)
        self.predictor.to(self._device)

    def reset(self, **kwargs: Dict[str, Any]):
        return self.env.reset(**kwargs)

    def step(self, action: int):  # type: ignore[override]
        obs, ext_r, term, trunc, info = self.env.step(action)
        flat = _flatten_obs(obs, self.observation_space)

        if flat.size == 0:
            return obs, ext_r, term, trunc, info

        x = self._torch.from_numpy(flat).to(self._device).unsqueeze(0)

        with self._torch.no_grad():
            t = self.target(x)

        p = self.predictor(x)
        loss = self._torch.mean((p - t) ** 2)

        self.opt.zero_grad(set_to_none=True)
        loss.backward()
        self._torch.nn.utils.clip_grad_norm_(self.predictor.parameters(), 1.0)
        self.opt.step()

        intr = float(loss.detach().cpu().item())
        info = dict(info or {})
        info["rnd_intrinsic"] = intr
        info["reward_extrinsic"] = float(ext_r)

        return obs, float(ext_r + self.beta * intr), term, trunc, info


__all__ = ["RNDIntrinsicRewardWrapper", "_flatten_obs"]
