"""Tests for execution.classes."""

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.execution.actions.actions import NavigateAction
from autoppia_iwa.src.execution.classes import ActionExecutionResult, BrowserSnapshot


def test_browser_snapshot_model_dump():
    action = NavigateAction(url="http://example.com")
    snapshot = BrowserSnapshot(
        iteration=1,
        action=action,
        prev_html="<p>before</p>",
        current_html="<p>after</p>",
        screenshot_before="",
        screenshot_after="",
        backend_events=[BackendEvent(event_name="test", data={"k": "v"})],
        current_url="http://example.com",
    )
    out = snapshot.model_dump()
    assert "html" in out
    assert out["html"] == "<p>after</p>"
    assert out["prev_html"] == "<p>before</p>"
    assert "timestamp" in out
    assert "backend_events" in out
    assert len(out["backend_events"]) == 1
    assert "action" not in out
    assert "screenshot_before" not in out


def test_action_execution_result_model_dump():
    action = NavigateAction(url="http://example.com")
    snapshot = BrowserSnapshot(
        iteration=0,
        action=action,
        prev_html="",
        current_html="",
        screenshot_before="",
        screenshot_after="",
        backend_events=[],
        current_url="",
    )
    result = ActionExecutionResult(
        action=action,
        action_event="NavigateAction",
        successfully_executed=True,
        execution_time=1.5,
        browser_snapshot=snapshot,
    )
    out = result.model_dump()
    assert out["action_event"] == "NavigateAction"
    assert out["successfully_executed"] is True
    assert "browser_snapshot" in out
    assert "action" in out
    assert "url" in out["action"]
