"""RL environment exports used by training and wrappers."""

from importlib import import_module
from typing import Any

_ENV_IMPORT_ERROR: Exception | None = None

try:  # pragma: no cover - optional dependency path
    from .agent.envs.iwa_env import IWAWebEnv, MacroAction
except ModuleNotFoundError as exc:  # pragma: no cover - handled lazily
    IWAWebEnv = None  # type: ignore[assignment]
    MacroAction = None  # type: ignore[assignment]
    _ENV_IMPORT_ERROR = exc

_OPTIONAL_ATTRS = {
    "JsInstrumentedEvaluator": (
        "autoppia_iwa.src.rl.agent.evaluators.instrumented",
        "JsInstrumentedEvaluator",
    ),
    "InstrumentationConfig": (
        "autoppia_iwa.src.rl.agent.evaluators.instrumented",
        "InstrumentationConfig",
    ),
    "InstrumentedBenchmark": (
        "autoppia_iwa.src.rl.agent.benchmark.instrumented",
        "InstrumentedBenchmark",
    ),
    "EpisodeDiagnostics": (
        "autoppia_iwa.src.rl.callbacks",
        "EpisodeDiagnostics",
    ),
}


def __getattr__(name: str) -> Any:  # pragma: no cover - simple delegation
    if name in {"IWAWebEnv", "MacroAction"}:
        if _ENV_IMPORT_ERROR is not None:
            raise ModuleNotFoundError(
                "gymnasium is required to instantiate IWAWebEnv; install optional dependency.",
            ) from _ENV_IMPORT_ERROR
        return globals()[name]
    if name in _OPTIONAL_ATTRS:
        module_path, attr_name = _OPTIONAL_ATTRS[name]
        module = import_module(module_path)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'rl' has no attribute '{name}'")


__all__ = [
    "EpisodeDiagnostics",
    "IWAWebEnv",
    "InstrumentationConfig",
    "InstrumentedBenchmark",
    "JsInstrumentedEvaluator",
    "MacroAction",
]
