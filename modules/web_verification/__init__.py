"""
Alias package that forwards imports to modules.create_web_project.verification.
"""

import sys
from importlib import import_module

_real_pkg = import_module("modules.create_web_project.verification")

__all__ = getattr(_real_pkg, "__all__", [])
__path__ = _real_pkg.__path__

for name in __all__:
    globals()[name] = getattr(_real_pkg, name)

# Ensure consumers share the same module object
sys.modules[__name__] = _real_pkg
