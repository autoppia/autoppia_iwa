from autoppia_iwa.src.execution.actions.actions import NavigateAction, RequestUserInputAction
from autoppia_iwa.src.execution.actions.browser_tools import all_tools, get_tool, tool_names


def test_all_tools_uses_browser_namespace_and_excludes_internal_tools() -> None:
    names = {tool["name"] for tool in all_tools()}

    assert "browser.navigate" in names
    assert "user.request_input" in names
    assert "browser.done" not in names
    assert "browser.evaluate" not in names


def test_all_tools_exposes_action_schema_and_description() -> None:
    navigate = next(tool for tool in all_tools() if tool["name"] == "browser.navigate")

    assert navigate["description"]
    assert navigate["parameters"]["type"] == "object"
    assert "url" in navigate["parameters"]["properties"]


def test_get_tool_resolves_namespaced_and_special_user_tool_names() -> None:
    assert get_tool("browser.navigate") is NavigateAction
    assert get_tool("user.request_input") is RequestUserInputAction
    assert get_tool("navigate") is NavigateAction


def test_get_tool_returns_none_for_unknown_name() -> None:
    assert get_tool("browser.not_real") is None


def test_tool_names_matches_all_tools_names() -> None:
    assert set(tool_names()) == {tool["name"] for tool in all_tools()}
