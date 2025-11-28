"""Autoppia ↔ Affine integration helpers."""

import sys
from importlib import import_module
from pathlib import Path

_affine_root = Path(__file__).resolve().parents[1]
_package_root = _affine_root / "autoppia_iwa"

for candidate in (_affine_root, _package_root):
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))


def _alias_submodule(name: str) -> None:
    alias = f"autoppia_iwa.{name}"
    if alias in sys.modules:
        return
    try:
        target = import_module(f"autoppia_iwa.autoppia_iwa.{name}")
    except ModuleNotFoundError:
        return
    sys.modules[alias] = target


_alias_submodule("src")
_alias_submodule("config")

__all__ = ["AffineEnvConfig"]


def __getattr__(name):
    if name == "AffineEnvConfig":
        from .config import AffineEnvConfig

        return AffineEnvConfig
    raise AttributeError(name)
