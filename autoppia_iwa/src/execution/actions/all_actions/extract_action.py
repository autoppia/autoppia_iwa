import re
from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import BaseAction, Selector
from .helpers import _ensure_page, log_action


class ExtractAction(BaseAction):
    """Extracts deterministic text from the page, optionally filtered by a query or selector."""

    type: Literal["ExtractAction"] = "ExtractAction"
    browser_use_tool_name: ClassVar[str] = "extract"
    query: str = Field(default="", description="Optional query used to filter the extracted content.")
    selector: Selector | None = Field(None, description="Optional selector to scope extraction.")
    include_html: bool = Field(False, description="If true, returns HTML instead of visible text.")
    max_chars: int = Field(4000, description="Maximum characters to return.")

    @staticmethod
    def _query_terms(query: str) -> list[str]:
        return [term for term in re.findall(r"[A-Za-z0-9]{3,}", str(query or "").lower()) if term]

    @classmethod
    def _filter_text(cls, text: str, query: str, max_chars: int) -> str:
        collapsed = "\n".join(line.strip() for line in str(text or "").splitlines() if line.strip())
        if not query.strip():
            return collapsed[:max_chars]
        terms = cls._query_terms(query)
        if not terms:
            return collapsed[:max_chars]
        matched_lines: list[str] = []
        for line in collapsed.splitlines():
            lowered = line.lower()
            if any(term in lowered for term in terms):
                matched_lines.append(line)
        if matched_lines:
            return "\n".join(matched_lines)[:max_chars]
        return collapsed[:max_chars]

    @log_action("ExtractAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "ExtractAction")
        max_chars = max(200, min(int(self.max_chars or 4000), 20000))
        if self.selector:
            selector_str = self.selector.to_playwright_selector()
            locator = page.locator(selector_str).first
            if await locator.count() == 0:
                raise ValueError("ExtractAction selector did not match any element.")
            if self.include_html:
                content = await locator.evaluate("(el) => el.outerHTML")
            else:
                content = await locator.inner_text()
            return self._filter_text(str(content or ""), self.query, max_chars)

        if self.include_html:
            content = await page.content()
        else:
            body = page.locator("body").first
            content = await body.inner_text() if await body.count() else await page.content()
        return self._filter_text(str(content or ""), self.query, max_chars)
