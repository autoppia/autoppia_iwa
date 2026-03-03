#!/usr/bin/env python3
"""Print vulnerability count from pip-audit JSON; print 0 on empty/invalid file or any error."""

import json
import sys
from pathlib import Path

path = Path("reports/pip-audit.json")
if not path.exists() or path.stat().st_size == 0:
    print(0)
    sys.exit(0)
try:
    raw = path.read_text().strip()
    if not raw:
        print(0)
        sys.exit(0)
    # Skip leading non-JSON (e.g. stderr mixed in)
    start = raw.find("{")
    if start < 0:
        start = raw.find("[")
    if start >= 0:
        raw = raw[start:]
    d = json.loads(raw)
    # pip-audit 2.x: dict mapping dependency (e.g. "pkg==ver") -> list of vuln objects
    if isinstance(d, dict):
        # Unwrap if nested under "dependencies" or "vulnerabilities"
        inner = d.get("dependencies", d.get("vulnerabilities", d))
        n = sum(len(v) if isinstance(v, list) else 0 for v in inner.values()) if isinstance(inner, dict) else sum(len(v) if isinstance(v, list) else 0 for v in d.values())
    # fallback: list of deps with "vulns" or "vulnerabilities"
    elif isinstance(d, list):
        n = sum(len(dep.get("vulns", dep.get("vulnerabilities", []))) for dep in d)
    else:
        n = 0
    print(n)
except (json.JSONDecodeError, TypeError, KeyError):
    print(0)
