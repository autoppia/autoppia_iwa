"""
Registry of per-project data-extraction trajectory loaders.

Separated from ``trajectory_registry.py`` so legacy event-based trajectories remain
independent of data-extraction flows.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

DataExtractionTrajectoryLoader = Callable[[], list["DataExtractionTrajectory"]]

__all__ = [
    "DATA_EXTRACTION_TRAJECTORY_LOADERS_BY_PROJECT_ID",
    "get_data_extraction_trajectories",
    "supported_data_extraction_trajectory_project_ids",
]

# WebProject.id -> package under demo_webs/projects/
_PROJECT_PACKAGES_WITH_DATA_EXTRACTION: dict[str, str] = {
    "autocinema": "p01_autocinema",
    "autobooks": "p02_autobooks",
    "autozone": "p03_autozone",
    "autodining": "p04_autodining",
    "autocrm": "p05_autocrm",
    "automail": "p06_automail",
    "autodelivery": "p07_autodelivery",
    "autolodge": "p08_autolodge",
    "autoconnect": "p09_autoconnect",
    "autowork": "p10_autowork",
    "autocalendar": "p11_autocalendar",
    "autolist": "p12_autolist",
    "autodrive": "p13_autodrive",
    "autohealth": "p14_autohealth",
    "autostats": "p15_autostats",
    "autodiscord": "p16_autodiscord",
}


def _make_data_extraction_loader(project_id: str, package: str) -> DataExtractionTrajectoryLoader:
    def _load() -> list[DataExtractionTrajectory]:
        module = importlib.import_module(f"autoppia_iwa.src.demo_webs.projects.{package}.data_extraction_trajectories")
        fn = getattr(module, f"load_{project_id}_data_extraction_trajectories")
        return fn()

    _load.__name__ = f"_load_data_extraction_{project_id}"
    return _load


DATA_EXTRACTION_TRAJECTORY_LOADERS_BY_PROJECT_ID: dict[str, DataExtractionTrajectoryLoader] = {
    project_id: _make_data_extraction_loader(project_id, package) for project_id, package in _PROJECT_PACKAGES_WITH_DATA_EXTRACTION.items()
}


def supported_data_extraction_trajectory_project_ids() -> frozenset[str]:
    return frozenset(DATA_EXTRACTION_TRAJECTORY_LOADERS_BY_PROJECT_ID.keys())


def get_data_extraction_trajectories(project_id: str) -> list[DataExtractionTrajectory] | None:
    loader = DATA_EXTRACTION_TRAJECTORY_LOADERS_BY_PROJECT_ID.get(project_id)
    if loader is None:
        return None
    return loader()
