"""Enumerations and helpers for the score-model pipeline phases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from . import paths


class PipelinePhase(str, Enum):
    INGEST = "ingest"
    PREPARE = "prepare"
    TRAIN = "train"
    EVAL = "eval"


@dataclass(frozen=True)
class PhasePaths:
    """Filesystem references for a pipeline phase run."""

    phase: PipelinePhase
    run_id: str

    @property
    def root(self) -> Path:
        return paths.subdir(self.phase.value, self.run_id)

    @property
    def raw_path(self) -> Path:
        return self.root / "raw"

    @property
    def processed_path(self) -> Path:
        return self.root / "processed"

    @property
    def artifacts_path(self) -> Path:
        return self.root / "artifacts"

    def ensure(self) -> "PhasePaths":
        for path in (self.root, self.raw_path, self.processed_path, self.artifacts_path):
            path.mkdir(parents=True, exist_ok=True)
        return self
