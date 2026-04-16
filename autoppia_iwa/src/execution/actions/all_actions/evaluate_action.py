from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class EvaluateAction(BaseAction):
    """Executes JavaScript on the current page and returns the raw result."""

    type: Literal["EvaluateAction"] = "EvaluateAction"
    browser_use_tool_name: ClassVar[str] = "evaluate"
    script: str = Field(..., description="JavaScript expression or function body to evaluate in the page context.")
    arg: Any = Field(default=None, description="Optional argument passed to the evaluated script.")

    @model_validator(mode="before")
    @classmethod
    def _normalize_script_aliases(cls, values):
        if "expression" in values and "script" not in values:
            values["script"] = values.pop("expression")
        return values

    @log_action("EvaluateAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "EvaluateAction")
        if self.arg is None:
            return await page.evaluate(self.script)
        return await page.evaluate(self.script, self.arg)
