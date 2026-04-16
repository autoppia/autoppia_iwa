"""Unit tests for autocalendar_11 events (parse + validate_criteria) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.p11_autocalendar.events import (
    BACKEND_EVENT_TYPES,
    CreateCalendarEvent,
    SearchSubmitEvent,
    UnselectCalendarEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# AddEventEvent (and subclasses) require startTime/endTime as [hour, minute] to avoid strptime empty string
ADD_EVENT_MINIMAL = {
    "startTime": [9, 0],
    "endTime": [10, 0],
    "date": "2025-01-15",
}

AUTOCALENDAR_PAYLOADS = [
    ("SELECT_MONTH", {}),
    ("SELECT_WEEK", {}),
    ("SELECT_FIVE_DAYS", {}),
    ("SELECT_DAY", {}),
    ("SELECT_TODAY", {}),
    ("ADD_NEW_CALENDAR", {}),
    ("CREATE_CALENDAR", {"name": "Work", "description": "Work calendar"}),
    ("UNSELECT_CALENDAR", {"calendarName": "Home"}),
    ("SELECT_CALENDAR", {"calendarName": "Work"}),
    ("ADD_EVENT", ADD_EVENT_MINIMAL),
    ("CELL_CLICKED", {"view": "week", "date": "2025-01-15"}),
    ("CANCEL_ADD_EVENT", ADD_EVENT_MINIMAL),
    ("DELETE_ADDED_EVENT", ADD_EVENT_MINIMAL),
    ("SEARCH_SUBMIT", {"query": "meeting"}),
    ("EVENT_WIZARD_OPEN", {"title": "Team sync", "date": "2025-01-15"}),
    ("EVENT_ADD_REMINDER", {"minutes": 15}),
    ("EVENT_REMOVE_REMINDER", {"minutes": 10}),
    ("EVENT_ADD_ATTENDEE", {"email": "a@b.com"}),
    ("EVENT_REMOVE_ATTENDEE", {"email": "b@c.com"}),
]


class TestParseAutocalendarEvents:
    def test_create_calendar_parse(self):
        e = CreateCalendarEvent.parse(_be("CREATE_CALENDAR", {"name": "Work", "description": "Work calendar"}))
        assert e.event_name == "CREATE_CALENDAR"
        assert e.name == "Work"
        assert e.description == "Work calendar"

    def test_search_submit_parse(self):
        e = SearchSubmitEvent.parse(_be("SEARCH_SUBMIT", {"query": "standup"}))
        assert e.event_name == "SEARCH_SUBMIT"
        assert e.query == "standup"

    def test_unselect_calendar_parse(self):
        e = UnselectCalendarEvent.parse(_be("UNSELECT_CALENDAR", {"calendarName": "Home"}))
        assert e.event_name == "UNSELECT_CALENDAR"
        assert e.calendar_name == "Home"


class TestValidateAutocalendarEvents:
    def test_create_calendar_validate_none(self):
        e = CreateCalendarEvent.parse(_be("CREATE_CALENDAR", {"name": "X", "description": "Y"}))
        assert e.validate_criteria(None) is True

    def test_create_calendar_validate_criteria(self):
        e = CreateCalendarEvent.parse(_be("CREATE_CALENDAR", {"name": "Work", "description": "Desc"}))
        criteria = CreateCalendarEvent.ValidationCriteria(name="Work", description="Desc")
        assert e.validate_criteria(criteria) is True

    def test_search_submit_validate_query(self):
        e = SearchSubmitEvent.parse(_be("SEARCH_SUBMIT", {"query": "meeting"}))
        criteria = SearchSubmitEvent.ValidationCriteria(query="meeting")
        assert e.validate_criteria(criteria) is True


@pytest.mark.parametrize("event_name,data", AUTOCALENDAR_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
