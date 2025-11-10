#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.dynamic_proxy.runner import resolve_config_path, run_from_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run demo web mutation proxies (one process per project).")
    parser.add_argument("--config", type=Path, help="JSON file describing proxy mappings (defaults to DYNAMIC_PROXY_CONFIG or example config).")
    parser.add_argument("--project", action="append", dest="projects", help="Limit to specific project id(s).")
    parser.add_argument("--list", action="store_true", help="Print configured projects and exit.")
    args = parser.parse_args()

    config_path = resolve_config_path(args.config)
    exit_code = run_from_config(config_path, projects=args.projects, list_only=args.list)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
