# actions.py
import asyncio
import json
from functools import wraps
from typing import Annotated, Any, Literal

from loguru import logger
from playwright.async_api import Page
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


# -------------------------------------------------------------------
# Concrete Action Implementations
# -------------------------------------------------------------------


class ClickAction(BaseActionWithSelector):
    """Clicks an element identified by a selector, or at specific coordinates."""

    type: Literal["ClickAction"] = "ClickAction"
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

    @log_action("ClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ClickAction")

        # Hay selector ➜ clic normal (esperamos navegación si la hay)
        if self.selector:
            selector_str = self.get_playwright_selector()

            # Espera a que la navegación termine SOLO si la hay
            async with page.expect_navigation(wait_until="networkidle"):
                await page.click(selector_str)

        # Hay coordenadas ➜ clic directo
        elif self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y)

        else:
            raise ValueError("Either a selector or (x, y) must be provided.")


class DoubleClickAction(BaseActionWithSelector):
    """Double-clicks an element identified by a selector."""

    type: Literal["DoubleClickAction"] = "DoubleClickAction"

    @log_action("DoubleClickAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "DoubleClickAction")
        selector_str = self.get_playwright_selector()
        await page.dblclick(selector_str)


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
    """Scrolls the page up, down, to an element, or by a specific amount."""

    type: Literal["ScrollAction"] = "ScrollAction"
    value: str | int | None = None
    up: bool = False
    down: bool = False

    async def _scroll_by_value(self, page: Page, value: int) -> None:
        """Scroll the page by a fixed amount."""
        try:
            if self.up:
                await page.evaluate(f"window.scrollBy(0, -{value});")
            elif self.down:
                await page.evaluate(f"window.scrollBy(0, {value});")
        except Exception as e:
            print(f"Failed to scroll by value {value}: {e}\n\n\n Retrying with fallback.")
            fallback_value = "window.innerHeight"
            if self.up:
                await page.evaluate(f"window.scrollBy(0, -{fallback_value});")
            elif self.down:
                await page.evaluate(f"window.scrollBy(0, {fallback_value});")

    @staticmethod
    async def _scroll_to_text(page: Page, text: str) -> None:
        """Scroll the page to a specific text element."""
        locators = [
            page.get_by_text(text, exact=False),
            page.locator(f"text={text}"),
            page.locator(f"//*[contains(text(), '{text}')]"),
        ]
        for locator in locators:
            try:
                if await locator.count() > 0 and await locator.first.is_visible():
                    await locator.first.scroll_into_view_if_needed()
                    # Allow time for the scroll to complete
                    await asyncio.sleep(0.5)
                    return
            except Exception as e:
                print(f"Failed to scroll to text '{text}' with locator: {e}")
                continue
        raise ValueError(f"Could not scroll to text: {text}")

    @log_action("ScrollAction")
    async def execute(self, page: Page | None, backend_service: Any, web_agent_id: str):
        """Execute the scroll action."""
        page = _ensure_page(page, "ScrollAction")
        try:
            if self.value is None:
                scroll_amount = "window.innerHeight"
                if self.up:
                    await page.evaluate(f"window.scrollBy(0, -{scroll_amount});")
                elif self.down:
                    await page.evaluate(f"window.scrollBy(0, {scroll_amount});")
            elif isinstance(self.value, int):
                await self._scroll_by_value(page, self.value)
            elif isinstance(self.value, str):
                if self.value.lower() in ["max", "bottom"]:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                else:
                    await self._scroll_to_text(page, self.value)
        except (Exception, ValueError) as e:
            print(f"ScrollAction failed: {e}. Falling back to keyboard scroll.")
            try:
                await page.keyboard.press("PageDown" if self.down else "PageUp")
            except Exception as kb_error:
                print(f"Keyboard scroll also failed: {kb_error}")
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
                option = await page.wait_for_selector(f"//option[translate(normalize-space(), ' ', '')='{self.text.replace(' ', '')}']", timeout=self.timeout_ms)
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


# -------------------------------------------------------------------
# Union Type to Handle All Actions by Discriminator
# -------------------------------------------------------------------

AllActionsUnion = Annotated[
    ClickAction
    | DoubleClickAction
    | NavigateAction
    | TypeAction
    | SelectAction
    | HoverAction
    | WaitAction
    | ScrollAction
    | SubmitAction
    | AssertAction
    | DragAndDropAction
    | ScreenshotAction
    | SendKeysIWAAction
    | GetDropDownOptionsAction
    | SelectDropDownOptionAction
    | UndefinedAction
    | IdleAction,
    Field(discriminator="type"),
]

# -------------------------------------------------------------------
# MAPS (as requested, appended at the end)
# -------------------------------------------------------------------

ACTION_CLASS_MAP_LOWER = {
    "click": ClickAction,
    "type": TypeAction,
    "hover": HoverAction,
    "navigate": NavigateAction,
    "dragAndDrop": DragAndDropAction,
    "submit": SubmitAction,
    "doubleClick": DoubleClickAction,
    "scroll": ScrollAction,
    "screenshot": ScreenshotAction,
    "wait": WaitAction,
    "assert": AssertAction,
    "select": SelectAction,
    "idle": IdleAction,
    "undefined": UndefinedAction,
    "sendkeysiwa": SendKeysIWAAction,
    "getdropdownoptionsaction": GetDropDownOptionsAction,
    "SelectDropDownOptionAction": SelectDropDownOptionAction,
}

ACTION_CLASS_MAP_CAPS = {
    "ClickAction": ClickAction,
    "TypeAction": TypeAction,
    "HoverAction": HoverAction,
    "NavigateAction": NavigateAction,
    "DragAndDropAction": DragAndDropAction,
    "SubmitAction": SubmitAction,
    "DoubleClickAction": DoubleClickAction,
    "ScrollAction": ScrollAction,
    "ScreenshotAction": ScreenshotAction,
    "WaitAction": WaitAction,
    "AssertAction": AssertAction,
    "SelectAction": SelectAction,
    "IdleAction": IdleAction,
    "UndefinedAction": UndefinedAction,
    "SendKeysIWAAction": SendKeysIWAAction,
    "GetDropDownOptionsAction": GetDropDownOptionsAction,
    "SelectDropDownOptionAction": SelectDropDownOptionAction,
}

ACTION_CLASS_MAP = {**ACTION_CLASS_MAP_CAPS, **ACTION_CLASS_MAP_LOWER}
