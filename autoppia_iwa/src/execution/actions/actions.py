import asyncio
import json
from typing import Optional

from playwright.async_api import Page
from pydantic import Field

from autoppia_iwa.src.execution.actions.base import BaseAction, BaseActionWithSelector
from autoppia_iwa.src.execution.actions.utils import action_logger, log_action

# -----------------------------------------
# Concrete Action classes
# -----------------------------------------


class ClickAction(BaseActionWithSelector):
    class Config:
        extra = "allow"

    x: Optional[int] = None
    y: Optional[int] = None

    @log_action("ClickAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        if self.selector:
            selector = self.validate_selector()
            await page.click(selector)
        elif self.x is not None and self.y is not None:
            await page.mouse.click(self.x, self.y)
        else:
            raise ValueError("Either selector or (x, y) coordinates must be provided.")


class DoubleClickAction(BaseActionWithSelector):
    @log_action("DoubleClickAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        try:
            selector = self.validate_selector()
            await page.dblclick(selector)
        except Exception as e:
            raise RuntimeError(f"DoubleClickAction failed: {e}")


class NavigateAction(BaseAction):
    url: Optional[str] = ""
    go_back: bool = False
    go_forward: bool = False

    @log_action("NavigateAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        try:
            if self.go_back:
                await page.go_back()
            elif self.go_forward:
                await page.go_forward()
            elif not self.url:
                raise ValueError("URL must be provided for navigation.")
            else:
                await page.goto(self.url)
        except Exception as e:
            raise RuntimeError(f"NavigateAction failed: {e}")


class TypeAction(BaseActionWithSelector):
    text: str

    @log_action("TypeAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        try:
            sel = self.validate_selector()
            await page.fill(sel, self.text)
        except Exception as e:
            raise RuntimeError(f"TypeAction failed: {e}")


class SelectAction(BaseActionWithSelector):
    value: str

    @log_action("ScrollAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        sel = self.validate_selector()
        await page.select_option(sel, self.value)


class HoverAction(BaseActionWithSelector):
    @log_action("HoverAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        sel = self.validate_selector()
        await page.hover(sel)


class WaitAction(BaseActionWithSelector):
    # Wait for a specific selector or just a time in seconds
    time_seconds: Optional[float] = None

    @log_action("WaitAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        try:
            if self.selector:
                selector = self.validate_selector()
                await page.wait_for_selector(selector, timeout=self.time_seconds * 1000 if self.time_seconds else None)
            elif self.time_seconds:
                await page.wait_for_timeout(self.time_seconds * 1000)
            else:
                raise ValueError("Either selector or time_seconds must be provided.")
        except Exception:
            raise


class ScrollAction(BaseAction):
    value: Optional[str | int] = None
    up: bool = False
    down: bool = False

    @log_action("ScrollAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        if self.up:
            try:
                await page.evaluate(f"window.scrollBy(0, -{self.value});")
            except Exception:
                await page.keyboard.press("PageUp")
        elif self.down:
            try:
                await page.evaluate(f"window.scrollBy(0, {self.value});")
            except Exception:
                await page.keyboard.press("PageDown")
        else:
            locators = [
                page.get_by_text(self.value, exact=False),
                page.locator(f"text={self.value}"),
                page.locator(f"//*[contains(text(), '{self.value}')]"),
            ]

            for locator in locators:
                try:
                    # First check if element exists and is visible
                    if await locator.count() > 0 and await locator.first.is_visible():
                        await locator.first.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        return
                except Exception:
                    continue
            raise ValueError(f"Could not scroll to selector: {self.value}")


class SubmitAction(BaseActionWithSelector):
    @log_action("SubmitAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        sel = self.validate_selector()
        await page.locator(sel).press("Enter")


class AssertAction(BaseAction):
    text_to_assert: str

    @log_action("AssertAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        content = await page.content()
        if self.text_to_assert not in content:
            raise AssertionError(f"Assertion failed: '{self.text_to_assert}' not found in page source.")


class DragAndDropAction(BaseAction):
    source_selector: str = Field(..., alias="sourceSelector")
    target_selector: str = Field(..., alias="targetSelector")

    @log_action("DragAndDropAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        await page.drag_and_drop(self.source_selector, self.target_selector)


class ScreenshotAction(BaseAction):
    file_path: str

    @log_action("ScreenshotAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        await page.screenshot(path=self.file_path)


class SendKeysIWAAction(BaseAction):
    keys: str

    @log_action("SendKeysIWAAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        await page.keyboard.press(self.keys)


class GetDropDownOptions(BaseActionWithSelector):
    @log_action("GetDropDownOptions")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        """Get all options from a native dropdown"""
        xpath = self.validate_selector()
        # Frame-aware approach since we know it works
        all_options = []
        frame_index = 0

        for frame in page.frames:
            try:
                options = await frame.evaluate(
                    """
                    (xpath) => {
                        const select = document.evaluate(xpath, document, null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        if (!select) return null;

                        return {
                            options: Array.from(select.options).map(opt => ({
                                text: opt.text, //do not trim, because we are doing exact match in select_dropdown_option
                                value: opt.value,
                                index: opt.index
                            })),
                            id: select.id,
                            name: select.name
                        };
                    }
                """,
                    xpath,
                )

                if options:
                    action_logger.debug(f"Found dropdown in frame {frame_index}")
                    action_logger.debug(f'Dropdown ID: {options["id"]}, Name: {options["name"]}')

                    formatted_options = []
                    for opt in options["options"]:
                        # encoding ensures AI uses the exact string in select_dropdown_option
                        encoded_text = json.dumps(opt["text"])
                        formatted_options.append(f'{opt["index"]}: text={encoded_text}')

                    all_options.extend(formatted_options)

            except Exception as frame_e:
                action_logger.debug(f"Frame {frame_index} evaluation failed: {str(frame_e)}")

            frame_index += 1

        if all_options:
            msg = "\n".join(all_options)
            msg += "\nUse the exact text string in select_dropdown_option"
            action_logger.info(msg)
        else:
            msg = "No options found in any frame for dropdown"
            action_logger.info(msg)


class SelectDropDownOption(BaseActionWithSelector):
    text: str

    @log_action("SelectDropDownOption")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        """Select dropdown option by the text of the option you want to select"""
        xpath = self.validate_selector()
        frame_index = 0
        for frame in page.frames:
            try:
                action_logger.debug(f"Trying frame {frame_index} URL: {frame.url}")

                # First verify we can find the dropdown in this frame
                find_dropdown_js = """
                            (xpath) => {
                                try {
                                    const select = document.evaluate(xpath, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                    if (!select) return null;
                                    if (select.tagName.toLowerCase() !== 'select') {
                                        return {
                                            error: `Found element but it's a ${select.tagName}, not a SELECT`,
                                            found: false
                                        };
                                    }
                                    return {
                                        id: select.id,
                                        name: select.name,
                                        found: true,
                                        tagName: select.tagName,
                                        optionCount: select.options.length,
                                        currentValue: select.value,
                                        availableOptions: Array.from(select.options).map(o => o.text.trim())
                                    };
                                } catch (e) {
                                    return {error: e.toString(), found: false};
                                }
                            }
                        """

                dropdown_info = await frame.evaluate(find_dropdown_js, xpath)

                if dropdown_info:
                    if not dropdown_info.get("found"):
                        action_logger.error(f'Frame {frame_index} error: {dropdown_info.get("error")}')
                        continue

                    action_logger.debug(f"Found dropdown in frame {frame_index}: {dropdown_info}")

                    # "label" because we are selecting by text
                    # nth(0) to disable error thrown by strict mode
                    # timeout=1000 because we are already waiting for all network events, therefore ideally we don't need to wait a lot here (default 30s)
                    selected_option_values = await frame.locator(xpath).nth(0).select_option(label=self.text, timeout=1000)

                    msg = f"selected option {self.text} with value {selected_option_values}"
                    action_logger.info(msg + f" in frame {frame_index}")

            except Exception as frame_e:
                action_logger.error(f"Frame {frame_index} attempt failed: {str(frame_e)}")
                action_logger.error(f"Frame type: {type(frame)}")
                action_logger.error(f"Frame URL: {frame.url}")

            frame_index += 1

        msg = f"Could not select option '{self.text}' in any frame"
        action_logger.info(msg)


class UndefinedAction(BaseAction):
    @log_action("UndefinedAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        pass


class IdleAction(BaseAction):
    @log_action("IdleAction")
    async def execute(self, page: Optional[Page], backend_service, web_agent_id: str):
        pass


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
}

# Merge both dictionaries to form a complete ACTION_CLASS_MAP
ACTION_CLASS_MAP = {**ACTION_CLASS_MAP_CAPS, **ACTION_CLASS_MAP_LOWER}
