"""
Canonical mapping from ``WebProject.id`` to the on-disk package directory
under ``autoppia_iwa.src.demo_webs.projects`` (e.g. ``autocinema`` → ``p01_autocinema``).

Use this for dynamic imports (``data_utils``, ``generation_functions``, ``use_cases``)
so renames stay consistent and imports do not rely on legacy ``{id}_{n}`` folder names.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

# WebProject.id → directory name under demo_webs/projects/
WEB_PROJECT_ID_TO_PACKAGE_DIR: Final[dict[str, str]] = {
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
}

# Old folder names (tests, docs) → current package dir
LEGACY_PACKAGE_DIR_TO_CANONICAL: Final[dict[str, str]] = {
    "autocinema_1": "p01_autocinema",
    "autobooks_2": "p02_autobooks",
    "autozone_3": "p03_autozone",
    "autodining_4": "p04_autodining",
    "autocrm_5": "p05_autocrm",
    "automail_6": "p06_automail",
    "autodelivery_7": "p07_autodelivery",
    "autolodge_8": "p08_autolodge",
    "autoconnect_9": "p09_autoconnect",
    "autowork_10": "p10_autowork",
    "autocalendar_11": "p11_autocalendar",
    "autolist_12": "p12_autolist",
    "autodrive_13": "p13_autodrive",
    "autohealth_14": "p14_autohealth",
    "autostats_15": "p15_autostats",
}


def normalize_project_package_dir(name: str) -> str:
    """Map a legacy package dir or pass through a current ``pNN_*`` name."""
    if re.fullmatch(r"p\d+_.+", name):
        return name
    return LEGACY_PACKAGE_DIR_TO_CANONICAL.get(name, name)


def resolve_demo_project_package_dir(project_id: str, *, projects_root: Path) -> str | None:
    """
    Resolve ``WebProject.id`` (or legacy dir name) to an existing package directory name.

    Order:
    1. Canonical map for ``project_id`` if that directory exists.
    2. If ``project_id`` is already a legacy dir name, normalize to ``pNN_*`` and verify.
    3. Scan for ``^p\\d+_{re.escape(project_id)}$`` (sorted).
    4. Legacy ``{project_id}_*`` directories (sorted).
    5. Exact ``projects_root / project_id``.
    """
    try:
        canonical = WEB_PROJECT_ID_TO_PACKAGE_DIR.get(project_id)
        if canonical and (projects_root / canonical).is_dir():
            return canonical

        normalized = normalize_project_package_dir(project_id)
        if normalized != project_id and (projects_root / normalized).is_dir():
            return normalized

        p_pat = re.compile(rf"^p\d+_{re.escape(project_id)}$")
        p_matches = sorted(d.name for d in projects_root.iterdir() if d.is_dir() and p_pat.match(d.name))
        if p_matches:
            return p_matches[0]

        legacy = sorted(d.name for d in projects_root.iterdir() if d.is_dir() and d.name.startswith(f"{project_id}_"))
        if legacy:
            return legacy[0]

        if (projects_root / project_id).is_dir():
            return project_id

    except OSError:
        pass

    return None
