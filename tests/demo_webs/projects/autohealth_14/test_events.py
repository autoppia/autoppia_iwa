"""Unit tests for autohealth_14 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.autohealth_14.events import (
    BACKEND_EVENT_TYPES,
    SearchDoctorsEvent,
)

from ..event_parse_helpers import assert_parse_cls_kwargs_match_model


def _be(event_name: str, data: dict | None = None, web_agent_id: str = "test-agent", **kwargs) -> BackendEvent:
    return BackendEvent(event_name=event_name, data=data or {}, web_agent_id=web_agent_id, **kwargs)


# Many events use data.get("data") or {} so pass {"data": {}} or {}
AUTOHEALTH_PAYLOADS = [
    ("APPOINTMENT_BOOKED_SUCCESSFULLY", {"data": {}}),
    ("REQUEST_QUICK_APPOINTMENT", {"data": {}}),
    ("SEARCH_APPOINTMENT", {"data": {}}),
    ("SEARCH_DOCTORS", {"data": {}}),
    ("SEARCH_PRESCRIPTION", {"data": {}}),
    ("VIEW_PRESCRIPTION", {"data": {}}),
    ("REFILL_PRESCRIPTION", {"data": {}}),
    ("SEARCH_MEDICAL_ANALYSIS", {"data": {}}),
    ("VIEW_MEDICAL_ANALYSIS", {"data": {}}),
    ("VIEW_DOCTOR_PROFILE", {"data": {}}),
    ("VIEW_DOCTOR_EDUCATION", {"data": {}}),
    ("VIEW_DOCTOR_AVAILABILITY", {"data": {}}),
    ("OPEN_APPOINTMENT_FORM", {"data": {}}),
    ("OPEN_CONTACT_DOCTOR_FORM", {"data": {}}),
    ("CONTACT_DOCTOR", {"data": {}}),
    ("DOCTOR_CONTACTED_SUCCESSFULLY", {"data": {"doctorName": "D", "message": "m", "patientEmail": "e@e.com", "patientName": "P"}}),
    ("FILTER_DOCTOR_REVIEWS", {"data": {}}),
]


class TestParseAutohealthEvents:
    def test_search_doctors_parse(self):
        e = SearchDoctorsEvent.parse(_be("SEARCH_DOCTORS", {"data": {"doctorName": "Smith"}}))
        assert e.event_name == "SEARCH_DOCTORS"


@pytest.mark.parametrize("event_name,data", AUTOHEALTH_PAYLOADS)
def test_backend_event_types_parse(event_name, data):
    event_class = BACKEND_EVENT_TYPES[event_name]
    e = event_class.parse(_be(event_name, data))
    assert e.event_name == event_name
    assert_parse_cls_kwargs_match_model(event_class)
