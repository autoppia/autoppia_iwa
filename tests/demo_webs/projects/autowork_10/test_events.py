"""Unit tests for autowork_10 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autowork_10.events import (
    BACKEND_EVENT_TYPES,
    NavbarClickEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Minimal payloads - autowork events often use data.get("page") or similar with defaults
AUTOWORK_PAYLOADS = [
    ("BOOK_A_CONSULTATION", {}),
    ("HIRE_BTN_CLICKED", {}),
    ("HIRE_LATER", {}),
    ("HIRE_LATER_ADDED", {}),
    ("HIRE_LATER_REMOVED", {}),
    ("HIRE_LATER_START", {}),
    ("QUICK_HIRE", {}),
    ("NAVBAR_CLICK", {"page": "jobs"}),
    ("NAVBAR_JOBS_CLICK", {}),
    ("NAVBAR_HIRES_CLICK", {}),
    ("NAVBAR_EXPERTS_CLICK", {}),
    ("NAVBAR_FAVORITES_CLICK", {}),
    ("NAVBAR_HIRE_LATER_CLICK", {}),
    ("NAVBAR_PROFILE_CLICK", {}),
    ("FAVORITE_EXPERT_SELECTED", {}),
    ("FAVORITE_EXPERT_REMOVED", {}),
    ("BROWSE_FAVORITE_EXPERT", {}),
    ("CONTACT_EXPERT_OPENED", {}),
    ("CONTACT_EXPERT_MESSAGE_SENT", {}),
    ("EDIT_ABOUT", {}),
    ("EDIT_PROFILE_NAME", {}),
    ("EDIT_PROFILE_TITLE", {}),
    ("EDIT_PROFILE_LOCATION", {}),
    ("EDIT_PROFILE_EMAIL", {}),
    ("SELECT_HIRING_TEAM", {}),
    ("HIRE_CONSULTANT", {}),
    ("CANCEL_HIRE", {"expert": {}}),
    ("POST_A_JOB", {"page": "p", "source": "s"}),
    ("WRITE_JOB_TITLE", {"query": "q"}),
    ("SUBMIT_JOB", {"title": "T", "description": "D", "budgetType": "fixed", "scope": "s", "duration": "d", "step": 1}),
    ("CLOSE_POST_A_JOB_WINDOW", {"title": "T", "description": "D", "budgetType": "fixed", "scope": "s", "duration": "d", "step": 1}),
    ("ADD_SKILL", {"skill": "s"}),
    ("SEARCH_SKILL", {"query": "python"}),
    ("REMOVE_SKILL", {"skill": "s"}),
    ("CHOOSE_BUDGET_TYPE", {}),
    ("CHOOSE_PROJECT_SIZE", {}),
    ("CHOOSE_PROJECT_TIMELINE", {}),
    ("SET_RATE_RANGE", {}),
    ("WRITE_JOB_DESCRIPTION", {}),
]


@pytest.mark.parametrize("event_name,data", AUTOWORK_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


def test_navbar_click_parse():
    e = NavbarClickEvent.parse(_be("NAVBAR_CLICK", {"page": "jobs", "source": "header"}))
    assert e.event_name == "NAVBAR_CLICK"
