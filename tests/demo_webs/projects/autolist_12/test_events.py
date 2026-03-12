"""Unit tests for autolist_12 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autolist_12.events import (
    BACKEND_EVENT_TYPES,
    SelectTaskPriorityEvent,
    TaskAddedEvent,
    TeamMembersAddedEvent,
    TeamRoleAssignedEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


AUTOLIST_PAYLOADS = [
    ("AUTOLIST_ADD_TASK_CLICKED", {}),
    ("AUTOLIST_SELECT_DATE_FOR_TASK", {}),
    ("AUTOLIST_SELECT_TASK_PRIORITY", {"label": "High"}),
    ("AUTOLIST_TASK_ADDED", {"name": "T", "description": "D", "priority": "P"}),
    ("AUTOLIST_CANCEL_TASK_CREATION", {"currentName": "", "currentDescription": "", "priority": ""}),
    ("AUTOLIST_EDIT_TASK_MODAL_OPENED", {"name": "T", "description": "D", "priority": "P"}),
    ("AUTOLIST_COMPLETE_TASK", {"name": "T", "description": "D", "priority": "P"}),
    ("AUTOLIST_DELETE_TASK", {"name": "T", "description": "D", "priority": "P"}),
    ("AUTOLIST_ADD_TEAM_CLICKED", {}),
    ("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 0, "members": []}),
    ("AUTOLIST_TEAM_ROLE_ASSIGNED", {"memberId": "m1", "role": "lead"}),
    ("AUTOLIST_TEAM_CREATED", {"teamName": "Team A", "members": []}),
]


class TestParseAutolistEvents:
    def test_select_priority_parse(self):
        e = SelectTaskPriorityEvent.parse(_be("AUTOLIST_SELECT_TASK_PRIORITY", {"label": "High"}))
        assert e.event_name == "AUTOLIST_SELECT_TASK_PRIORITY"
        assert e.priority == "High"

    def test_task_added_parse(self):
        e = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "Fix bug", "description": "Desc", "priority": "Medium"}))
        assert e.event_name == "AUTOLIST_TASK_ADDED"
        assert e.name == "Fix bug"
        assert e.priority == "Medium"

    def test_team_members_added_parse(self):
        e = TeamMembersAddedEvent.parse(_be("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 2, "members": ["Alice", "Bob"]}))
        assert e.event_name == "AUTOLIST_TEAM_MEMBERS_ADDED"
        assert e.member_count == 2
        assert e.members == ["Alice", "Bob"]

    def test_team_role_assigned_parse(self):
        e = TeamRoleAssignedEvent.parse(_be("AUTOLIST_TEAM_ROLE_ASSIGNED", {"memberId": "m1", "role": "lead"}))
        assert e.event_name == "AUTOLIST_TEAM_ROLE_ASSIGNED"
        assert e.member == "m1"
        assert e.role == "lead"


class TestValidateAutolistEvents:
    def test_task_added_validate_none(self):
        e = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "T", "description": "D", "priority": "P"}))
        assert e.validate_criteria(None) is True

    def test_task_added_validate_criteria(self):
        e = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "Deploy", "description": "Prod", "priority": "High"}))
        criteria = TaskAddedEvent.ValidationCriteria(name="Deploy", priority="High")
        assert e.validate_criteria(criteria) is True

    def test_team_members_added_validate_none(self):
        e = TeamMembersAddedEvent.parse(_be("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 0, "members": []}))
        assert e.validate_criteria(None) is True


@pytest.mark.parametrize("event_name,data", AUTOLIST_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
