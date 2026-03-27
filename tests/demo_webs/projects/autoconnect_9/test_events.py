"""Unit tests for autoconnect_9 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autoconnect_9.events import (
    BACKEND_EVENT_TYPES,
    ConnectWithUserEvent,
    HomeNavbarEvent,
    PostStatusEvent,
    ViewUserProfileEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTOCONNECT_PARSE_PAYLOADS = [
    ("VIEW_USER_PROFILE", {"username": "u", "name": "N"}),
    ("CONNECT_WITH_USER", {"targetUser": {"username": "u", "name": "N"}}),
    ("HOME_NAVBAR", {}),
    ("JOBS_NAVBAR", {}),
    ("POST_STATUS", {"userName": "u", "content": "c"}),
    ("LIKE_POST", {"userName": "u", "posterName": "p", "posterContent": "c"}),
    ("COMMENT_ON_POST", {"userName": "u", "posterName": "p", "posterContent": "c", "content": "c"}),
    ("SAVE_POST", {"userName": "u", "posterName": "p", "posterContent": "c"}),
    ("HIDE_POST", {"userName": "u", "posterName": "p", "posterContent": "c"}),
    ("APPLY_FOR_JOB", {"jobTitle": "t", "company": "c"}),
    ("SEARCH_USERS", {"query": "q"}),
    ("VIEW_ALL_RECOMMENDATIONS", {}),
    ("FOLLOW_PAGE", {"pageName": "p", "data": {"recommendation": "r"}}),
    ("UNFOLLOW_PAGE", {"pageName": "p", "data": {"recommendation": "r"}}),
    ("SEARCH_JOBS", {"query": "q"}),
    ("FILTER_JOBS", {}),
    ("VIEW_JOB", {"jobTitle": "t", "company": "c"}),
    ("BACK_TO_ALL_JOBS", {}),
    ("VIEW_SAVED_POSTS", {}),
    ("VIEW_APPLIED_JOBS", {}),
    ("CANCEL_APPLICATION", {"jobTitle": "t", "company": "c"}),
    ("EDIT_PROFILE", {"username": "u", "name": "n"}),
    ("EDIT_EXPERIENCE", {}),
    ("REMOVE_POST", {"userName": "u", "posterName": "p", "posterContent": "c"}),
    ("VIEW_HIDDEN_POSTS", {}),
    ("UNHIDE_POST", {"userName": "u", "posterName": "p", "posterContent": "c"}),
    ("ADD_EXPERIENCE", {"experience": {"company": "C", "description": "d", "duration": "1y", "location": "L", "title": "T"}}),
]


class TestParseAutoconnectEvents:
    def test_view_user_profile_parse(self):
        e = ViewUserProfileEvent.parse(_be("VIEW_USER_PROFILE", {"username": "alice", "name": "Alice"}))
        assert e.username == "alice"
        assert e.name == "Alice"

    def test_connect_with_user_parse(self):
        e = ConnectWithUserEvent.parse(_be("CONNECT_WITH_USER", {"targetUser": {"username": "bob", "name": "Bob"}}))
        assert e.target_username == "bob"
        assert e.target_name == "Bob"

    def test_home_navbar_parse(self):
        e = HomeNavbarEvent.parse(_be("HOME_NAVBAR", {}))
        assert e.event_name == "HOME_NAVBAR"

    def test_post_status_parse(self):
        e = PostStatusEvent.parse(_be("POST_STATUS", {"userName": "u", "content": "Hello"}))
        assert e.content == "Hello"


class TestValidateAutoconnectEvents:
    def test_view_user_profile_validate_none(self):
        e = ViewUserProfileEvent.parse(_be("VIEW_USER_PROFILE", {"username": "u", "name": "N"}))
        assert e.validate_criteria(None) is True

    def test_connect_with_user_validate(self):
        e = ConnectWithUserEvent.parse(_be("CONNECT_WITH_USER", {"targetUser": {"username": "bob", "name": "Bob"}}))
        criteria = ConnectWithUserEvent.ValidationCriteria(target_username="bob", target_name="Bob")
        assert e.validate_criteria(criteria) is True

    def test_home_navbar_validate_none(self):
        e = HomeNavbarEvent.parse(_be("HOME_NAVBAR", {}))
        assert e.validate_criteria(None) is True


@pytest.mark.parametrize("event_name,data", AUTOCONNECT_PARSE_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)


@pytest.mark.parametrize("event_name,data", AUTOCONNECT_PARSE_PAYLOADS)
def test_backend_event_types_validate_none_criteria(event_name, data):
    """Most event validators short-circuit to True when criteria is None."""
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.validate_criteria(None) is True


def test_connect_with_user_parse_missing_target_user_defaults():
    e = ConnectWithUserEvent.parse(_be("CONNECT_WITH_USER", {}))
    assert e.target_username == ""
    assert e.target_name == ""
