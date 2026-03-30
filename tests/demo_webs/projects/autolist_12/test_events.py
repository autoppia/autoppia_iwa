"""Unit tests for autolist_12 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.p12_autolist.events import (
    BACKEND_EVENT_TYPES,
    AddTaskClickedEvent,
    AddTeamClickedEvent,
    CancelTaskCreationEvent,
    CompleteTaskEvent,
    DeleteTaskEvent,
    EditTaskModalOpenedEvent,
    SelectDateForTaskEvent,
    SelectTaskPriorityEvent,
    TaskAddedEvent,
    TeamCreatedEvent,
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
    def test_select_date_for_task_validate(self):
        e = SelectDateForTaskEvent.parse(_be("AUTOLIST_SELECT_DATE_FOR_TASK", {"selectedDate": "2025-03-01T00:00:00", "quickOption": "today"}))
        criteria = SelectDateForTaskEvent.ValidationCriteria(quick_option="today")
        assert e.validate_criteria(criteria) is True

    def test_task_added_validate_none(self):
        e = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "T", "description": "D", "priority": "P"}))
        assert e.validate_criteria(None) is True

    def test_task_added_validate_criteria(self):
        e = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "Deploy", "description": "Prod", "priority": "High"}))
        criteria = TaskAddedEvent.ValidationCriteria(name="Deploy", priority="High")
        assert e.validate_criteria(criteria) is True

    def test_cancel_task_creation_validate(self):
        e = CancelTaskCreationEvent.parse(_be("AUTOLIST_CANCEL_TASK_CREATION", {"currentName": "Draft", "currentDescription": "Tmp", "priority": "Low"}))
        criteria = CancelTaskCreationEvent.ValidationCriteria(name="Draft", description="Tmp", priority="Low")
        assert e.validate_criteria(criteria) is True

    def test_team_members_added_validate_none(self):
        e = TeamMembersAddedEvent.parse(_be("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 0, "members": []}))
        assert e.validate_criteria(None) is True

    def test_team_members_added_validate_contains(self):
        e = TeamMembersAddedEvent.parse(_be("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 2, "members": ["Alice", "Bob"]}))
        criteria = TeamMembersAddedEvent.ValidationCriteria(member_count=2, members=CriterionValue(operator="contains", value=["ali"]))
        assert e.validate_criteria(criteria) is True

    def test_team_role_assigned_validate(self):
        e = TeamRoleAssignedEvent.parse(_be("AUTOLIST_TEAM_ROLE_ASSIGNED", {"memberId": "m1", "role": "lead"}))
        criteria = TeamRoleAssignedEvent.ValidationCriteria(member="m1", role="lead")
        assert e.validate_criteria(criteria) is True

    def test_team_created_validate(self):
        e = TeamCreatedEvent.parse(
            _be(
                "AUTOLIST_TEAM_CREATED",
                {
                    "teamName": "Core",
                    "teamDescription": "Main team",
                    "members": [{"id": "1", "name": "Alice", "role": "lead"}],
                },
            )
        )
        criteria = TeamCreatedEvent.ValidationCriteria(name="Core", description="Main team", member="Alice", role="lead")
        assert e.validate_criteria(criteria) is True

    def test_negative_validation_and_list_operator_paths(self):
        date_event = SelectDateForTaskEvent.parse(_be("AUTOLIST_SELECT_DATE_FOR_TASK", {"selectedDate": "2025-03-01T00:00:00", "quickOption": "today"}))
        assert date_event.validate_criteria(SelectDateForTaskEvent.ValidationCriteria(quick_option="tomorrow")) is False

        priority_event = SelectTaskPriorityEvent.parse(_be("AUTOLIST_SELECT_TASK_PRIORITY", {"label": "High"}))
        assert priority_event.validate_criteria(SelectTaskPriorityEvent.ValidationCriteria(priority="Low")) is False

        task = TaskAddedEvent.parse(_be("AUTOLIST_TASK_ADDED", {"name": "Deploy", "description": "Prod", "priority": "High"}))
        assert task.validate_criteria(TaskAddedEvent.ValidationCriteria(name="Other")) is False

        cancel = CancelTaskCreationEvent.parse(_be("AUTOLIST_CANCEL_TASK_CREATION", {"currentName": "Draft", "currentDescription": "Tmp", "priority": "Low"}))
        assert cancel.validate_criteria(CancelTaskCreationEvent.ValidationCriteria(priority="High")) is False

        members = TeamMembersAddedEvent.parse(_be("AUTOLIST_TEAM_MEMBERS_ADDED", {"memberCount": 2, "members": ["Alice", "Bob"]}))
        assert members.validate_criteria(TeamMembersAddedEvent.ValidationCriteria(member_count=3)) is False
        assert members.validate_criteria(TeamMembersAddedEvent.ValidationCriteria(members=["Alice"])) is False
        assert members.validate_criteria(TeamMembersAddedEvent.ValidationCriteria(members=CriterionValue(operator="not_contains", value=["ali"]))) is False
        assert members.validate_criteria(TeamMembersAddedEvent.ValidationCriteria(members=CriterionValue(operator="in_list", value=["Bob"]))) is True
        assert members.validate_criteria(TeamMembersAddedEvent.ValidationCriteria(members=CriterionValue(operator="not_in_list", value=["Alice"]))) is False

        role = TeamRoleAssignedEvent.parse(_be("AUTOLIST_TEAM_ROLE_ASSIGNED", {"memberId": "m1", "role": "lead"}))
        assert role.validate_criteria(TeamRoleAssignedEvent.ValidationCriteria(role="dev")) is False

        team = TeamCreatedEvent.parse(
            _be(
                "AUTOLIST_TEAM_CREATED",
                {
                    "teamName": "Core",
                    "teamDescription": "Main team",
                    "members": [{"id": "1", "name": "Alice", "role": "lead"}, {"id": "2", "name": "Bob", "role": "dev"}],
                },
            )
        )
        assert team.validate_criteria(TeamCreatedEvent.ValidationCriteria(member="Alice", role="lead")) is False
        assert team.validate_criteria(TeamCreatedEvent.ValidationCriteria(name="Other")) is False


def test_simple_event_classes_parse():
    assert AddTaskClickedEvent.parse(_be("AUTOLIST_ADD_TASK_CLICKED", {})).event_name == "AUTOLIST_ADD_TASK_CLICKED"
    assert AddTeamClickedEvent.parse(_be("AUTOLIST_ADD_TEAM_CLICKED", {})).event_name == "AUTOLIST_ADD_TEAM_CLICKED"
    assert EditTaskModalOpenedEvent.parse(_be("AUTOLIST_EDIT_TASK_MODAL_OPENED", {"name": "T", "description": "D", "priority": "P"})).event_name == "AUTOLIST_EDIT_TASK_MODAL_OPENED"
    assert CompleteTaskEvent.parse(_be("AUTOLIST_COMPLETE_TASK", {"name": "T", "description": "D", "priority": "P"})).event_name == "AUTOLIST_COMPLETE_TASK"
    assert DeleteTaskEvent.parse(_be("AUTOLIST_DELETE_TASK", {"name": "T", "description": "D", "priority": "P"})).event_name == "AUTOLIST_DELETE_TASK"


@pytest.mark.parametrize("event_name,data", AUTOLIST_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
