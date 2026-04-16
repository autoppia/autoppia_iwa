"""Tests for web_agents.classes."""

from autoppia_iwa.src.execution.actions.actions import TypeAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType
from autoppia_iwa.src.web_agents.classes import (
    BaseAgent,
    TaskSolution,
    replace_credential_placeholders_in_string,
    replace_credentials_in_action,
    sanitize_snapshot_html,
)


def test_replace_credential_placeholders_in_string():
    out = replace_credential_placeholders_in_string("<username> <password> <web_agent_id>", "agent-1")
    assert "useragent-1" in out
    assert "Passw0rd!" in out
    assert "agent-1" in out
    out2 = replace_credential_placeholders_in_string("<signup_username> <signup_email> <signup_password>", "x")
    assert "newuserx" in out2
    assert "newuserx@gmail.com" in out2


def test_replace_credentials_in_action():
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="input")
    action = TypeAction(type="TypeAction", text="<username>", selector=sel)
    replace_credentials_in_action(action, "agent-1")
    assert action.text == "useragent-1"


def test_replace_credentials_in_action_selector_value():
    sel = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="<web_agent_id>")
    action = TypeAction(type="TypeAction", text="hello", selector=sel)
    replace_credentials_in_action(action, "my-id")
    assert action.selector.value == "my-id"


def test_sanitize_snapshot_html_empty():
    assert sanitize_snapshot_html("", "x") == ""
    assert sanitize_snapshot_html(None, "x") is None


def test_sanitize_snapshot_html():
    html = "userfoo and Passw0rd! and newuserfoo newuserfoo@gmail.com"
    out = sanitize_snapshot_html(html, "foo")
    assert "<username>" in out
    assert "<password>" in out
    assert "<signup_username>" in out
    assert "<signup_email>" in out
    assert "userfoo" not in out
    assert "Passw0rd!" not in out


def test_base_agent_generate_random_web_agent_id():
    class ConcreteAgent(BaseAgent):
        async def step(self, *, task, html, screenshot=None, url="", step_index=0, history=None):
            return []

    agent = ConcreteAgent()
    uid = agent.generate_random_web_agent_id(length=10)
    assert len(uid) == 10
    assert uid.isalnum()


def test_base_agent_init_with_id_and_name():
    class ConcreteAgent(BaseAgent):
        async def step(self, *, task, html, screenshot=None, url="", step_index=0, history=None):
            return []

    agent = ConcreteAgent(id="custom-id", name="Custom")
    assert agent.id == "custom-id"
    assert agent.name == "Custom"


def test_task_solution_total_tokens():
    sol = TaskSolution(web_agent_id="a", input_tokens=100, output_tokens=50)
    assert sol.total_tokens == 150


def test_task_solution_replace_web_agent_id():
    action = TypeAction(
        type="TypeAction",
        text="<web_agent_id>",
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x"),
    )
    sol = TaskSolution(web_agent_id="agent-99", actions=[action])
    sol.replace_web_agent_id()
    assert sol.actions[0].text == "agent-99"


def test_task_solution_replace_web_agent_id_noop_without_agent_id():
    action = TypeAction(
        type="TypeAction",
        text="<web_agent_id>",
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x"),
    )
    sol = TaskSolution(web_agent_id=None, actions=[action])
    out = sol.replace_web_agent_id()
    assert out is sol.actions
    assert sol.actions[0].text == "<web_agent_id>"


def test_task_solution_replace_credentials():
    action = TypeAction(
        type="TypeAction",
        text="<username>",
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="x"),
    )
    sol = TaskSolution(web_agent_id="x", actions=[action])
    sol.replace_credentials("agent-1")
    assert sol.actions[0].text == "useragent-1"


def test_task_solution_nested_model_dump():
    action = TypeAction(
        type="TypeAction",
        text="hi",
        selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="y"),
    )
    sol = TaskSolution(actions=[action])
    out = sol.nested_model_dump()
    assert "actions" in out
    assert len(out["actions"]) == 1
    assert out["actions"][0]["text"] == "hi"
