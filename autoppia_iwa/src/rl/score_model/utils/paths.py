"""Helpers for locating package data directories."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PACKAGE_ROOT / "configs"


def package_root() -> Path:
    return PACKAGE_ROOT


def config_path(*parts: str) -> Path:
    """Return an absolute path inside the package config directory."""

    return CONFIG_DIR.joinpath(*parts)
