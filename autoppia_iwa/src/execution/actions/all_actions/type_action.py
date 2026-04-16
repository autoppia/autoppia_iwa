from typing import Any, ClassVar, Literal

from loguru import logger
from pydantic import Field, model_validator

from ..base import BaseAction, Selector
from .helpers import _ensure_page, log_action


class TypeAction(BaseAction):
    """Fills an input field identified by a selector with the given text. Clears the field first."""

    type: Literal["TypeAction"] = "TypeAction"
    browser_use_tool_name: ClassVar[str] = "input"
    text: str = Field(..., description="The text to type into the element.")
    selector: Selector | None = Field(None, description="Selector for the element to type into. Required if 'text' is not provided.")

    @model_validator(mode="before")
    @classmethod
    def map_value_to_text(cls, values):
        if "value" in values and "text" not in values:
            values["text"] = values.pop("value")
        elif "value" in values and "text" in values and values["value"] != values["text"]:
            logger.warning("Both 'text' and 'value' provided to TypeAction. Using 'text'.")
            values.pop("value")
        if "text" not in values:
            raise ValueError("TypeAction requires a 'text' field (or 'value' alias).")
        return values

    @log_action("TypeAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "TypeAction")
        if self.selector:
            sel_str = self.get_playwright_selector()
            await page.fill(sel_str, self.text)
        else:
            await page.keyboard.type(self.text)
