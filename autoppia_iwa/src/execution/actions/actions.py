# actions.py
import asyncio
import json
from functools import wraps
from typing import Annotated, Literal

from loguru import logger
from playwright.async_api import Page
from pydantic import Field

# Use your new combined base classes
from autoppia_iwa.src.execution.actions.base import BaseAction, BaseActionWithSelector

action_logger = logger.bind(action="autoppia_action")
logger.disable("autoppia_action")  # Disable logging for agent actions execution as its so annoying


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


# -------------------------------------------------------------------
# Concrete Actions
# -------------------------------------------------------------------


class ClickAction(BaseActionWithSelector):
    type: Literal["ClickAction"] = "ClickAction"
    x: int | None = None
    y: int | None = None

    @log_action("ClickAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        if self.selector:
            selector_str = self.validate_selector()
            await page.click(selector_str)
        elif self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y)
        else:
            raise ValueError("Either a selector or (x, y) must be provided.")


class DoubleClickAction(BaseActionWithSelector):
    type: Literal["DoubleClickAction"] = "DoubleClickAction"

    @log_action("DoubleClickAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        selector_str = self.validate_selector()
        await page.dblclick(selector_str)


class NavigateAction(BaseAction):
    type: Literal["NavigateAction"] = "NavigateAction"
    url: str | None = ""
    go_back: bool = False
    go_forward: bool = False

    @log_action("NavigateAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        if self.go_back:
            await page.go_back()
        elif self.go_forward:
            await page.go_forward()
        elif not self.url:
            raise ValueError("URL must be provided for navigation.")
        else:
            await page.goto(self.url)


class TypeAction(BaseActionWithSelector):
    type: Literal["TypeAction"] = "TypeAction"
    text: str

    @log_action("TypeAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        sel_str = self.validate_selector()
        await page.fill(sel_str, self.text)


class SelectAction(BaseActionWithSelector):
    type: Literal["SelectAction"] = "SelectAction"
    value: str

    @log_action("SelectAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        sel_str = self.validate_selector()
        await page.select_option(sel_str, self.value)


class HoverAction(BaseActionWithSelector):
    type: Literal["HoverAction"] = "HoverAction"

    @log_action("HoverAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        sel_str = self.validate_selector()
        await page.hover(sel_str)


class WaitAction(BaseActionWithSelector):
    type: Literal["WaitAction"] = "WaitAction"
    time_seconds: float | None = None

    @log_action("WaitAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        if self.selector:
            sel_str = self.validate_selector()
            await page.wait_for_selector(sel_str, timeout=self.time_seconds * 1000 if self.time_seconds else None)
        elif self.time_seconds:
            await page.wait_for_timeout(self.time_seconds * 1000)
        else:
            raise ValueError("Either selector or time_seconds must be provided.")


class ScrollAction(BaseAction):
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
                    await asyncio.sleep(0.5)  # Allow time for the scroll to complete
                    return
            except Exception as e:
                print(f"Failed to scroll to text '{text}' with locator: {e}")
                continue
        raise ValueError(f"Could not scroll to text: {text}")

    @log_action("ScrollAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str) -> None:
        """Execute the scroll action."""
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
    type: Literal["SubmitAction"] = "SubmitAction"

    @log_action("SubmitAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        sel_str = self.validate_selector()
        await page.locator(sel_str).press("Enter")


class AssertAction(BaseAction):
    type: Literal["AssertAction"] = "AssertAction"
    text_to_assert: str

    @log_action("AssertAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        content = await page.content()
        if self.text_to_assert not in content:
            raise AssertionError(f"'{self.text_to_assert}' not found in page source.")


class DragAndDropAction(BaseAction):
    type: Literal["DragAndDropAction"] = "DragAndDropAction"
    source_selector: str = Field(..., alias="sourceSelector")
    target_selector: str = Field(..., alias="targetSelector")

    @log_action("DragAndDropAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        await page.drag_and_drop(self.source_selector, self.target_selector)


class ScreenshotAction(BaseAction):
    type: Literal["ScreenshotAction"] = "ScreenshotAction"
    file_path: str

    @log_action("ScreenshotAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        await page.screenshot(path=self.file_path)


class SendKeysIWAAction(BaseAction):
    type: Literal["SendKeysIWAAction"] = "SendKeysIWAAction"
    keys: str

    @log_action("SendKeysIWAAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        await page.keyboard.press(self.keys)


class GetDropDownOptionsAction(BaseActionWithSelector):
    type: Literal["GetDropDownOptionsAction"] = "GetDropDownOptionsAction"

    @log_action("GetDropDownOptionsAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        xpath = self.validate_selector()
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
    type: Literal["SelectDropDownOptionAction"] = "SelectDropDownOptionAction"
    text: str
    timeout_ms: int = 1000

    @log_action("SelectDropDownOptionAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        xpath = self.validate_selector()
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
    type: Literal["UndefinedAction"] = "UndefinedAction"

    @log_action("UndefinedAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
        pass


class IdleAction(BaseAction):
    type: Literal["IdleAction"] = "IdleAction"

    @log_action("IdleAction")
    async def execute(self, page: Page | None, backend_service, web_agent_id: str):
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
