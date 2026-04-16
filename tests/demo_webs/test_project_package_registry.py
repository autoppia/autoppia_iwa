"""Tests for demo_webs.project_package_registry."""

from pathlib import Path

from autoppia_iwa.src.demo_webs.project_package_registry import (
    WEB_PROJECT_ID_TO_PACKAGE_DIR,
    normalize_project_package_dir,
    resolve_demo_project_package_dir,
)


def test_normalize_legacy_to_p_prefixed():
    assert normalize_project_package_dir("autohealth_14") == "p14_autohealth"
    assert normalize_project_package_dir("p14_autohealth") == "p14_autohealth"


def test_resolve_by_web_project_id(tmp_path: Path):
    (tmp_path / "p14_autohealth").mkdir()
    assert resolve_demo_project_package_dir("autohealth", projects_root=tmp_path) == "p14_autohealth"


def test_resolve_legacy_dir_name_input(tmp_path: Path):
    (tmp_path / "p01_autocinema").mkdir()
    assert resolve_demo_project_package_dir("autocinema_1", projects_root=tmp_path) == "p01_autocinema"


def test_registry_covers_all_demo_projects():
    assert set(WEB_PROJECT_ID_TO_PACKAGE_DIR) == {
        "autocinema",
        "autobooks",
        "autozone",
        "autodining",
        "autocrm",
        "automail",
        "autodelivery",
        "autolodge",
        "autoconnect",
        "autowork",
        "autocalendar",
        "autolist",
        "autodrive",
        "autohealth",
        "autostats",
    }
