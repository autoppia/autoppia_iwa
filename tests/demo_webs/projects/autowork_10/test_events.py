"""Unit tests for autowork_10 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.p10_autowork.events import (
    BACKEND_EVENT_TYPES,
    BookAConsultationEvent,
    CancelHireEvent,
    ClosePostAJobWindowEvent,
    FavoriteExpertSelectedEvent,
    HireConsultantEvent,
    NavbarClickEvent,
    NavbarProfileClickEvent,
    SubmitJobEvent,
    _base_event_kwargs,
    _validate_criteria_fields,
    _validate_skill_criteria,
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
    ("AUTOWORK_CONTACT_PAGE_VIEWED", {}),
    ("AUTOWORK_CONTACT_FORM_SUBMITTED", {"name": "n", "email": "e@e.com", "subject": "s", "message": "message here"}),
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


def test_helper_functions_cover_true_and_false_paths():
    assert _validate_skill_criteria(["Python", "SQL"], None) is True
    assert _validate_skill_criteria(["Python", "SQL"], "py") is True
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="contains", value="yth")) is True
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="not_contains", value="java")) is True
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="in_list", value=["Python", "Go"])) is True
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="not_in_list", value=["Go"])) is True
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="in_list", value="Python")) is False
    assert _validate_skill_criteria(["Python"], CriterionValue(operator="not_in_list", value="Python")) is False

    dummy = BookAConsultationEvent(event_name="BOOK_A_CONSULTATION", timestamp=1, web_agent_id="a", user_id=None, country="ES")
    assert _validate_criteria_fields(dummy, None, ["country"]) is True
    assert _validate_criteria_fields(dummy, BookAConsultationEvent.ValidationCriteria(country="ES"), ["country"]) is True
    assert _validate_criteria_fields(dummy, BookAConsultationEvent.ValidationCriteria(country="US"), ["country"]) is False
    assert _base_event_kwargs(dummy, extra="x")["extra"] == "x"


def test_parse_and_negative_validation_paths():
    consult = BookAConsultationEvent.parse(_be("BOOK_A_CONSULTATION", {"country": "ES", "expertName": "Ana", "jobs": 4, "rate": "$50", "rating": 4.8, "role": "Designer", "expertSlug": "ana"}))
    assert consult.validate_criteria(BookAConsultationEvent.ValidationCriteria(name="Other")) is False

    hire = HireConsultantEvent.parse(
        _be(
            "HIRE_CONSULTANT",
            {"country": "ES", "expertName": "Ana", "paymentType": "hourly", "increaseHowMuch": "10%", "increaseWhen": "later", "role": "Designer"},
        )
    )
    assert hire.validate_criteria(HireConsultantEvent.ValidationCriteria(paymentType="fixed")) is False

    cancel = CancelHireEvent.parse(_be("CANCEL_HIRE", {"expert": {"country": "ES", "name": "Ana", "rate": "$50", "role": "Designer", "slug": "ana"}}))
    assert cancel.validate_criteria(CancelHireEvent.ValidationCriteria(slug="other")) is False

    navbar_profile = NavbarProfileClickEvent.parse(_be("NAVBAR_PROFILE_CLICK", {"label": "Profile", "href": "/profile"}))
    assert navbar_profile.label == "Profile"
    assert navbar_profile.href == "/profile"

    favorite = FavoriteExpertSelectedEvent.parse(_be("FAVORITE_EXPERT_SELECTED", {"expertName": "Ana", "expertSlug": "ana", "source": "card", "country": "ES", "role": "Designer"}))
    assert favorite.validate_criteria(FavoriteExpertSelectedEvent.ValidationCriteria(source="other")) is False


def test_submit_and_close_job_skill_validation_paths():
    payload = {
        "title": "Build app",
        "description": "Need help",
        "budgetType": "fixed",
        "scope": "medium",
        "duration": "1 month",
        "step": 2,
        "skills": ["Python", "SQL"],
        "rateFrom": "20",
        "rateTo": "40",
    }
    submitted = SubmitJobEvent.parse(_be("SUBMIT_JOB", payload))
    assert submitted.validate_criteria(SubmitJobEvent.ValidationCriteria(skills="Python", title="Build app")) is True
    assert submitted.validate_criteria(SubmitJobEvent.ValidationCriteria(skills=CriterionValue(operator="not_contains", value="Java"))) is True
    assert submitted.validate_criteria(SubmitJobEvent.ValidationCriteria(skills=CriterionValue(operator="in_list", value=["Go"]))) is False

    closed = ClosePostAJobWindowEvent.parse(_be("CLOSE_POST_A_JOB_WINDOW", payload))
    assert closed.validate_criteria(ClosePostAJobWindowEvent.ValidationCriteria(title="Other")) is False
