from functools import wraps
from typing import Any

from loguru import logger
from playwright.async_api import Page, TimeoutError as PWTimeout

action_logger = logger.bind(action="autoppia_action")
# Disable logging for agent actions execution as its so annoying
logger.disable("autoppia_action")

SELECTOR_OR_COORDS_REQUIRED_MSG = "Either a selector or (x, y) must be provided."


def log_action(action_name: str):
    """Decorator to log action execution around the `execute` call."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, page: Page | None, backend_service, web_agent_id: str):
            action_logger.debug(f"Executing {action_name} with data: {self.model_dump()}")
            return await func(self, page, backend_service, web_agent_id)

        return wrapper

    return decorator


def _ensure_page(page: Page | None, action_name: str) -> Page:
    """Checks if the page object is valid, raises ValueError otherwise."""
    if page is None:
        raise ValueError(f"{action_name} requires a valid Page object, but received None.")
    return page


async def _maybe_wait_navigation(page: Page, timeout_ms: int = 3000) -> None:
    """Optionally wait for navigation if click triggers it."""
    try:
        await page.wait_for_event("framenavigated", timeout=timeout_ms)
        await page.wait_for_load_state("domcontentloaded")
    except PWTimeout:
        pass


async def _element_center(page: Page, selector_str: str) -> tuple[int, int]:
    """Resolve selector center coordinates (scrolling into view first)."""
    loc = page.locator(selector_str)
    await loc.scroll_into_view_if_needed()
    box = await loc.bounding_box()
    if not box:
        raise ValueError("Could not resolve bounding box for selector.")
    x = int(box["x"] + box["width"] / 2)
    y = int(box["y"] + box["height"] / 2)
    return x, y


async def _move_mouse_to(page: Page, selector: str | None, x: int | None, y: int | None, steps: int = 1) -> None:
    """Move mouse to selector center or to explicit coordinates."""
    if selector:
        cx, cy = await _element_center(page, selector)
        await page.mouse.move(cx, cy, steps=steps)
        return
    if x is not None and y is not None:
        await page.mouse.move(x, y, steps=steps)
        return
    raise ValueError(SELECTOR_OR_COORDS_REQUIRED_MSG)

