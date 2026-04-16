from typing import Any

from loguru import logger
from playwright.async_api import Page
from pydantic import Field, model_validator

from ..base import BaseActionWithSelector, Selector


class BaseClickAction(BaseActionWithSelector):
    """Base class for click-related actions that support both selector and coordinate-based clicks."""

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
        raise NotImplementedError("BaseClickAction is abstract and should not be instantiated directly.")
