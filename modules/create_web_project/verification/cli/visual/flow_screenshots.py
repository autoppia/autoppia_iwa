from __future__ import annotations

import argparse
import asyncio
from typing import Iterable

from ...phases.visual.screenshot_capture import (
    DEFAULT_BASE_URL,
    PROJECT_CHOICES,
    capture_pages,
)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a predefined flow's screenshots (demo web).")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL hosting the demo project")
    parser.add_argument(
        "--project",
        choices=PROJECT_CHOICES,
        default="autozone",
        help="Which predefined flow to capture",
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="firefox",
        help="Playwright browser engine",
    )
    parser.add_argument("--headed", action="store_true", help="Run browsers in headed mode")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    asyncio.run(capture_pages(args.project, args.base_url, args.browser, not args.headed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
