#!/usr/bin/env python3
"""
Debug the ``iwa generate-tasks`` entrypoint for one project and optional use-case filter.

Delegates to ``autoppia_iwa.entrypoints.generate_tasks.run`` (same code path as
``python -m autoppia_iwa.entrypoints.generate_tasks.run``).

CLI (from autoppia_iwa repo root; requires LLM credentials, see ``_require_llm_credentials``):

  python scripts/debug_generate_tasks.py -p autolist -u AUTOLIST_ADD_TASK_CLICKED -n 1 -o debug_tasks.json
  python scripts/debug_generate_tasks.py -p autodrive -u SELECT_DATE -n 2

PyCharm:
  1. Working directory: autoppia_iwa repo root.
  2. Interpreter: this repo's ``.venv`` (with ``OPENAI_API_KEY`` or Chutes env as needed).
  3. Script path: ``scripts/debug_generate_tasks.py``.
  4. Script parameters: e.g. ``-p autolist -u AUTOLIST_ADD_TASK_CLICKED -n 1 -o debug_tasks.json``.
  5. Run → Debug; set breakpoints in ``entrypoints/generate_tasks/run.py`` or
     ``src/data_generation/tasks/pipeline.py``.

If you Debug with **no** script parameters, defaults are applied:
``-p autolist -u AUTOLIST_ADD_TASK_CLICKED -n 1 -o debug_generate_tasks.json``.

PyCharm script path (repo root): scripts/debug_generate_tasks.py
"""

from __future__ import annotations

import asyncio
import sys


def main() -> int:
    if len(sys.argv) == 1:
        sys.argv.extend(
            [
                "-p",
                "autolist",
                "-u",
                "AUTOLIST_CANCEL_TASK_CREATION",
                "-n",
                "1",
                "-o",
                "debug_generate_tasks.json",
            ]
        )

    from autoppia_iwa.entrypoints.generate_tasks.run import _main_async, _parse_args

    return asyncio.run(_main_async(_parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
