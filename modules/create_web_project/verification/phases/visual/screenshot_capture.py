"""
Utilities for capturing reference screenshots of demo webs via Playwright.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

from playwright.async_api import Browser, Page, async_playwright

from autoppia_iwa.config.config import PROJECT_BASE_DIR

DEFAULT_BASE_URL = "http://localhost:8002/"
PROJECT_CHOICES = ["autozone", "autocrm"]
SCREENSHOT_DIR = PROJECT_BASE_DIR.parent / "data" / "web_verification" / "screenshots"


@dataclass
class CaptureStep:
    """Describes a navigation + screenshot step."""

    name: str
    url: str
    before_capture: Callable[[Page], Awaitable[None]] | None = None


async def _scroll_halfway(page: Page) -> None:
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
    await page.wait_for_timeout(500)


async def _ensure_cart_has_item(page: Page, base_url: str) -> None:
    await page.goto(f"{base_url}tech-1", wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(500)
    await page.click("text=Add to Cart")
    await page.wait_for_timeout(1000)


def build_steps(project: str, base_url: str) -> list[CaptureStep]:
    base_url = base_url.rstrip("/") + "/"
    if project == "autocrm":
        return [
            CaptureStep("dashboard", base_url),
            CaptureStep("matters", f"{base_url}matters"),
            CaptureStep("matter_detail", f"{base_url}matters/1"),
            CaptureStep("clients", f"{base_url}clients"),
            CaptureStep("documents", f"{base_url}documents"),
            CaptureStep("billing", f"{base_url}billing"),
        ]

    return [
        CaptureStep("home", base_url, before_capture=_scroll_halfway),
        CaptureStep("search_ssd", f"{base_url}search?q=ssd"),
        CaptureStep("product_tech1", f"{base_url}tech-1", before_capture=_scroll_halfway),
        CaptureStep("cart", f"{base_url}cart"),
        CaptureStep("checkout", f"{base_url}checkout"),
    ]


async def capture_pages(project: str, base_url: str, browser_name: str, headless: bool) -> None:
    project_dir = SCREENSHOT_DIR / project
    project_dir.mkdir(parents=True, exist_ok=True)
    steps = build_steps(project, base_url)

    async with async_playwright() as playwright:
        browser_launcher = getattr(playwright, browser_name)
        launch_args = ["--no-sandbox", "--disable-setuid-sandbox"] if browser_name == "chromium" else None
        browser: Browser = await browser_launcher.launch(headless=headless, args=launch_args)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        if project == "autozone":
            await _ensure_cart_has_item(page, base_url)

        for step in steps:
            await page.goto(step.url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(1000)
            if step.before_capture:
                await step.before_capture(page)
            target = project_dir / f"{project}_{step.name}.png"
            await page.screenshot(path=target.as_posix(), full_page=True)
            print(f"Saved {target}")

        await browser.close()


def capture_sync(project: str, base_url: str, browser: str, headed: bool) -> None:
    asyncio.run(capture_pages(project, base_url, browser, not headed))
