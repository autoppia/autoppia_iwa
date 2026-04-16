#!/usr/bin/env python3
"""
Run the IWA benchmark under a debugger (PyCharm / VS Code / pdb).

PyCharm:
  1. Set working directory to the autoppia_iwa repo root.
  2. Interpreter: .venv of this repo.
  3. Script path: this file.
  4. Run → Debug (or set breakpoints first).

With no script arguments, defaults match a typical local AutoHealth + operator run.
Pass your own argv to override, e.g. in "Script parameters":

  http://127.0.0.1:8000 -p autohealth -t /path/to/tasks.json -o . --task-limit 1 --debug-agent
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    path = "/data/autoppia/autoppia_web_agents/concrete_actions/13_autodrive/autodrive_tasks.json"
    repo = Path(__file__).resolve().parents[1]
    tasks = Path(path).resolve()
    if len(sys.argv) == 1:
        args: list[str] = [
            "http://127.0.0.1:8000",
            "-p",
            "autodrive",
        ]
        if tasks.is_file():
            args += ["-t", str(tasks)]
        args += ["-o", str(repo), "--debug-agent", "--no-headless", "-u", "SELECT_DATE"]
        sys.argv = [sys.argv[0], *args]

    from autoppia_iwa.entrypoints.benchmark.run import main as bench_main

    bench_main()


if __name__ == "__main__":
    main()
