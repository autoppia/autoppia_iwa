from __future__ import annotations

import importlib
import inspect
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from playwright.async_api import Browser, Page, async_playwright

from autoppia_iwa.src.demo_webs.classes import WebProject

SCREENSHOT_ROOT = Path("data") / "web_verification" / "screenshots"
MODULE_PREFIX = "autoppia_iwa.src.demo_webs.projects"
DEFAULT_MAX_PAGES = 12


def _load_web_project(project_slug: str) -> WebProject:
    main_module = importlib.import_module(f"{MODULE_PREFIX}.{project_slug}.main")
    web_project = _discover_web_project(main_module)
    if not web_project:
        raise RuntimeError(f"No WebProject found for slug '{project_slug}'")
    return web_project


def _discover_web_project(module) -> WebProject | None:
    for _, value in inspect.getmembers(module):
        if isinstance(value, WebProject):
            return value
    return None


def _attach_seed(url: str, seed: int | None) -> str:
    if seed is None:
        return url
    parts = list(urlsplit(url))
    query = parts[3]
    query = f"{query}&seed={seed}" if query else f"seed={seed}"
    parts[3] = query
    return urlunsplit(parts)


def _normalize_url(base_url: str, href: str) -> str:
    if href.startswith(("http://", "https://")):
        return href
    return urljoin(base_url, href)


def _slugify_url(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path.strip("/") or "home"
    safe_path = path.replace("/", "_").replace("?", "_").replace("=", "_")
    return safe_path[:80]


async def _discover_routes(page: Page, start_url: str, max_pages: int) -> list[str]:
    origin = urlsplit(start_url)
    origin_netloc = origin.netloc
    queue = [start_url]
    seen: set[str] = set()
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception:
            continue
        discovered.append(url)
        anchors = await page.eval_on_selector_all(
            "a[href]",
            "els => els.map(a => a.href)",
        )
        for href in anchors:
            normalized = _normalize_url(start_url, href)
            parsed = urlsplit(normalized)
            if parsed.netloc and parsed.netloc != origin_netloc:
                continue
            normalized = urlunsplit((origin.scheme, origin.netloc, parsed.path, parsed.query, parsed.fragment))
            if normalized in seen or normalized in queue:
                continue
            if len(discovered) + len(queue) >= max_pages:
                continue
            queue.append(normalized)
    return discovered


async def _capture_pages(
    project_id: str,
    urls: list[str],
    browser_name: str,
    headless: bool,
    screenshot_dir: Path,
) -> None:
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser_launcher = getattr(p, browser_name)
        browser: Browser = await browser_launcher.launch(headless=headless)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        for idx, url in enumerate(urls):
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(1000)
                filename = screenshot_dir / f"{idx:02d}_{_slugify_url(url)}.png"
                await page.screenshot(path=filename.as_posix(), full_page=True)
                print(f"[{project_id}] saved {filename}")
            except Exception as exc:  # pragma: no cover - best effort logging
                print(f"[{project_id}] failed to capture {url}: {exc}")
        await browser.close()


async def capture_site(
    project_slug: str,
    *,
    base_url: str | None = None,
    seed: int | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
    include_paths: Iterable[str] | None = None,
    browser: str = "firefox",
    headed: bool = False,
) -> Path:
    """Capture screenshots for a web project, auto-discovering routes."""
    web_project = _load_web_project(project_slug)
    target_base = base_url or getattr(web_project, "frontend_url", "")
    if not target_base:
        raise RuntimeError("Frontend URL is not configured; pass --base-url explicitly.")
    target_base = _attach_seed(target_base, seed)

    async with async_playwright() as p:
        browser_launcher = getattr(p, browser)
        browser_instance: Browser = await browser_launcher.launch(headless=not headed)
        page = await browser_instance.new_page(viewport={"width": 1440, "height": 900})
        discovered = await _discover_routes(page, target_base, max_pages)
        await browser_instance.close()

    extra_urls = [_normalize_url(target_base, path) for path in include_paths or []]
    all_urls = list(dict.fromkeys(discovered + extra_urls))
    project_id = getattr(web_project, "id", project_slug).lower()
    screenshot_dir = SCREENSHOT_ROOT / project_id
    await _capture_pages(project_id, all_urls, browser, not headed, screenshot_dir)
    return screenshot_dir
