import sys
from pathlib import Path
from pkgutil import extend_path

root_dir = Path(__file__).resolve().parent
inner_pkg = root_dir / "autoppia_iwa"

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if "__path__" not in globals():
    __path__ = []  # type: ignore[misc]

__path__ = extend_path(__path__, __name__)

if inner_pkg.exists():
    inner_str = str(inner_pkg)
    if inner_str not in __path__:
        __path__.append(inner_str)
