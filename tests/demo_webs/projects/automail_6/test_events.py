"""Unit tests for automail_6 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.automail_6.events import (
    BACKEND_EVENT_TYPES,
    SearchEmailEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTOMAIL_PAYLOADS = [
    ("VIEW_EMAIL", {}),
    ("STAR_AN_EMAIL", {}),
    ("MARK_EMAIL_AS_IMPORTANT", {}),
    ("MARK_AS_UNREAD", {}),
    ("DELETE_EMAIL", {}),
    ("MARK_AS_SPAM", {}),
    ("ADD_LABEL", {}),
    ("CREATE_LABEL", {}),
    ("SEND_EMAIL", {}),
    ("EMAIL_SAVE_AS_DRAFT", {}),
    ("EDIT_DRAFT_EMAIL", {}),
    ("ARCHIVE_EMAIL", {}),
    ("REPLY_EMAIL", {}),
    ("FORWARD_EMAIL", {}),
    ("THEME_CHANGED", {}),
    ("SEARCH_EMAIL", {"query": "q"}),
    ("CLEAR_SELECTION", {}),
    ("EMAILS_NEXT_PAGE", {}),
    ("EMAILS_PREV_PAGE", {}),
    ("VIEW_TEMPLATES", {}),
    ("TEMPLATE_SELECTED", {}),
    ("TEMPLATE_BODY_EDITED", {}),
    ("TEMPLATE_SENT", {}),
    ("TEMPLATE_SAVED_DRAFT", {}),
    ("TEMPLATE_CANCELED", {}),
]


@pytest.mark.parametrize("event_name,data", AUTOMAIL_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


def test_search_email_parse():
    e = SearchEmailEvent.parse(_be("SEARCH_EMAIL", {"query": "test"}))
    assert e.query == "test"
