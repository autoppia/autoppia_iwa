from typing import Any, Literal

from playwright.async_api import Error as PlaywrightError, TimeoutError as PWTimeout
from pydantic import Field

from ..base import BaseActionWithSelector
from .helpers import _ensure_page, log_action


class SelectAction(BaseActionWithSelector):
    """Selects an option in a dropdown (<select>) element."""

    type: Literal["SelectAction"] = "SelectAction"
    value: str = Field(..., description="The value, label, or index of the option to select.")

    @log_action("SelectAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SelectAction")
        sel_str = self.get_playwright_selector()
        locator = page.locator(sel_str).first
        last_error: Exception | None = None
        for strategy in ({"label": self.value}, {"value": self.value}):
            try:
                await locator.select_option(**strategy)
                return
            except (PlaywrightError, PWTimeout, ValueError, TypeError) as exc:
                last_error = exc
                continue
        try:
            index = int(str(self.value).strip())
            if index >= 0:
                await locator.select_option(index=index)
                return
        except Exception as exc:
            last_error = exc
        try:
            options = await locator.locator("option").all_inner_texts()
            target = str(self.value).strip().lower()
            for idx, option_text in enumerate(options):
                if target and target in str(option_text).strip().lower():
                    await locator.select_option(index=idx)
                    return
        except Exception as exc:
            last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError(f"Unable to select option: {self.value}")
