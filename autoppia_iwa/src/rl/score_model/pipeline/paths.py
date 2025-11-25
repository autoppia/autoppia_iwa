"""Shared filesystem layout for the score-model pipeline."""

from __future__ import annotations

from pathlib import Path

PIPELINE_ROOT = Path("data/score_model_pipeline")
RAW_DIR = PIPELINE_ROOT / "raw"
PROCESSED_DIR = PIPELINE_ROOT / "processed"
DATASETS_DIR = PIPELINE_ROOT / "datasets"
METRICS_DIR = PIPELINE_ROOT / "metrics"

for target in (PIPELINE_ROOT, RAW_DIR, PROCESSED_DIR, DATASETS_DIR, METRICS_DIR):
    target.mkdir(parents=True, exist_ok=True)


def subdir(*parts: str) -> Path:
    """Return a child directory under the pipeline root (creating it)."""

    path = PIPELINE_ROOT.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path
