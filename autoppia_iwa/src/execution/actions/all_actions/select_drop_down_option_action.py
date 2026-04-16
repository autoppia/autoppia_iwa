import json
from typing import Any, ClassVar, Literal

from playwright.async_api import Error as PlaywrightError, TimeoutError as PWTimeout
from pydantic import Field

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, action_logger, log_action


class SelectDropDownOptionAction(BaseActionWithSelector):
    """Selects a specific option within a <select> dropdown element by its visible text."""

    type: Literal["SelectDropDownOptionAction"] = "SelectDropDownOptionAction"
    browser_use_tool_name: ClassVar[str] = "select_dropdown"
    text: str = Field(..., description="The exact visible text of the option to select.")
    timeout_ms: int = Field(1000, description="Maximum time in milliseconds to wait for the element and option.")

    @log_action("SelectDropDownOptionAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str) -> bool:
        page = _ensure_page(page, "SelectDropDownOptionAction")
        xpath = self.get_playwright_selector()
        found = False
        last_error = None

        async def try_select(frame, frame_idx):
            nonlocal found, last_error
            try:
                select_element = await frame.wait_for_selector(
                    xpath,
                    state="attached",
                    timeout=self.timeout_ms,
                    strict=True,
                )
                tag_name = await select_element.evaluate("el => el.tagName.toLowerCase()")
                if tag_name != "select":
                    action_logger.debug(f"Element at {xpath} is {tag_name}, not SELECT (frame {frame_idx})")
                    return False

                selection_strategies = [{"label": self.text}, {"value": self.text}, {"index": await self._find_option_index(select_element, self.text)}]
                for strategy in selection_strategies:
                    try:
                        await select_element.select_option(**strategy, timeout=self.timeout_ms)
                        return True
                    except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
                        action_logger.debug(f"Selection failed with {strategy}: {e!s}")
                        last_error = str(e)
                        continue
                return False
            except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
                last_error = str(e)
                return False

        if await try_select(page.main_frame, "main"):
            return True

        for i, frame in enumerate(page.frames):
            if frame == page.main_frame:
                continue
            if await try_select(frame, i):
                return True

        if not found:
            try:
                element = await page.wait_for_selector(xpath, timeout=self.timeout_ms)
                await element.click()
                await page.wait_for_timeout(300)
                option_selector = f"xpath=//*[normalize-space(text())={json.dumps(self.text.strip())}]"
                option = await page.wait_for_selector(option_selector, timeout=self.timeout_ms)
                await option.click()
                found = True
            except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
                last_error = str(e)

        if not found:
            action_logger.error(f"Failed to select option '{self.text}'. Last error: {last_error}")

        return found

    async def _find_option_index(self, select_element, text):
        options = await select_element.query_selector_all("option")
        clean_text = text.strip().lower()
        for idx, option in enumerate(options):
            option_text = (await option.inner_text()).strip().lower()
            if clean_text in option_text:
                return idx
        return -1
