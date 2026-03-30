import urllib.parse
from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import BaseAction
from .helpers import _ensure_page, log_action


class SearchAction(BaseAction):
    """Searches the web using a search engine and opens the results page."""

    type: Literal["SearchAction"] = "SearchAction"
    browser_use_tool_name: ClassVar[str] = "search"
    query: str = Field(..., description="Search query to run.")
    engine: str = Field(default="duckduckgo", description="Search engine: duckduckgo, google, or bing.")

    @log_action("SearchAction")
    async def execute(self, page, backend_service: Any, web_agent_id: str):
        page = _ensure_page(page, "SearchAction")
        engine = str(self.engine or "duckduckgo").strip().lower()
        query = urllib.parse.quote_plus(str(self.query or "").strip())
        if not query:
            raise ValueError("SearchAction requires a non-empty query.")
        search_urls = {
            "duckduckgo": f"https://duckduckgo.com/?q={query}",
            "google": f"https://www.google.com/search?q={query}&udm=14",
            "bing": f"https://www.bing.com/search?q={query}",
        }
        if engine not in search_urls:
            raise ValueError("SearchAction engine must be one of: duckduckgo, google, bing.")
        await page.goto(search_urls[engine])
