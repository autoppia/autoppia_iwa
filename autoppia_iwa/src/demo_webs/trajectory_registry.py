"""
Registry of per-project trajectory loaders and URL remapping helpers.
"""

from __future__ import annotations

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


def remap_url_to_frontend(url: str, frontend_url: str) -> str:
    """
    Replace scheme+netloc in ``url`` with those from ``frontend_url``,
    preserving path/query/fragment.
    """

    if not url or not frontend_url:
        return url

    src = urlsplit(url)
    dst = urlsplit(frontend_url)
    return urlunsplit((dst.scheme, dst.netloc, src.path, src.query, src.fragment))


def _load_autocinema() -> dict[str, Trajectory]:
    from autoppia_iwa.src.demo_webs.projects.p01_autocinema.trajectories import load_autocinema_use_case_completion_flows

    return load_autocinema_use_case_completion_flows()


TRAJECTORY_LOADERS_BY_PROJECT_ID: dict[str, TrajectoryLoader] = {
    "autocinema": _load_autocinema,
}


def supported_trajectory_project_ids() -> frozenset[str]:
    return frozenset(TRAJECTORY_LOADERS_BY_PROJECT_ID.keys())


def get_trajectory_map(project_id: str) -> dict[str, Trajectory] | None:
    loader = TRAJECTORY_LOADERS_BY_PROJECT_ID.get(project_id)
    if loader is None:
        return None
    return loader()
