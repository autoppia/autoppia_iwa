"""Unit tests for execution.actions.base (Selector, ActionRegistry, BaseAction.create_action)."""

import pytest

from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import (
    ActionRegistry,
    BaseAction,
    Selector,
    SelectorType,
)


class TestSelectorToPlaywrightSelector:
    def test_id_attribute(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="btn")
        assert s.to_playwright_selector() == "#btn"

    def test_id_strips_hash(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="#btn")
        assert s.to_playwright_selector() == "#btn"

    def test_class_single(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="class", value="btn")
        assert s.to_playwright_selector() == ".btn"

    def test_class_multiple(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="class", value="btn primary")
        assert ".btn" in s.to_playwright_selector() and ".primary" in s.to_playwright_selector()

    def test_data_testid(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="data-testid", value="submit")
        assert s.to_playwright_selector() == "[data-testid='submit']"

    def test_xpath_with_slash(self):
        s = Selector(type=SelectorType.XPATH_SELECTOR, value="//button[@id='ok']")
        assert s.to_playwright_selector().startswith("xpath=")
        assert "button" in s.to_playwright_selector()

    def test_xpath_without_leading_slash(self):
        s = Selector(type=SelectorType.XPATH_SELECTOR, value="button")
        result = s.to_playwright_selector()
        assert result == "xpath=//button" or "//button" in result

    def test_tag_contains_selector(self):
        s = Selector(type=SelectorType.TAG_CONTAINS_SELECTOR, value="Submit")
        result = s.to_playwright_selector()
        assert "text=" in result
        assert "Submit" in result

    def test_attribute_value_selector_missing_attribute_raises(self):
        s = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute=None, value="x")
        with pytest.raises(ValueError):
            s.to_playwright_selector()


class TestActionRegistry:
    def test_get_click_action(self):
        cls = ActionRegistry.get("ClickAction")
        assert cls is ClickAction

    def test_get_lowercase_without_action_suffix(self):
        cls = ActionRegistry.get("click")
        assert cls is ClickAction

    def test_get_navigate_action(self):
        cls = ActionRegistry.get("NavigateAction")
        assert cls is NavigateAction

    def test_unsupported_raises(self):
        with pytest.raises(ValueError) as exc_info:
            ActionRegistry.get("NonExistentAction")
        assert "Unsupported" in str(exc_info.value)


class TestBaseActionCreateAction:
    def test_create_navigate_action(self):
        data = {"type": "NavigateAction", "url": "http://example.com"}
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, NavigateAction)
        assert action.url == "http://example.com"

    def test_create_click_action(self):
        data = {
            "type": "ClickAction",
            "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "btn"},
        }
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, ClickAction)

    def test_missing_type_raises(self):
        with pytest.raises(ValueError):
            BaseAction.create_action({"url": "http://x.com"})

    def test_not_dict_raises(self):
        with pytest.raises(ValueError):
            BaseAction.create_action("not a dict")

    def test_type_normalized_without_action_suffix(self):
        # Some payloads send type without "Action"
        data = {"type": "navigate", "url": "http://example.com"}
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, NavigateAction)


class TestTypeActionAndWaitAction:
    """Tests for TypeAction and WaitAction creation."""

    def test_create_type_action_with_text(self):
        data = {
            "type": "TypeAction",
            "text": "hello",
            "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "input"},
        }
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, TypeAction)
        assert action.text == "hello"

    def test_create_type_action_value_alias_maps_to_text(self):
        data = {"type": "TypeAction", "value": "mapped", "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "x"}}
        action = BaseAction.create_action(data)
        assert action is not None
        assert action.text == "mapped"

    def test_create_wait_action_with_selector(self):
        data = {"type": "WaitAction", "selector": {"type": "attributeValueSelector", "attribute": "id", "value": "loading"}}
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, WaitAction)
        assert action.selector is not None

    def test_create_wait_action_with_time_seconds(self):
        data = {"type": "WaitAction", "time_seconds": 2.0}
        action = BaseAction.create_action(data)
        assert action is not None
        assert isinstance(action, WaitAction)
        assert action.time_seconds == 2.0


@pytest.mark.asyncio
async def test_execute_with_page_none_raises():
    """Actions that require a page raise ValueError when page is None (_ensure_page)."""
    action = NavigateAction(url="http://example.com")
    with pytest.raises(ValueError, match="requires a valid Page"):
        await action.execute(page=None, backend_service=None, web_agent_id="t")
