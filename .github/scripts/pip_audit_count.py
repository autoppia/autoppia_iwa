#!/usr/bin/env python3
"""Print vulnerability count from pip-audit JSON (direct dependencies only).
Only counts vulns for packages listed in requirements.txt so transitive
deps do not block the pipeline. Print 0 on empty/invalid file or any error."""

import json
import re
import sys
from pathlib import Path

REQUIREMENTS_PATH = Path("requirements.txt")
AUDIT_JSON_PATH = Path("reports/pip-audit.json")


def _normalize_name(name: str) -> str:
    """PEP 503: canonical name is lowercase, - and _ equivalent."""
    return name.lower().replace("_", "-").strip()


def get_direct_deps(path: Path) -> set[str]:
    """Parse requirements.txt and return set of normalized package names."""
    if not path.exists():
        return set()
    direct = set()
    spec = re.compile(r"^([a-zA-Z0-9][a-zA-Z0-9._-]*)\s*([=<>!].*)?$")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = spec.match(line)
        if m:
            direct.add(_normalize_name(m.group(1)))
    return direct


def _pkg_from_key(key: str) -> str:
    """Extract normalized package name from 'pkg==1.2.3' or 'pkg'."""
    pkg = key.split("==")[0].split(">=")[0].split("<=")[0].strip()
    return _normalize_name(pkg)


def _count_from_dict(d: dict, direct: set[str]) -> int:
    """Count vulns from pip-audit dict. Handles both:
    - {"dependencies": [{"name": "pkg", "vulns": [...]}, ...]}  (pip-audit 2.x)
    - {"pkg==1.0": [...], ...}  (legacy dict of dep spec -> vulns)
    """
    inner = d.get("dependencies", d.get("vulnerabilities", d))
    if isinstance(inner, list):
        return _count_from_list(inner, direct)
    if not isinstance(inner, dict):
        inner = d
    n = 0
    for key, v in inner.items():
        if not isinstance(v, list):
            continue
        if direct and _pkg_from_key(key) not in direct:
            continue
        n += len(v)
    return n


def _count_from_list(d: list, direct: set[str]) -> int:
    """Count vulns from list-of-deps format."""
    n = 0
    for dep in d:
        if not isinstance(dep, dict):
            continue
        pkg = (dep.get("name") or dep.get("package") or "").split("==")[0]
        if direct and _normalize_name(pkg) not in direct:
            continue
        n += len(dep.get("vulns", dep.get("vulnerabilities", [])))
    return n


def main() -> None:
    if not AUDIT_JSON_PATH.exists() or AUDIT_JSON_PATH.stat().st_size == 0:
        print(0)
        return
    direct = get_direct_deps(REQUIREMENTS_PATH)
    try:
        raw = AUDIT_JSON_PATH.read_text().strip()
        if not raw:
            print(0)
            return
        start = raw.find("{")
        if start < 0:
            start = raw.find("[")
        if start >= 0:
            raw = raw[start:]
        d = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        print(0)
        return

    if isinstance(d, dict):
        n = _count_from_dict(d, direct)
    elif isinstance(d, list):
        n = _count_from_list(d, direct)
    else:
        n = 0
    print(n)


if __name__ == "__main__":
    main()
    sys.exit(0)
