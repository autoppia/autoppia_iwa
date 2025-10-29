"""Lightweight exports for RL env."""

from typing import Any

_ENV_IMPORT_ERROR: Exception | None = None

try:  # pragma: no cover
    from .iwa_env import IWAWebEnv, MacroAction
except ModuleNotFoundError as exc:  # pragma: no cover
    IWAWebEnv = None  # type: ignore[assignment]
    MacroAction = None  # type: ignore[assignment]
    _ENV_IMPORT_ERROR = exc


def __getattr__(name: str) -> Any:  # pragma: no cover
    if name in {"IWAWebEnv", "MacroAction"} and _ENV_IMPORT_ERROR is not None:
        raise ModuleNotFoundError(
            "gymnasium is required to instantiate IWAWebEnv; install optional dependency",
        ) from _ENV_IMPORT_ERROR
    raise AttributeError(f"module 'rl.envs' has no attribute '{name}'")


__all__ = ["IWAWebEnv", "MacroAction"]
