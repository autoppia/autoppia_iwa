"""
Browser tools mapping: browser.navigate → NavigateAction, etc.

Usage:
    from autoppia_iwa.src.execution.actions.browser_tools import all_tools, get_tool

    tools = all_tools()  # Returns list of tool definitions for model tool-use
    action_cls = get_tool("browser.navigate")  # Returns NavigateAction class
"""

from autoppia_iwa.src.execution.actions.base import ActionRegistry, BaseAction


def all_tools() -> list[dict]:
    """
    Returns all browser actions as tool definitions in the format:
    [{"name": "browser.navigate", "description": "...", "parameters": {...}}, ...]
    """
    tools = []
    for action_cls in ActionRegistry.values():
        tool_name = action_cls.tool_name()
        if tool_name in {"done", "evaluate"}:
            continue
        namespaced = "user.request_input" if tool_name == "request_user_input" else f"browser.{tool_name}"
        tools.append({
            "name": namespaced,
            "description": action_cls.tool_description(),
            "parameters": action_cls.tool_parameters_schema(),
        })
    return tools


def get_tool(name: str) -> type[BaseAction] | None:
    """
    Resolve a namespaced tool name (e.g. 'browser.navigate') to its action class.
    Returns None if not found.
    """
    if name.startswith("browser."):
        action_name = name.split(".", 1)[1]
    elif name == "user.request_input":
        action_name = "request_user_input"
    else:
        action_name = name

    try:
        return ActionRegistry.get(action_name)
    except ValueError:
        return None


def tool_names() -> list[str]:
    """Returns all available tool names in browser.* namespace."""
    names = []
    for action_cls in ActionRegistry.values():
        tool_name = action_cls.tool_name()
        if tool_name in {"done", "evaluate"}:
            continue
        namespaced = "user.request_input" if tool_name == "request_user_input" else f"browser.{tool_name}"
        names.append(namespaced)
    return names
