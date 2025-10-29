"""Simple running mean/variance normaliser for shaped rewards."""

from __future__ import annotations


class RunningNorm:
    """Welford-style online normaliser."""

    def __init__(self, eps: float = 1e-6):
        self.count = eps
        self.mean = 0.0
        self.var = 1.0

    def update(self, x: float) -> None:
        self.count += 1.0
        delta = x - self.mean
        self.mean += delta / self.count
        self.var += delta * (x - self.mean)

    def normalize(self, x: float) -> float:
        std = (self.var / max(1.0, self.count - 1.0)) ** 0.5
        return (x - self.mean) / (std + 1e-6)
