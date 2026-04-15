"""
Registry of per-project trajectory loaders and helpers to align hardcoded demo URLs
with the active ``WebProject.frontend_url``.

Lives under ``demo_webs/`` (not ``web_verification/``) so imports avoid loading the
full verification pipeline package ``__init__``.

Each ``WebProject.id`` maps to ``projects/pNN_<name>/trajectories.py`` and the
exported ``load_<id>_use_case_completion_flows()`` (see ``_PROJECT_PACKAGES``).

Registered project IDs include (non-exhaustive): ``autocinema`` … ``automail`` (p01-p07),
``autolodge`` (p08), ``autoconnect`` (p09), ``autocalendar`` (p11), ``autolist`` (p12),
``autodrive`` (p13), ``autohealth`` (p14).
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit

if TYPE_CHECKING:
    from autoppia_iwa.src.demo_webs.classes import Trajectory

TrajectoryLoader = Callable[[], dict[str, "Trajectory"]]

__all__ = [
    "TRAJECTORY_LOADERS_BY_PROJECT_ID",
    "get_trajectory_map",
    "remap_url_to_frontend",
    "supported_trajectory_project_ids",
]

# WebProject.id -> package directory under ``demo_webs/projects/`` (lazy import target).
_PROJECT_PACKAGES: dict[str, str] = {
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
}


def _make_trajectory_loader(project_id: str, package: str) -> TrajectoryLoader:
    """Build a lazy loader that imports ``load_<project_id>_use_case_completion_flows``."""

    def _load() -> dict[str, Trajectory]:
        module = importlib.import_module(f"autoppia_iwa.src.demo_webs.projects.{package}.trajectories")
        fn = getattr(module, f"load_{project_id}_use_case_completion_flows")
        return fn()

    _load.__name__ = f"_load_{project_id}"
    _load.__doc__ = f"Load golden trajectories for WebProject.id {project_id!r}."
    return _load


TRAJECTORY_LOADERS_BY_PROJECT_ID: dict[str, TrajectoryLoader] = {pid: _make_trajectory_loader(pid, pkg) for pid, pkg in _PROJECT_PACKAGES.items()}


def remap_url_to_frontend(url: str, frontend_url: str) -> str:
    """
    Replace scheme and netloc of ``url`` with those of ``frontend_url``,
    preserving path, query, and fragment (including ``seed=``).

    Empty or whitespace-only ``frontend_url`` leaves ``url`` unchanged.
    """
    if not (url or "").strip() or not (frontend_url or "").strip():
        return url
    src = urlsplit(url.strip())
    base = urlsplit(frontend_url.strip())
    if not base.scheme or not base.netloc:
        return url
    return urlunsplit((base.scheme, base.netloc, src.path, src.query, src.fragment))


def supported_trajectory_project_ids() -> frozenset[str]:
    """Immutable set of ``WebProject.id`` values with a trajectory loader."""
    return frozenset(TRAJECTORY_LOADERS_BY_PROJECT_ID.keys())


def get_trajectory_map(project_id: str) -> dict[str, Trajectory] | None:
    """
    Return ``use_case_name`` -> :class:`Trajectory` for projects that define
    ``trajectories.py``. Returns ``None`` if this project has no registered loader.
    """
    loader = TRAJECTORY_LOADERS_BY_PROJECT_ID.get(project_id)
    if loader is None:
        return None
    return loader()
