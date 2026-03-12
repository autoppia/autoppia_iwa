"""Create every action type via BaseAction.create_action (coverage for ActionRegistry and all actions)."""

from autoppia_iwa.src.execution.actions.actions import (
    AssertAction,
    ClickAction,
    DoubleClickAction,
    DragAndDropAction,
    GetDropDownOptionsAction,
    HoldKeyAction,
    HoverAction,
    IdleAction,
    LeftClickDragAction,
    MiddleClickAction,
    MouseDownAction,
    MouseMoveAction,
    MouseUpAction,
    NavigateAction,
    RightClickAction,
    ScreenshotAction,
    ScrollAction,
    SelectAction,
    SelectDropDownOptionAction,
    SendKeysIWAAction,
    SubmitAction,
    TripleClickAction,
    TypeAction,
    UndefinedAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction

SEL = {"type": "attributeValueSelector", "attribute": "id", "value": "x"}


class TestCreateActionAllTypes:
    def test_create_navigate_url(self):
        a = BaseAction.create_action({"type": "NavigateAction", "url": "http://u"})
        assert isinstance(a, NavigateAction)

    def test_create_navigate_go_back(self):
        a = BaseAction.create_action({"type": "NavigateAction", "go_back": True})
        assert isinstance(a, NavigateAction)
        assert a.go_back is True

    def test_create_click_selector(self):
        a = BaseAction.create_action({"type": "ClickAction", "selector": SEL})
        assert isinstance(a, ClickAction)

    def test_create_click_coords(self):
        a = BaseAction.create_action({"type": "ClickAction", "x": 10, "y": 20})
        assert isinstance(a, ClickAction)

    def test_create_double_click(self):
        a = BaseAction.create_action({"type": "DoubleClickAction", "selector": SEL})
        assert isinstance(a, DoubleClickAction)

    def test_create_right_click(self):
        a = BaseAction.create_action({"type": "RightClickAction", "x": 0, "y": 0})
        assert isinstance(a, RightClickAction)

    def test_create_middle_click(self):
        a = BaseAction.create_action({"type": "MiddleClickAction", "selector": SEL})
        assert isinstance(a, MiddleClickAction)

    def test_create_triple_click(self):
        a = BaseAction.create_action({"type": "TripleClickAction", "selector": SEL})
        assert isinstance(a, TripleClickAction)

    def test_create_mouse_down(self):
        a = BaseAction.create_action({"type": "MouseDownAction", "selector": SEL})
        assert isinstance(a, MouseDownAction)

    def test_create_mouse_up(self):
        a = BaseAction.create_action({"type": "MouseUpAction", "x": 1, "y": 1})
        assert isinstance(a, MouseUpAction)

    def test_create_mouse_move(self):
        a = BaseAction.create_action({"type": "MouseMoveAction", "selector": SEL, "steps": 2})
        assert isinstance(a, MouseMoveAction)

    def test_create_type(self):
        a = BaseAction.create_action({"type": "TypeAction", "text": "hi", "selector": SEL})
        assert isinstance(a, TypeAction)

    def test_create_select(self):
        a = BaseAction.create_action({"type": "SelectAction", "selector": SEL, "value": "a"})
        assert isinstance(a, SelectAction)

    def test_create_hover(self):
        a = BaseAction.create_action({"type": "HoverAction", "selector": SEL})
        assert isinstance(a, HoverAction)

    def test_create_wait_selector(self):
        a = BaseAction.create_action({"type": "WaitAction", "selector": SEL})
        assert isinstance(a, WaitAction)

    def test_create_wait_time(self):
        a = BaseAction.create_action({"type": "WaitAction", "time_seconds": 1.0})
        assert isinstance(a, WaitAction)

    def test_create_scroll(self):
        a = BaseAction.create_action({"type": "ScrollAction", "down": True})
        assert isinstance(a, ScrollAction)

    def test_create_submit(self):
        a = BaseAction.create_action({"type": "SubmitAction", "selector": SEL})
        assert isinstance(a, SubmitAction)

    def test_create_assert(self):
        a = BaseAction.create_action({"type": "AssertAction", "text_to_assert": "x"})
        assert isinstance(a, AssertAction)

    def test_create_drag_and_drop(self):
        a = BaseAction.create_action({"type": "DragAndDropAction", "sourceSelector": "#a", "targetSelector": "#b"})
        assert isinstance(a, DragAndDropAction)

    def test_create_left_click_drag(self):
        a = BaseAction.create_action(
            {
                "type": "LeftClickDragAction",
                "selector": SEL,
                "targetSelector": {"type": "attributeValueSelector", "attribute": "id", "value": "y"},
                "steps": 2,
            }
        )
        assert isinstance(a, LeftClickDragAction)

    def test_create_screenshot(self):
        a = BaseAction.create_action({"type": "ScreenshotAction", "file_path": "/tmp/s.png"})
        assert isinstance(a, ScreenshotAction)

    def test_create_send_keys(self):
        a = BaseAction.create_action({"type": "SendKeysIWAAction", "keys": "Enter"})
        assert isinstance(a, SendKeysIWAAction)

    def test_create_hold_key(self):
        a = BaseAction.create_action({"type": "HoldKeyAction", "key": "Shift"})
        assert isinstance(a, HoldKeyAction)

    def test_create_get_drop_down_options(self):
        a = BaseAction.create_action({"type": "GetDropDownOptionsAction", "selector": SEL})
        assert isinstance(a, GetDropDownOptionsAction)

    def test_create_select_drop_down_option(self):
        a = BaseAction.create_action({"type": "SelectDropDownOptionAction", "selector": SEL, "text": "Opt"})
        assert isinstance(a, SelectDropDownOptionAction)

    def test_create_idle(self):
        a = BaseAction.create_action({"type": "IdleAction"})
        assert isinstance(a, IdleAction)

    def test_create_undefined(self):
        a = BaseAction.create_action({"type": "UndefinedAction"})
        assert isinstance(a, UndefinedAction)
