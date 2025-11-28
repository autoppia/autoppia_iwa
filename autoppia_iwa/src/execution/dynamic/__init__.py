from importlib import import_module

from .executor import DynamicPhaseConfig, DynamicPlaywrightExecutor, MutationAuditRecord

__all__ = ["DynamicPhaseConfig", "DynamicPlaywrightExecutor", "MutationAuditRecord"]


def __getattr__(name):
    if name in __all__:
        module = import_module("autoppia_iwa.src.execution.dynamic.executor")
        return getattr(module, name)
    raise AttributeError(name)
