from __future__ import annotations

import argparse
import asyncio
from typing import Iterable

from ..site_capture import DEFAULT_MAX_PAGES, capture_site


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture screenshots across a web project")
    parser.add_argument("--project-slug", required=True, help="IWA project slug (e.g., dining_4)")
    parser.add_argument("--base-url", help="Override frontend URL instead of using the WebProject definition")
    parser.add_argument("--seed", type=int, help="Optional ?seed= value appended to the base URL")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help="Maximum pages to capture via auto-discovery",
    )
    parser.add_argument(
        "--include-path",
        action="append",
        default=[],
        help="Extra relative paths (e.g., /admin) to force into the capture list; can be repeated",
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="firefox",
        help="Playwright browser engine",
    )
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    asyncio.run(
        capture_site(
            args.project_slug,
            base_url=args.base_url,
            seed=args.seed,
            max_pages=args.max_pages,
            include_paths=args.include_path,
            browser=args.browser,
            headed=args.headed,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
