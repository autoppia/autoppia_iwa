"""Unit tests to improve actions.py coverage: validators, helpers, and edge paths."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from playwright.async_api import TimeoutError as PWTimeout

from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    DoubleClickAction,
    HoldKeyAction,
    LeftClickDragAction,
    MiddleClickAction,
    MouseDownAction,
    MouseMoveAction,
    MouseUpAction,
    NavigateAction,
    RightClickAction,
    ScrollAction,
    TripleClickAction,
    TypeAction,
    WaitAction,
    _element_center,
    _ensure_page,
    _maybe_wait_navigation,
    _move_mouse_to,
)
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType

# ---------------------------------------------------------------------------
# Validators (hit warning and error branches)
# ---------------------------------------------------------------------------


class TestBaseClickActionValidator:
    def test_click_action_neither_selector_nor_coords_raises(self):
        with pytest.raises(ValueError, match="Either 'selector' or both 'x' and 'y'"):
            ClickAction(selector=None, x=None, y=None)

    def test_click_action_both_selector_and_coords_warning(self):
        """Both selector and coords provided: validator logs warning and prioritizes selector."""
        sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
        action = ClickAction(selector=sel, x=10, y=20)
        assert action.selector is not None
        assert action.x == 10
        assert action.y == 20


class TestNavigateActionValidator:
    def test_navigate_no_target_raises(self):
        with pytest.raises(ValueError, match="exactly one of"):
            NavigateAction(url=None, go_back=False, go_forward=False)

    def test_navigate_two_targets_raises(self):
        with pytest.raises(ValueError, match="exactly one of"):
            NavigateAction(url="http://x.com", go_back=True, go_forward=False)


class TestTypeActionValidator:
    def test_type_action_both_text_and_value_different_warning(self):
        sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x")
        # When both "text" and "value" provided and different, validator pops value and logs warning
        action = TypeAction(text="a", value="b", selector=sel)
        assert action.text == "a"
        assert not hasattr(action, "value") or getattr(action, "value", None) != "b"


class TestWaitActionValidator:
    def test_wait_action_neither_selector_nor_time_raises(self):
        with pytest.raises(ValueError, match="either 'selector' or 'time_seconds'"):
            WaitAction(selector=None, time_seconds=None)

    def test_wait_action_both_selector_and_time_warning(self):
        sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x")
        action = WaitAction(selector=sel, time_seconds=1.0)
        assert action.selector is not None
        assert action.time_seconds == 1.0


class TestHoldKeyActionValidator:
    def test_hold_key_invalid_duration_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            HoldKeyAction(key="a", duration_ms=-1)

    def test_hold_key_release_and_duration_raises(self):
        with pytest.raises(Exception, match="either.*release.*duration_ms"):
            HoldKeyAction(key="a", release=True, duration_ms=100)

    def test_hold_key_missing_key_raises(self):
        with pytest.raises(ValueError):
            HoldKeyAction(key="")


class TestScrollActionValidator:
    def test_scroll_action_no_direction_raises(self):
        with pytest.raises(ValueError, match="exactly one of up/down/left/right"):
            ScrollAction(up=False, down=False, left=False, right=False)


# ---------------------------------------------------------------------------
# Helper: _ensure_page
# ---------------------------------------------------------------------------


def test_ensure_page_none_raises():
    with pytest.raises(ValueError, match="requires a valid Page"):
        _ensure_page(None, "TestAction")


def test_ensure_page_returns_page():
    page = MagicMock()
    assert _ensure_page(page, "TestAction") is page


# ---------------------------------------------------------------------------
# Helper: _move_mouse_to (line 72 - ValueError when no selector and no x,y)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_move_mouse_to_no_selector_no_coords_raises():
    page = MagicMock()
    with pytest.raises(ValueError, match="selector or.*x.*y"):
        await _move_mouse_to(page, None, None, None)


# ---------------------------------------------------------------------------
# Helper: _element_center (line 57 - bounding_box None)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_element_center_bounding_box_none_raises():
    page = MagicMock()
    loc = AsyncMock()
    loc.scroll_into_view_if_needed = AsyncMock()
    loc.bounding_box = AsyncMock(return_value=None)
    page.locator = MagicMock(return_value=loc)
    with pytest.raises(ValueError, match="Could not resolve bounding box"):
        await _element_center(page, "#foo")


# ---------------------------------------------------------------------------
# Helper: _maybe_wait_navigation (lines 47-48 - PWTimeout path)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_maybe_wait_navigation_timeout_does_not_raise():
    page = AsyncMock()
    page.wait_for_event = AsyncMock(side_effect=PWTimeout("timeout"))
    await _maybe_wait_navigation(page, timeout_ms=1)
    page.wait_for_event.assert_called_once()
    page.wait_for_load_state.assert_not_called()


@pytest.mark.asyncio
async def test_maybe_wait_navigation_success_calls_load_state():
    """When wait_for_event succeeds, wait_for_load_state is called (lines 45-46)."""
    page = AsyncMock()
    page.wait_for_event = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    await _maybe_wait_navigation(page, timeout_ms=1000)
    page.wait_for_event.assert_called_once()
    page.wait_for_load_state.assert_called_once_with("domcontentloaded")


# ---------------------------------------------------------------------------
# ClickAction with selector triggers _maybe_wait_navigation (integration with mock)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_click_action_selector_triggers_maybe_wait_navigation():
    page = AsyncMock()
    page.click = AsyncMock()
    page.wait_for_event = AsyncMock(side_effect=PWTimeout("timeout"))
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = ClickAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.click.assert_called_once()
    page.wait_for_event.assert_called_once()


# ---------------------------------------------------------------------------
# MouseMoveAction with neither selector nor coords: validator prevents it, so we test via execute
# that _move_mouse_to ValueError can be reached from MouseDownAction with invalid state.
# Actually MouseDownAction always has either selector or x,y by validator. So the only way
# to hit _move_mouse_to(..., None, None, None) is the direct test above. Done.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# WaitAction execute: else branch (line 382-383) - invalid state
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_wait_action_execute_invalid_state_raises():
    page = MagicMock()
    action = WaitAction(selector=None, time_seconds=1.0)
    # Corrupt state for test: make selector and time_seconds both falsy after construction
    action.selector = None
    action.time_seconds = None
    with pytest.raises(ValueError, match="Invalid state"):
        await action.execute(page, backend_service=None, web_agent_id="t")


# ---------------------------------------------------------------------------
# NavigateAction execute: else branch (line 294-295)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_navigate_action_execute_invalid_state_raises():
    page = MagicMock()
    page.go_back = AsyncMock()
    page.go_forward = AsyncMock()
    page.goto = AsyncMock()
    action = NavigateAction(url="http://x.com", go_back=False, go_forward=False)
    action.url = None
    action.go_back = False
    action.go_forward = False
    with pytest.raises(ValueError, match="Invalid state"):
        await action.execute(page, backend_service=None, web_agent_id="t")


# ---------------------------------------------------------------------------
# LeftClickDragAction: missing targetX/targetY when using coordinate target (line 458-459)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_left_click_drag_missing_target_coords_raises():
    """When targetSelector is None but only one of targetX/targetY is set, execute raises."""
    page = AsyncMock()
    page.mouse = AsyncMock()
    page.mouse.move = AsyncMock()
    page.mouse.down = AsyncMock()
    page.mouse.up = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    loc = AsyncMock()
    loc.bounding_box = AsyncMock(return_value={"x": 0, "y": 0, "width": 10, "height": 10})
    page.locator = MagicMock(return_value=loc)
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="src")
    action = LeftClickDragAction(
        selector=sel,
        targetSelector=None,
        targetX=100,
        targetY=100,
        steps=1,
    )
    action.targetSelector = None
    action.targetX = 100
    action.targetY = None
    with pytest.raises(ValueError, match="targetX.*targetY"):
        await action.execute(page, backend_service=None, web_agent_id="t")


# ---------------------------------------------------------------------------
# ScrollAction: exception path and keyboard fallback (lines 511-524)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_scroll_action_js_failure_keyboard_fallback():
    """When _scroll_by_value fails, ScrollAction falls back to keyboard press."""
    from playwright.async_api import Error as PlaywrightError

    page = AsyncMock()
    page.evaluate = AsyncMock(side_effect=PlaywrightError("evaluate failed"))
    page.keyboard = AsyncMock()
    page.keyboard.press = AsyncMock()
    action = ScrollAction(down=True)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.keyboard.press.assert_called_once_with("PageDown")


@pytest.mark.asyncio
async def test_scroll_action_keyboard_fallback_also_fails_raises():
    """When both JS scroll and keyboard fallback fail, ScrollAction raises."""
    from playwright.async_api import Error as PlaywrightError

    page = AsyncMock()
    page.evaluate = AsyncMock(side_effect=PlaywrightError("evaluate failed"))
    page.keyboard = AsyncMock()
    page.keyboard.press = AsyncMock(side_effect=PWTimeout("keyboard timeout"))
    action = ScrollAction(down=True)
    with pytest.raises(ValueError, match="ScrollAction completely failed"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_scroll_action_keyboard_fallback_left():
    """ScrollAction left=True with JS failure uses ArrowLeft fallback."""
    from playwright.async_api import Error as PlaywrightError

    page = AsyncMock()
    page.evaluate = AsyncMock(side_effect=PlaywrightError("evaluate failed"))
    page.keyboard = AsyncMock()
    page.keyboard.press = AsyncMock()
    action = ScrollAction(left=True)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.keyboard.press.assert_called_once_with("ArrowLeft")


@pytest.mark.asyncio
async def test_scroll_action_keyboard_fallback_right():
    """ScrollAction right=True with JS failure uses ArrowRight fallback."""
    from playwright.async_api import Error as PlaywrightError

    page = AsyncMock()
    page.evaluate = AsyncMock(side_effect=PlaywrightError("evaluate failed"))
    page.keyboard = AsyncMock()
    page.keyboard.press = AsyncMock()
    action = ScrollAction(right=True)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.keyboard.press.assert_called_once_with("ArrowRight")


@pytest.mark.asyncio
async def test_scroll_action_keyboard_fallback_up():
    """ScrollAction up=True with JS failure uses PageUp fallback."""
    from playwright.async_api import Error as PlaywrightError

    page = AsyncMock()
    page.evaluate = AsyncMock(side_effect=PlaywrightError("evaluate failed"))
    page.keyboard = AsyncMock()
    page.keyboard.press = AsyncMock()
    action = ScrollAction(up=True)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.keyboard.press.assert_called_once_with("PageUp")


# ---------------------------------------------------------------------------
# Execute paths: coordinate-based and selector-based (cover 119-263)
# ---------------------------------------------------------------------------


def _mock_page_for_click_actions():
    page = AsyncMock()
    page.click = AsyncMock()
    page.dblclick = AsyncMock()
    page.mouse = AsyncMock()
    page.mouse.click = AsyncMock()
    page.mouse.dblclick = AsyncMock()
    page.mouse.move = AsyncMock()
    page.mouse.down = AsyncMock()
    page.mouse.up = AsyncMock()
    page.wait_for_event = AsyncMock(side_effect=PWTimeout("no nav"))
    page.locator = MagicMock(
        return_value=AsyncMock(
            scroll_into_view_if_needed=AsyncMock(),
            bounding_box=AsyncMock(return_value={"x": 10, "y": 20, "width": 100, "height": 50}),
        )
    )
    return page


@pytest.mark.asyncio
async def test_click_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = ClickAction(x=5, y=10)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.click.assert_called_once_with(5, 10)


@pytest.mark.asyncio
async def test_double_click_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = DoubleClickAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.dblclick.assert_called_once()


@pytest.mark.asyncio
async def test_double_click_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = DoubleClickAction(x=1, y=2)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.dblclick.assert_called_once_with(x=1, y=2)


@pytest.mark.asyncio
async def test_right_click_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = RightClickAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.click.assert_called_once()
    assert page.click.call_args[1].get("button") == "right"


@pytest.mark.asyncio
async def test_right_click_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = RightClickAction(x=0, y=0)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.click.assert_called_once_with(0, 0, button="right")


@pytest.mark.asyncio
async def test_middle_click_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = MiddleClickAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    assert page.click.call_args[1].get("button") == "middle"


@pytest.mark.asyncio
async def test_middle_click_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = MiddleClickAction(x=3, y=4)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.click.assert_called_once_with(3, 4, button="middle")


@pytest.mark.asyncio
async def test_triple_click_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = TripleClickAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    assert page.click.call_args[1].get("click_count") == 3


@pytest.mark.asyncio
async def test_triple_click_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = TripleClickAction(x=0, y=0)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.click.assert_called_once_with(0, 0, click_count=3)


@pytest.mark.asyncio
async def test_mouse_down_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = MouseDownAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.down.assert_called_once_with(button="left")


@pytest.mark.asyncio
async def test_mouse_down_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = MouseDownAction(x=10, y=20)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.move.assert_called()
    page.mouse.down.assert_called_once_with(button="left")


@pytest.mark.asyncio
async def test_mouse_up_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
    action = MouseUpAction(selector=sel)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.up.assert_called_once_with(button="left")


@pytest.mark.asyncio
async def test_mouse_up_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = MouseUpAction(x=1, y=1)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.up.assert_called_once_with(button="left")


@pytest.mark.asyncio
async def test_mouse_move_action_selector_path():
    page = _mock_page_for_click_actions()
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="area")
    action = MouseMoveAction(selector=sel, steps=3)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.move.assert_called_once()
    assert page.mouse.move.call_args[1].get("steps") == 3


@pytest.mark.asyncio
async def test_mouse_move_action_coordinate_path():
    page = _mock_page_for_click_actions()
    action = MouseMoveAction(x=50, y=50, steps=2)
    await action.execute(page, backend_service=None, web_agent_id="t")
    page.mouse.move.assert_called_once_with(50, 50, steps=2)


@pytest.mark.asyncio
async def test_mouse_move_action_no_selector_no_coords_raises():
    """MouseMoveAction requires selector or (x,y); validator raises at construction."""
    with pytest.raises(Exception, match="Either"):
        MouseMoveAction(selector=None, x=None, y=None)


@pytest.mark.asyncio
async def test_click_action_execute_neither_selector_nor_coords_raises():
    """Execute raises when both selector and coords are missing (corrupt state)."""
    page = MagicMock()
    action = ClickAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_double_click_action_execute_neither_selector_nor_coords_raises():
    page = MagicMock()
    action = DoubleClickAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_right_click_action_execute_neither_selector_nor_coords_raises():
    page = MagicMock()
    action = RightClickAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_middle_click_action_execute_neither_selector_nor_coords_raises():
    page = MagicMock()
    action = MiddleClickAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_triple_click_action_execute_neither_selector_nor_coords_raises():
    page = MagicMock()
    action = TripleClickAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


@pytest.mark.asyncio
async def test_mouse_move_action_execute_neither_selector_nor_coords_raises():
    page = _mock_page_for_click_actions()
    action = MouseMoveAction(x=0, y=0)
    action.selector = None
    action.x = None
    action.y = None
    with pytest.raises(ValueError, match="selector or"):
        await action.execute(page, backend_service=None, web_agent_id="t")


class TestTypeActionValidatorExecute:
    def test_type_action_missing_text_raises(self):
        with pytest.raises(Exception, match="text"):
            TypeAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x"))
