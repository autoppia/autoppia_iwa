from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from playwright.async_api import TimeoutError as PWTimeout

from autoppia_iwa.src.execution.actions.all_actions.select_drop_down_option_action import (
    SelectDropDownOptionAction,
)
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType


def _selector() -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value="//select[@id='pet-select']")


@pytest.mark.asyncio
async def test_select_dropdown_uses_index_strategy_after_label_and_value_fail():
    option_cat = SimpleNamespace(inner_text=AsyncMock(return_value="Cat"))
    option_dog = SimpleNamespace(inner_text=AsyncMock(return_value="Dog"))
    select_element = SimpleNamespace(
        evaluate=AsyncMock(return_value="select"),
        query_selector_all=AsyncMock(return_value=[option_cat, option_dog]),
    )
    select_element.select_option = AsyncMock(side_effect=[ValueError("label"), TypeError("value"), None])

    frame = SimpleNamespace(wait_for_selector=AsyncMock(return_value=select_element))
    page = SimpleNamespace(main_frame=frame, frames=[frame])

    action = SelectDropDownOptionAction(selector=_selector(), text="Dog", timeout_ms=50)
    result = await action.execute(page=page, backend_service=None, web_agent_id="t")

    assert result is True
    assert select_element.select_option.await_count == 3
    assert select_element.select_option.await_args_list[2].kwargs["index"] == 1


@pytest.mark.asyncio
async def test_select_dropdown_falls_back_to_clicking_visible_option():
    frame = SimpleNamespace(wait_for_selector=AsyncMock(side_effect=PWTimeout("missing select")))
    clicked_select = SimpleNamespace(click=AsyncMock())
    clicked_option = SimpleNamespace(click=AsyncMock())
    page = SimpleNamespace(
        main_frame=frame,
        frames=[frame],
        wait_for_selector=AsyncMock(side_effect=[clicked_select, clicked_option]),
        wait_for_timeout=AsyncMock(),
    )

    action = SelectDropDownOptionAction(selector=_selector(), text="Dog", timeout_ms=50)
    result = await action.execute(page=page, backend_service=None, web_agent_id="t")

    assert result is True
    clicked_select.click.assert_awaited_once()
    clicked_option.click.assert_awaited_once()
    page.wait_for_timeout.assert_awaited_once_with(300)


@pytest.mark.asyncio
async def test_select_dropdown_returns_false_when_not_select_and_fallback_fails():
    element = SimpleNamespace(evaluate=AsyncMock(return_value="div"))
    frame = SimpleNamespace(wait_for_selector=AsyncMock(return_value=element))
    page = SimpleNamespace(
        main_frame=frame,
        frames=[frame],
        wait_for_selector=AsyncMock(side_effect=PWTimeout("still missing")),
        wait_for_timeout=AsyncMock(),
    )

    action = SelectDropDownOptionAction(selector=_selector(), text="Dog", timeout_ms=50)
    result = await action.execute(page=page, backend_service=None, web_agent_id="t")

    assert result is False
