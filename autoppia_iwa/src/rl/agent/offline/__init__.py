"""
Offline data utilities for RL warm-start (behavior cloning).

This package provides:
    - Protocols for fetching trajectory data.
    - Dataset helpers for feeding torch DataLoaders.
    - A simple behavior cloning trainer that mirrors the MultiInputPolicy
      architecture used by MaskablePPO.
"""

from .interfaces import ObservationSpec, StepRecord, Trajectory, TrajectoryProvider  # noqa: F401
from .http_provider import HttpTrajectoryProvider  # noqa: F401
from .bc_trainer import BehaviorCloningConfig, BehaviorCloningTrainer  # noqa: F401

__all__ = [
    "ObservationSpec",
    "StepRecord",
    "Trajectory",
    "TrajectoryProvider",
    "HttpTrajectoryProvider",
    "BehaviorCloningConfig",
    "BehaviorCloningTrainer",
]
