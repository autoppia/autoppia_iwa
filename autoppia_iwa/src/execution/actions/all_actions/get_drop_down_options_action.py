import json
from typing import Any, ClassVar, Literal

from playwright.async_api import Error as PlaywrightError, TimeoutError as PWTimeout

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, action_logger, log_action


class GetDropDownOptionsAction(BaseActionWithSelector):
    """Retrieves all options (text and value) from a <select> dropdown element."""

    type: Literal["GetDropDownOptionsAction"] = "GetDropDownOptionsAction"
    browser_use_tool_name: ClassVar[str] = "dropdown_options"

    @log_action("GetDropDownOptionsAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "GetDropDownOptionsAction")
        playwright_selector = self.get_playwright_selector()
        all_options = []
        found_dropdown = False

        raw_xpath = None
        if playwright_selector.startswith("xpath="):
            raw_xpath = playwright_selector[6:]
        elif playwright_selector.startswith("//") or playwright_selector.startswith("(//"):
            raw_xpath = playwright_selector
        else:
            action_logger.debug(f"Non-XPath selector detected: {playwright_selector}, attempting conversion")

        for i, frame in enumerate(page.frames):
            try:
                if raw_xpath:
                    options = await frame.evaluate(
                        """
                        (xpath) => {
                            try {
                                const select = document.evaluate(xpath, document, null,
                                    XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                                if (!select) return null;
                                if (select.tagName.toLowerCase() !== 'select') return null;
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
                        raw_xpath,
                    )
                else:
                    try:
                        select_element = await frame.wait_for_selector(
                            playwright_selector,
                            state="attached",
                            timeout=2000,
                            strict=False,
                        )
                        if select_element:
                            options = await select_element.evaluate(
                                """
                                (select) => {
                                    if (select.tagName.toLowerCase() !== 'select') return null;
                                    return {
                                        options: Array.from(select.options).map(opt => ({
                                            text: opt.text.trim(),
                                            value: opt.value,
                                            index: opt.index
                                        })),
                                        id: select.id || null,
                                        name: select.name || null
                                    };
                                }
                                """
                            )
                        else:
                            options = None
                    except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
                        action_logger.debug(f"Frame {i} Playwright selector evaluation failed: {e!s}")
                        options = None

                if options and "error" not in options and options.get("options"):
                    found_dropdown = True
                    action_logger.debug(f"Dropdown found in frame {i} (ID: {options.get('id')}, Name: {options.get('name')})")
                    formatted_options = [f"{opt['index']}: text={json.dumps(opt['text'])}" for opt in options["options"]]
                    all_options.extend(formatted_options)
                    break
                elif options and "error" in options:
                    action_logger.debug(f"Frame {i} evaluation error: {options['error']}")
                elif options and not options.get("options"):
                    action_logger.debug(f"Frame {i}: Element found but has no options or is not a select element")
            except (PlaywrightError, PWTimeout, ValueError, TypeError) as e:
                action_logger.debug(f"Frame {i} evaluate error: {e!s}")

        if found_dropdown:
            msg = "\n".join(all_options) + "\nUse the exact string in SelectDropDownOptionAction"
            action_logger.info(msg)
        else:
            action_logger.warning(f"No dropdown options found in any frame. Selector used: {playwright_selector}")
