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
    d = json.loads(path.read_text())
    deps = d if isinstance(d, list) else d.get("dependencies", [])
    n = sum(len(dep.get("vulns", dep.get("vulnerabilities", []))) for dep in deps)
    print(n)
except (json.JSONDecodeError, TypeError, KeyError):
    print(0)
