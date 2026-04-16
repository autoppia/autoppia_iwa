from typing import Any, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class DragAndDropAction(BaseAction):
    """Performs a drag-and-drop operation between two elements."""

    type: Literal["DragAndDropAction"] = "DragAndDropAction"
    source_selector: str = Field(..., alias="sourceSelector")
    target_selector: str = Field(..., alias="targetSelector")

    @log_action("DragAndDropAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "DragAndDropAction")
        await page.drag_and_drop(self.source_selector, self.target_selector)
