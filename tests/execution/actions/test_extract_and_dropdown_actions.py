from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from autoppia_iwa.src.execution.actions.all_actions.extract_action import ExtractAction
from autoppia_iwa.src.execution.actions.all_actions.get_drop_down_options_action import GetDropDownOptionsAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType


def _id_selector(value: str = "field") -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=value)


def test_extract_action_query_helpers_cover_empty_and_matches():
    assert ExtractAction._query_terms("a bb ccc 123") == ["ccc", "123"]
    assert ExtractAction._filter_text(" one \n\nTwo words\nThree ", "", 50) == "one\nTwo words\nThree"
    assert ExtractAction._filter_text("Alpha\nBeta", "zzz", 50) == "Alpha\nBeta"
    assert ExtractAction._filter_text("Alpha line\nBeta line", "beta", 50) == "Beta line"


@pytest.mark.asyncio
async def test_extract_action_selector_paths_cover_inner_text_and_html():
    locator = MagicMock()
    locator.count = AsyncMock(return_value=1)
    locator.inner_text = AsyncMock(return_value="Alpha\nBeta")
    locator.evaluate = AsyncMock(return_value="<div>Alpha</div>")
    locator.first = locator

    page = MagicMock()
    page.locator = MagicMock(return_value=locator)

    action = ExtractAction(selector=_id_selector("target"), query="alpha", include_html=False, max_chars=10)
    assert await action.execute(page, backend_service=None, web_agent_id="agent") == "Alpha"

    html_action = ExtractAction(selector=_id_selector("target"), include_html=True)
    assert await html_action.execute(page, backend_service=None, web_agent_id="agent") == "<div>Alpha</div>"


@pytest.mark.asyncio
async def test_extract_action_selector_missing_element_raises():
    locator = MagicMock()
    locator.count = AsyncMock(return_value=0)
    locator.first = locator
    page = MagicMock()
    page.locator = MagicMock(return_value=locator)

    with pytest.raises(ValueError, match="did not match any element"):
        await ExtractAction(selector=_id_selector("missing")).execute(page, backend_service=None, web_agent_id="agent")


@pytest.mark.asyncio
async def test_extract_action_page_paths_cover_body_and_content_fallback():
    body = MagicMock()
    body.count = AsyncMock(return_value=1)
    body.inner_text = AsyncMock(return_value="Body Text")
    body.first = body
    page = MagicMock()
    page.locator = MagicMock(return_value=body)
    page.content = AsyncMock(return_value="<body>fallback</body>")

    assert await ExtractAction().execute(page, backend_service=None, web_agent_id="agent") == "Body Text"

    body.count = AsyncMock(return_value=0)
    assert await ExtractAction().execute(page, backend_service=None, web_agent_id="agent") == "<body>fallback</body>"
    assert await ExtractAction(include_html=True).execute(page, backend_service=None, web_agent_id="agent") == "<body>fallback</body>"


@pytest.mark.asyncio
async def test_dropdown_options_action_covers_xpath_non_xpath_and_empty_paths():
    xpath_frame = MagicMock()
    xpath_frame.evaluate = AsyncMock(
        return_value={
            "options": [{"text": "One", "value": "1", "index": 0}],
            "id": "my-select",
            "name": "numbers",
        }
    )
    page = SimpleNamespace(frames=[xpath_frame])
    xpath_selector = Selector(type=SelectorType.XPATH_SELECTOR, value="//select")
    await GetDropDownOptionsAction(selector=xpath_selector).execute(page, backend_service=None, web_agent_id="agent")

    select_element = MagicMock()
    select_element.evaluate = AsyncMock(
        return_value={
            "options": [{"text": "Two", "value": "2", "index": 1}],
            "id": "other-select",
            "name": "other",
        }
    )
    css_frame = MagicMock()
    css_frame.wait_for_selector = AsyncMock(return_value=select_element)
    css_page = SimpleNamespace(frames=[css_frame])
    await GetDropDownOptionsAction(selector=_id_selector("country")).execute(css_page, backend_service=None, web_agent_id="agent")

    empty_frame = MagicMock()
    empty_frame.wait_for_selector = AsyncMock(return_value=None)
    empty_page = SimpleNamespace(frames=[empty_frame])
    await GetDropDownOptionsAction(selector=_id_selector("missing")).execute(empty_page, backend_service=None, web_agent_id="agent")
