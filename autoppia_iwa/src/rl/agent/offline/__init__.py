"""
Offline data utilities for RL warm-start (behavior cloning).

This package provides:
    - Protocols for fetching trajectory data.
    - Dataset helpers for feeding torch DataLoaders.
    - A simple behavior cloning trainer that mirrors the MultiInputPolicy
      architecture used by MaskablePPO.
"""

from .bc_trainer import BehaviorCloningConfig, BehaviorCloningTrainer
from .http_provider import HttpTrajectoryProvider
from .interfaces import ObservationSpec, StepRecord, Trajectory, TrajectoryProvider

__all__ = [
    "BehaviorCloningConfig",
    "BehaviorCloningTrainer",
    "HttpTrajectoryProvider",
    "ObservationSpec",
    "StepRecord",
    "Trajectory",
    "TrajectoryProvider",
]
