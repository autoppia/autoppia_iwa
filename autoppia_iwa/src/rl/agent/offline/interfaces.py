from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

import numpy as np


@dataclass(frozen=True)
class ObservationSpec:
    """Shape/dtype information for the MultiInput observation."""

    goal_ids: tuple[int, ...]
    dom_ids: tuple[int, ...]
    url_id: tuple[int, ...]
    prev_actions: tuple[int, ...]
    topk_text_ids: tuple[int, ...]
    topk_meta: tuple[int, ...]
    score: tuple[int, ...] = (1,)
    action_dim: int = 0

    @property
    def discrete_action_dim(self) -> int:
        if self.action_dim <= 0:
            raise AttributeError("Discrete action dimension was not provided.")
        return self.action_dim


@dataclass(frozen=True)
class StepRecord:
    """One transition produced by the data provider."""

    # Observations follow the same layout produced by IWAWebEnv.
    goal_ids: np.ndarray
    dom_ids: np.ndarray
    url_id: np.ndarray
    prev_actions: np.ndarray
    topk_text_ids: np.ndarray
    topk_meta: np.ndarray
    action_mask: np.ndarray
    action_index: int
    score: np.ndarray | None = None


@dataclass(frozen=True)
class Trajectory:
    """Collection of ordered steps for a single episode."""

    steps: list[StepRecord]


class TrajectoryProvider(Protocol):
    """Abstraction for loading trajectories from any backend (HTTP, DB, local)."""

    def fetch(self, limit: int | None = None) -> Iterable[Trajectory]:
        """Return an iterable of trajectories (may stream)."""
        ...
