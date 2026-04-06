"""
Registry of per-project trajectory loaders and helpers to align hardcoded demo URLs
with the active WebProject.frontend_url.

Lives under ``demo_webs/`` (not ``web_verification/``) so imports avoid loading the
full verification pipeline package ``__init__``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit

if TYPE_CHECKING:
    from autoppia_iwa.src.demo_webs.classes import Trajectory

TrajectoryLoader = Callable[[], dict[str, "Trajectory"]]


def remap_url_to_frontend(url: str, frontend_url: str) -> str:
    """
    Replace scheme and netloc of ``url`` with those of ``frontend_url``,
    preserving path, query, and fragment (including ``seed=``).
    """
    if not url or not frontend_url:
        return url
    src = urlsplit(url)
    base = urlsplit(frontend_url)
    return urlunsplit((base.scheme, base.netloc, src.path, src.query, src.fragment))


def _load_autolist() -> dict[str, Trajectory]:
    from autoppia_iwa.src.demo_webs.projects.p12_autolist.trajectories import load_autolist_use_case_completion_flows

    return load_autolist_use_case_completion_flows()


def _load_autodrive() -> dict[str, Trajectory]:
    from autoppia_iwa.src.demo_webs.projects.p13_autodrive.trajectories import load_autodrive_use_case_completion_flows

    return load_autodrive_use_case_completion_flows()


def _load_autohealth() -> dict[str, Trajectory]:
    from autoppia_iwa.src.demo_webs.projects.p14_autohealth.trajectories import load_autohealth_use_case_completion_flows

    return load_autohealth_use_case_completion_flows()


def _load_autocalendar() -> dict[str, Trajectory]:
    from autoppia_iwa.src.demo_webs.projects.p11_autocalendar.trajectories import load_autocalendar_use_case_completion_flows

    return load_autocalendar_use_case_completion_flows()


# Project ``id`` (WebProject.id) -> lazy loader
TRAJECTORY_LOADERS_BY_PROJECT_ID: dict[str, TrajectoryLoader] = {
    "autocalendar": _load_autocalendar,
    "autolist": _load_autolist,
    "autodrive": _load_autodrive,
    "autohealth": _load_autohealth,
}


def supported_trajectory_project_ids() -> frozenset[str]:
    return frozenset(TRAJECTORY_LOADERS_BY_PROJECT_ID.keys())


def get_trajectory_map(project_id: str) -> dict[str, Trajectory] | None:
    """
    Return use_case_name -> Trajectory for projects that define ``trajectories.py``.
    Returns ``None`` if this project has no registered loader.
    """
    loader = TRAJECTORY_LOADERS_BY_PROJECT_ID.get(project_id)
    if loader is None:
        return None
    return loader()
