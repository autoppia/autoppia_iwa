# actions.py
import json
from functools import wraps
from typing import Any, Literal

from loguru import logger
from playwright.async_api import Page, TimeoutError as PWTimeout
from pydantic import Field, model_validator

from .base import BaseAction, BaseActionWithSelector, Selector

action_logger = logger.bind(action="autoppia_action")
# Disable logging for agent actions execution as its so annoying
logger.disable("autoppia_action")


def log_action(action_name: str):
    """Decorator to log action execution around the `execute` call."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, page: Page | None, backend_service, web_agent_id: str):
            action_logger.debug(f"Executing {action_name} with data: {self.model_dump()}")
            try:
                return await func(self, page, backend_service, web_agent_id)
            except Exception as e:
                # error_details = traceback.format_exc()
                # action_logger.error(f"{action_name} failed: {e}\n\n Traceback: {error_details}")
                # action_logger.error(f"{action_name} failed: {e}")
                raise e

        return wrapper

    return decorator


# Helper function to check for page object
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
    raise ValueError("Either a selector or (x, y) must be provided.")


# -------------------------------------------------------------------
# Concrete Action Implementations
# -------------------------------------------------------------------
class BaseClickAction(BaseActionWithSelector):
    """Base class for click-related actions that support both selector and coordinate-based clicks."""

    # Make selector optional if x,y are provided
    selector: Selector | None = Field(None, description="Selector for the element to click. Required if x, y are not provided.")
    x: int | None = Field(None, description="X-coordinate for the click, relative to the top-left corner of the viewport.")
    y: int | None = Field(None, description="Y-coordinate for the click, relative to the top-left corner of the viewport.")

    @model_validator(mode="before")
    @classmethod
    def check_selector_or_coords(cls, values):
        selector = values.get("selector")
        x, y = values.get("x"), values.get("y")
        if selector is None and (x is None or y is None):
            raise ValueError("Either 'selector' or both 'x' and 'y' coordinates must be provided for ClickAction.")
        if selector is not None and (x is not None or y is not None):
            logger.warning("Both 'selector' and coordinates (x, y) provided for ClickAction. Selector will be prioritized.")
        return values

    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        """Base implementation - must be overridden by subclasses."""
        raise NotImplementedError("BaseClickAction is abstract and should not be instantiated directly.")


class ClickAction(BaseClickAction):
    """Clicks an element identified by a selector, or at specific coordinates."""

    type: Literal["ClickAction"] = "ClickAction"

    @log_action("ClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ClickAction")

        # Click by selector
        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        # Click by coordinates
        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y)
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class DoubleClickAction(BaseClickAction):
    """Double-clicks an element identified by a selector or coordinates."""

    type: Literal["DoubleClickAction"] = "DoubleClickAction"

    @log_action("DoubleClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "DoubleClickAction")

        if self.selector:
            selector_str = self.get_playwright_selector()
            await page.dblclick(selector_str, no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.dblclick(x=self.x, y=self.y)
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class RightClickAction(BaseClickAction):
    """Right-clicks an element identified by a selector or coordinates."""

    type: Literal["RightClickAction"] = "RightClickAction"

    @log_action("RightClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "RightClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, button="right", no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, button="right")
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class MiddleClickAction(BaseClickAction):
    """Middle-clicks an element identified by a selector or coordinates."""

    type: Literal["MiddleClickAction"] = "MiddleClickAction"

    @log_action("MiddleClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MiddleClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, button="middle", no_wait_after=True)
            await _maybe_wait_navigation(page)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, button="middle")
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class TripleClickAction(BaseClickAction):
    """Triple-clicks an element identified by a selector or coordinates."""

    type: Literal["TripleClickAction"] = "TripleClickAction"

    @log_action("TripleClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "TripleClickAction")

        if self.selector:
            sel = self.get_playwright_selector()
            await page.click(sel, click_count=3, no_wait_after=True)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y, click_count=3)
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class MouseDownAction(BaseClickAction):
    """Presses the left mouse button down on a selector or at coordinates."""

    type: Literal["MouseDownAction"] = "MouseDownAction"

    @log_action("MouseDownAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseDownAction")

        sel = self.get_playwright_selector() if self.selector else None
        await _move_mouse_to(page, sel, self.x, self.y)
        await page.mouse.down(button="left")


class MouseUpAction(BaseClickAction):
    """Releases the left mouse button on a selector or at coordinates."""

    type: Literal["MouseUpAction"] = "MouseUpAction"

    @log_action("MouseUpAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseUpAction")

        sel = self.get_playwright_selector() if self.selector else None
        # If a target is provided, move to it first (keeps behavior predictable).
        if sel or (self.x is not None and self.y is not None):
            await _move_mouse_to(page, sel, self.x, self.y)
        await page.mouse.up(button="left")


class MouseMoveAction(BaseClickAction):
    """Moves the mouse to a selector center or to specific coordinates."""

    type: Literal["MouseMoveAction"] = "MouseMoveAction"
    steps: int = Field(1, description="Number of intermediate mouse move steps (animation).")

    @log_action("MouseMoveAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "MouseMoveAction")

        if self.selector:
            sel = self.get_playwright_selector()
            cx, cy = await _element_center(page, sel)
            await page.mouse.move(cx, cy, steps=self.steps)
            return

        if self.x is not None and self.y is not None:
            await page.mouse.move(self.x, self.y, steps=self.steps)
            return

        raise ValueError("Either a selector or (x, y) must be provided.")


class NavigateAction(BaseAction):
    """Navigates the browser to a URL, or goes back/forward in history."""

    type: Literal["NavigateAction"] = "NavigateAction"
    url: str | None = Field(None, description="The URL to navigate to. Required unless go_back or go_forward is true.")
    go_back: bool = Field(False, description="If true, navigates to the previous page in history.")
    go_forward: bool = Field(False, description="If true, navigates to the next page in history.")

    @model_validator(mode="before")
    @classmethod
    def check_navigation_target(cls, values):
        url = values.get("url")
        go_back = values.get("go_back", False)
        go_forward = values.get("go_forward", False)
        # Ensure exactly one navigation method is specified
        if sum([bool(url), go_back, go_forward]) != 1:
            raise ValueError("NavigateAction requires exactly one of 'url', 'go_back=True', or 'go_forward=True'.")
        return values

    @log_action("NavigateAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "NavigateAction")
        if self.go_back:
            await page.go_back()
        elif self.go_forward:
            await page.go_forward()
        elif self.url:
            await page.goto(self.url)
        else:
            raise ValueError("Invalid state: NavigateAction has no target.")


class TypeAction(BaseAction):
    """Fills an input field identified by a selector with the given text. Clears the field first."""

    type: Literal["TypeAction"] = "TypeAction"
    text: str = Field(..., description="The text to type into the element.")
    selector: Selector | None = Field(None, description="Selector for the element to type into. Required if 'text' is not provided.")

    @model_validator(mode="before")
    @classmethod
    def map_value_to_text(cls, values):
        # Allow 'value' as an alias for 'text' for backward compatibility or flexibility
        if "value" in values and "text" not in values:
            values["text"] = values.pop("value")
        elif "value" in values and "text" in values and values["value"] != values["text"]:
            logger.warning("Both 'text' and 'value' provided to TypeAction. Using 'text'.")
            values.pop("value")  # Remove the alias field
        if "text" not in values:
            raise ValueError("TypeAction requires a 'text' field (or 'value' alias).")
        return values

    @log_action("TypeAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "TypeAction")
        if self.selector:
            sel_str = self.get_playwright_selector()
            await page.fill(sel_str, self.text)
        else:
            await page.keyboard.type(self.text)


class SelectAction(BaseActionWithSelector):
    """Selects an option in a dropdown (<select>) element."""

    type: Literal["SelectAction"] = "SelectAction"
    value: str = Field(..., description="The value, label, or index of the option to select.")

    @log_action("SelectAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SelectAction")
        sel_str = self.get_playwright_selector()
        await page.select_option(sel_str, self.value)


class HoverAction(BaseActionWithSelector):
    """Hovers the mouse cursor over an element identified by a selector."""

    type: Literal["HoverAction"] = "HoverAction"

    @log_action("HoverAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "HoverAction")
        sel_str = self.get_playwright_selector()
        await page.hover(sel_str)


class WaitAction(BaseAction):
    """Waits for a specific condition: an element to appear or a fixed duration."""

    type: Literal["WaitAction"] = "WaitAction"
    selector: Selector | None = Field(None, description="Selector for an element to wait for. If provided, waits for the element.")
    time_seconds: float | None = Field(None, description="Duration in seconds to wait. If provided without a selector, pauses execution.")
    timeout_seconds: float = Field(5.0, description="Maximum time in seconds to wait for the selector.")

    @model_validator(mode="before")
    @classmethod
    def check_wait_condition(cls, values):
        selector = values.get("selector")
        time_seconds = values.get("time_seconds")
        if selector is None and time_seconds is None:
            raise ValueError("WaitAction requires either 'selector' or 'time_seconds'.")
        if selector is not None and time_seconds is not None:
            logger.warning("Both 'selector' and 'time_seconds' provided for WaitAction. Selector will be prioritized for waiting, 'time_seconds' ignored.")
        return values

    @log_action("WaitAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "WaitAction")
        if self.selector:
            selector_str = self.selector.to_playwright_selector()
            timeout_ms = self.timeout_seconds * 1000
            # Wait for visible state
            await page.wait_for_selector(selector_str, state="visible", timeout=timeout_ms)
        elif self.time_seconds is not None:
            wait_ms = self.time_seconds * 1000
            await page.wait_for_timeout(wait_ms)
        else:
            raise ValueError("Invalid state: WaitAction has no condition.")


class ScrollAction(BaseAction):
    """Scrolls the page up, down, left, right, to a text, or by a specific amount."""

    type: Literal["ScrollAction"] = "ScrollAction"

    value: str | int | None = Field(
        None,
        description=(
            "Scroll amount or target. "
            "If int: scroll by that many px in the chosen direction. "
            "If None: scroll by viewport size in the chosen direction. "
            "If str: one of {'top','bottom','left','right','max','start','end'} or text to scroll into view."
        ),
    )
    up: bool = Field(False, description="Scroll vertically up.")
    down: bool = Field(False, description="Scroll vertically down.")
    left: bool = Field(False, description="Scroll horizontally left.")
    right: bool = Field(False, description="Scroll horizontally right.")

    @model_validator(mode="before")
    @classmethod
    def _validate_directions(cls, values):
        up = bool(values.get("up", False))
        down = bool(values.get("down", False))
        left = bool(values.get("left", False))
        right = bool(values.get("right", False))
        value = values.get("value", None)

        dir_count = sum([up, down, left, right])

        # If value is int or None, require exactly one direction flag.
        if isinstance(value, int | type(None)) and dir_count != 1:
            raise ValueError("ScrollAction requires exactly one of up/down/left/right when 'value' is int or None.")
        # If value is a str keyword, we can infer direction. If it's arbitrary text, no flags are needed.
        return values

    async def _scroll_by_value(self, page: Page, dx: int, dy: int) -> None:
        """Scroll window by dx, dy."""
        await page.evaluate(
            """({dx, dy}) => { window.scrollBy(dx, dy); }""",
            {"dx": dx, "dy": dy},
        )

    @staticmethod
    async def _scroll_to_text(page: Page, text: str) -> None:
        """Scroll the page to make an element containing the given text visible."""
        locator = page.get_by_text(text, exact=False).first
        count = await locator.count()
        if count == 0:
            # Try a looser XPath contains fallback
            locator = page.locator(f"xpath=//*[contains(normalize-space(string(.)), {json.dumps(text)})]").first
            count = await locator.count()
            if count == 0:
                raise ValueError(f"Could not find text on page: {text}")
        await locator.scroll_into_view_if_needed()

    async def _scroll_to_edge(self, page: Page, axis: str, end: str) -> None:
        """Scroll to an extreme along the axis: axis in {'x','y'}, end in {'start','end'}."""
        # Use the scrolling element for consistent behavior
        script = """
            ({axis, end}) => {
              const el = document.scrollingElement || document.documentElement;
              if (axis === 'y') {
                if (end === 'start') {
                  el.scrollTop = 0;
                } else {
                  // Clamp to maximum scrollable top
                  el.scrollTop = Math.max(0, el.scrollHeight - el.clientHeight);
                }
              } else {
                if (end === 'start') {
                  el.scrollLeft = 0;
                } else {
                  // Clamp to maximum scrollable left
                  el.scrollLeft = Math.max(0, el.scrollWidth - el.clientWidth);
                }
              }
            }
        """
        await page.evaluate(script, {"axis": axis, "end": end})

    @log_action("ScrollAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ScrollAction")

        # If value is a directive string, handle it first.
        if isinstance(self.value, str):
            v = self.value.strip().lower()
            if v in {"top", "start"}:
                await self._scroll_to_edge(page, axis="y", end="start")
                return
            if v in {"bottom", "max", "end"}:
                await self._scroll_to_edge(page, axis="y", end="end")
                return
            if v in {"left"}:
                await self._scroll_to_edge(page, axis="x", end="start")
                return
            if v in {"right"}:
                await self._scroll_to_edge(page, axis="x", end="end")
                return

            # Otherwise treat it as text to scroll to.
            await self._scroll_to_text(page, self.value)
            return

        # Otherwise, we are scrolling by a numeric amount or by viewport size with a single direction flag.
        try:
            # Determine axis and sign.
            axis = "y" if (self.up or self.down) else "x"
            positive = self.down or self.right  # positive increases scrollTop/scrollLeft
            sign = 1 if positive else -1

            if isinstance(self.value, int):
                amount = abs(self.value)
            else:
                # Default step is viewport size on the chosen axis.
                if axis == "y":
                    inner = await page.evaluate("() => window.innerHeight")
                else:
                    inner = await page.evaluate("() => window.innerWidth")
                amount = int(inner) if inner else 600  # fallback

            dx, dy = (sign * amount, 0) if axis == "x" else (0, sign * amount)
            await self._scroll_by_value(page, dx=dx, dy=dy)
        except Exception as e:
            # Fallback to keyboard scroll if JS scrolling fails.
            action_logger.warning(f"ScrollAction failed with JS scrolling: {e}. Using keyboard fallback.")
            try:
                if self.left or (isinstance(self.value, str) and self.value.strip().lower() == "left"):
                    await page.keyboard.press("ArrowLeft")
                elif self.right or (isinstance(self.value, str) and self.value.strip().lower() == "right"):
                    await page.keyboard.press("ArrowRight")
                elif self.up or (isinstance(self.value, str) and self.value.strip().lower() in {"top", "start"}):
                    await page.keyboard.press("PageUp")
                else:
                    await page.keyboard.press("PageDown")
            except Exception as kb_error:
                raise ValueError(f"ScrollAction completely failed: {e}") from kb_error


class SubmitAction(BaseActionWithSelector):
    """Submits a form by pressing Enter on a specific element (usually an input inside the form)."""

    type: Literal["SubmitAction"] = "SubmitAction"

    @log_action("SubmitAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SubmitAction")
        sel_str = self.get_playwright_selector()
        await page.locator(sel_str).press("Enter")


class AssertAction(BaseAction):
    """Asserts that specific text exists within the page's main frame content."""

    type: Literal["AssertAction"] = "AssertAction"
    text_to_assert: str = Field(..., description="The text content to check for existence on the page.")

    @log_action("AssertAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "AssertAction")
        content = await page.content()
        if self.text_to_assert not in content:
            raise AssertionError(f"'{self.text_to_assert}' not found in page source.")


class DragAndDropAction(BaseAction):
    """Performs a drag-and-drop operation between two elements."""

    type: Literal["DragAndDropAction"] = "DragAndDropAction"
    source_selector: str = Field(..., alias="sourceSelector")
    target_selector: str = Field(..., alias="targetSelector")

    @log_action("DragAndDropAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "DragAndDropAction")
        await page.drag_and_drop(self.source_selector, self.target_selector)


class LeftClickDragAction(BaseAction):
    r"""Left-click drag from a start selector/(x,y) to a target selector/(x,y)."""

    type: Literal["LeftClickDragAction"] = "LeftClickDragAction"

    # Start point
    selector: Selector | None = Field(None, description="Start selector. If omitted, x/y must be provided.")
    x: int | None = Field(None, description="Start X coordinate.")
    y: int | None = Field(None, description="Start Y coordinate.")

    # Target point
    targetSelector: Selector | None = Field(None, description="Target selector. If omitted, targetX/targetY must be provided.")
    targetX: int | None = Field(None, description="Target X coordinate.")
    targetY: int | None = Field(None, description="Target Y coordinate.")

    steps: int = Field(1, description="Number of intermediate mouse move steps during the drag.")

    @model_validator(mode="before")
    @classmethod
    def _validate_points(cls, values):
        # Validate start
        has_start_sel = values.get("selector") is not None
        has_start_xy = values.get("x") is not None and values.get("y") is not None
        if not (has_start_sel or has_start_xy):
            raise ValueError("Provide a start 'selector' or both 'x' and 'y'.")

        # Validate target
        has_target_sel = values.get("targetSelector") is not None
        has_target_xy = values.get("targetX") is not None and values.get("targetY") is not None
        if not (has_target_sel or has_target_xy):
            raise ValueError("Provide a target 'targetSelector' or both 'targetX' and 'targetY'.")

        steps = values.get("steps", 1)
        try:
            steps = int(steps)
        except Exception:
            steps = 1
        values["steps"] = max(1, steps)
        return values

    @log_action("LeftClickDragAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "LeftClickDragAction")

        # Resolve start and move there
        start_selector_str = self.selector.to_playwright_selector() if self.selector else None
        await _move_mouse_to(page, start_selector_str, self.x, self.y, steps=1)

        # Press and hold left button
        await page.mouse.down(button="left")

        # Resolve target and drag
        if self.targetSelector:
            target_sel_str = self.targetSelector.to_playwright_selector()
            tx, ty = await _element_center(page, target_sel_str)
            await page.mouse.move(tx, ty, steps=self.steps)
            # Make sure we're hovering over the target element
            await page.hover(target_sel_str)
        else:
            if self.targetX is None or self.targetY is None:
                await page.mouse.up(button="left")
                raise ValueError("Target coordinates must include both 'targetX' and 'targetY'.")

            tx, ty = int(self.targetX), int(self.targetY)
            await page.mouse.move(tx, ty, steps=self.steps)

        # Wait briefly to ensure browser registers the position
        await page.wait_for_timeout(50)

        # Release the mouse button
        await page.mouse.up(button="left")


class ScreenshotAction(BaseAction):
    """Takes a screenshot of the current page."""

    type: Literal["ScreenshotAction"] = "ScreenshotAction"
    file_path: str = Field(default="", description="The file path where the screenshot should be saved.")
    full_page: bool = Field(False, description="Whether to capture the full scrollable page.")

    @log_action("ScreenshotAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ScreenshotAction")
        if self.file_path:
            await page.screenshot(path=self.file_path, full_page=self.full_page)
        else:
            await page.screenshot(full_page=self.full_page)


class SendKeysIWAAction(BaseAction):
    """Presses keyboard keys. Can be used for shortcuts or special keys."""

    type: Literal["SendKeysIWAAction"] = "SendKeysIWAAction"
    keys: str = Field(..., description="The key or key combination to press (e.g., 'Enter', 'Control+C', 'ArrowDown'). See Playwright docs for key names.")

    @log_action("SendKeysIWAAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SendKeysIWAAction")
        await page.keyboard.press(self.keys)


class HoldKeyAction(BaseAction):
    """Hold a keyboard key down, optionally for a duration, and release it."""

    type: Literal["HoldKeyAction"] = "HoldKeyAction"
    key: str = Field(..., description="Keyboard key to hold/release. Use Playwright key names.")
    duration_ms: int | float | None = Field(None, description="Optional duration in ms to hold before releasing.")
    release: bool = Field(False, description="If true, only releases the key instead of pressing it.")

    @model_validator(mode="before")
    @classmethod
    def _validate_params(cls, values):
        key = values.get("key")
        if not key or not isinstance(key, str):
            raise ValueError("A valid 'key' string is required.")
        dur = values.get("duration_ms")
        rel = values.get("release", False)
        if dur is not None and (not isinstance(dur, int | float) or dur < 0):
            raise ValueError(r"'duration_ms' must be a non-negative number if provided.")
        if rel and dur is not None:
            # Releasing with a duration is ambiguous; enforce one behavior.
            raise ValueError("Provide either 'release=True' or 'duration_ms', not both.")
        return values

    @log_action("HoldKeyAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "HoldKeyAction")

        if self.release:
            await page.keyboard.up(self.key)
            return

        await page.keyboard.down(self.key)
        if self.duration_ms is not None:
            await page.wait_for_timeout(int(self.duration_ms))
            await page.keyboard.up(self.key)


class GetDropDownOptionsAction(BaseActionWithSelector):
    """Retrieves all options (text and value) from a <select> dropdown element."""

    type: Literal["GetDropDownOptionsAction"] = "GetDropDownOptionsAction"

    @log_action("GetDropDownOptionsAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        """
        Finds the dropdown in any frame.
        """
        page = _ensure_page(page, "GetDropDownOptionsAction")
        xpath = self.get_playwright_selector()
        all_options = []
        found_dropdown = False

        for i, frame in enumerate(page.frames):
            try:
                options = await frame.evaluate(
                    """
                    (xpath) => {
                        try {
                            const select = document.evaluate(xpath, document, null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (!select) return null;
                            return {
                                options: Array.from(select.options).map(opt => ({
                                    text: opt.text.trim(),
                                    value: opt.value,
                                    index: opt.index
                                })),
                                id: select.id || null,
                                name: select.name || null
                            };
                        } catch (e) {
                            return { error: e.toString() };
                        }
                    }
                    """,
                    xpath,
                )

                if options and "error" not in options:
                    found_dropdown = True
                    action_logger.debug(f"Dropdown found in frame {i} (ID: {options.get('id')}, Name: {options.get('name')})")

                    formatted_options = [f"{opt['index']}: text={json.dumps(opt['text'])}" for opt in options["options"]]
                    all_options.extend(formatted_options)

                    # Stop searching after finding the first dropdown with options
                    break
                elif "error" in options:
                    action_logger.debug(f"Frame {i} evaluation error: {options['error']}")

            except Exception as e:
                action_logger.debug(f"Frame {i} evaluate error: {e!s}")

        if found_dropdown:
            msg = "\n".join(all_options) + "\nUse the exact string in SelectDropDownOptionAction"
            action_logger.info(msg)
        else:
            action_logger.warning("No dropdown options found in any frame.")


class SelectDropDownOptionAction(BaseActionWithSelector):
    """Selects a specific option within a <select> dropdown element by its visible text."""

    type: Literal["SelectDropDownOptionAction"] = "SelectDropDownOptionAction"
    text: str = Field(..., description="The exact visible text of the option to select.")
    timeout_ms: int = Field(1000, description="Maximum time in milliseconds to wait for the element and option.")

    @log_action("SelectDropDownOptionAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str) -> bool:
        """
        Attempts to select the dropdown option by text across frames.

        Returns:
            True if the option was successfully selected, False otherwise.
        """
        page = _ensure_page(page, "SelectDropDownOptionAction")
        xpath = self.get_playwright_selector()
        found = False
        last_error = None

        async def try_select(frame, frame_idx):
            nonlocal found, last_error
            try:
                # Wait for element with more tolerance
                select_element = await frame.wait_for_selector(
                    xpath,
                    state="attached",
                    timeout=self.timeout_ms,
                    strict=True,
                )

                # Verify element type
                tag_name = await select_element.evaluate("el => el.tagName.toLowerCase()")
                if tag_name != "select":
                    action_logger.debug(f"Element at {xpath} is {tag_name}, not SELECT (frame {frame_idx})")
                    return False

                # Try multiple selection strategies
                selection_strategies = [{"label": self.text}, {"value": self.text}, {"index": await self._find_option_index(select_element, self.text)}]

                for strategy in selection_strategies:
                    try:
                        await select_element.select_option(**strategy, timeout=self.timeout_ms)
                        return True
                    except Exception as e:
                        action_logger.debug(f"Selection failed with {strategy}: {e!s}")
                        last_error = str(e)
                        continue

                return False

            except Exception as e:
                last_error = str(e)
                return False

        # Try main frame first (most common case)
        if await try_select(page.main_frame, "main"):
            return True

        # Try other frames if needed
        for i, frame in enumerate(page.frames):
            if frame == page.main_frame:
                continue  # Already tried
            if await try_select(frame, i):
                return True

        # Fallback: Try clicking the dropdown first
        if not found:
            try:
                element = await page.wait_for_selector(xpath, timeout=self.timeout_ms)
                await element.click()
                await page.wait_for_timeout(300)  # Allow dropdown to open
                option = await page.wait_for_selector(f"//*[normalize-space(text())={self.text.strip()}]", timeout=self.timeout_ms)
                await option.click()
                found = True
            except Exception as e:
                last_error = str(e)

        if not found:
            action_logger.error(f"Failed to select option '{self.text}'. Last error: {last_error}")

        return found

    async def _find_option_index(self, select_element, text):
        """Helper to find option index by text"""
        options = await select_element.query_selector_all("option")
        clean_text = text.strip().lower()
        for idx, option in enumerate(options):
            option_text = (await option.inner_text()).strip().lower()
            if clean_text in option_text:
                return idx
        return -1


class UndefinedAction(BaseAction):
    """Represents an undefined or placeholder action. Does nothing."""

    type: Literal["UndefinedAction"] = "UndefinedAction"

    @log_action("UndefinedAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        pass


class IdleAction(BaseAction):
    """Represents an intentional idle state or pause. Does nothing."""

    type: Literal["IdleAction"] = "IdleAction"

    @log_action("IdleAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        pass


