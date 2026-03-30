"""Unit tests for automail_6 events (parse) to improve coverage."""

import pytest

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.criterion_helper import CriterionValue
from autoppia_iwa.src.demo_webs.projects.p06_automail.events import (
    BACKEND_EVENT_TYPES,
    AddLabelEvent,
    CreateLabelEvent,
    EditDraftEmailEvent,
    EmailSaveAsDraftEvent,
    ForwardEmailEvent,
    MarkAsSpamEvent,
    MarkAsUnreadEvent,
    MarkEmailAsImportantEvent,
    ReplyEmailEvent,
    SearchEmailEvent,
    SendEmailEvent,
    StarEmailEvent,
    TemplateBodyEditedEvent,
    TemplateSelectedEvent,
    TemplateSentEvent,
    ThemeChangedEvent,
    ViewEmailEvent,
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


def test_view_email_and_simple_flag_events_validate():
    view = ViewEmailEvent.parse(_be("VIEW_EMAIL", {"subject": "Hi", "from": "a@b.com"}))
    star = StarEmailEvent.parse(_be("STAR_AN_EMAIL", {"subject": "Hi", "from": "a@b.com", "is_star": False}))
    important = MarkEmailAsImportantEvent.parse(_be("MARK_EMAIL_AS_IMPORTANT", {"subject": "Hi", "from": "a@b.com", "is_important": True}))
    unread = MarkAsUnreadEvent.parse(_be("MARK_AS_UNREAD", {"subject": "Hi", "from": "a@b.com", "is_read": False}))
    spam = MarkAsSpamEvent.parse(_be("MARK_AS_SPAM", {"subject": "Hi", "from": "a@b.com", "is_spam": True}))
    assert view.validate_criteria(ViewEmailEvent.ValidationCriteria(subject="Hi", from_email="a@b.com"))
    assert star.validate_criteria(StarEmailEvent.ValidationCriteria(subject="Hi", from_email="a@b.com", is_starred=True))
    assert important.validate_criteria(MarkEmailAsImportantEvent.ValidationCriteria(is_important=True, subject="Hi"))
    assert unread.validate_criteria(MarkAsUnreadEvent.ValidationCriteria(is_read=False, subject="Hi"))
    assert spam.validate_criteria(MarkAsSpamEvent.ValidationCriteria(is_spam=True, subject="Hi"))


def test_add_and_create_label_validate():
    event = AddLabelEvent.parse(_be("ADD_LABEL", {"label_name": "Work", "emails": [{"subject": "Roadmap", "body": "Plan"}]}))
    created = CreateLabelEvent.parse(_be("CREATE_LABEL", {"label_name": "Work"}))
    assert event.validate_criteria(AddLabelEvent.ValidationCriteria(label_name="Work", subject="Roadmap", body="Plan"))
    assert created.validate_criteria(CreateLabelEvent.ValidationCriteria(label_name="Work"))


def test_send_draft_reply_and_forward_validate():
    payload = {"to": ["x@y.com"], "subject": "Hello", "body": "World", "from": "a@b.com"}
    send = SendEmailEvent.parse(_be("SEND_EMAIL", payload))
    draft = EmailSaveAsDraftEvent.parse(_be("EMAIL_SAVE_AS_DRAFT", payload))
    edit = EditDraftEmailEvent.parse(_be("EDIT_DRAFT_EMAIL", payload))
    reply = ReplyEmailEvent.parse(_be("REPLY_EMAIL", payload))
    forward = ForwardEmailEvent.parse(_be("FORWARD_EMAIL", payload))
    criteria = SendEmailEvent.ValidationCriteria(to="x@y.com", subject="Hello", body="World")
    assert send.validate_criteria(criteria)
    assert draft.validate_criteria(EmailSaveAsDraftEvent.ValidationCriteria(to="x@y.com", subject="Hello", body="World"))
    assert edit.validate_criteria(EmailSaveAsDraftEvent.ValidationCriteria(to="x@y.com", subject="Hello", body="World"))
    assert reply.validate_criteria(ReplyEmailEvent.ValidationCriteria(to="x@y.com", subject="Hello", from_email="a@b.com"))
    assert forward.validate_criteria(ForwardEmailEvent.ValidationCriteria(to="x@y.com", subject="Hello", from_email="a@b.com"))


def test_theme_and_templates_validate():
    theme = ThemeChangedEvent.parse(_be("THEME_CHANGED", {"theme": "dark"}))
    selected = TemplateSelectedEvent.parse(_be("TEMPLATE_SELECTED", {"template_name": "Promo", "subject": "Sale"}))
    edited = TemplateBodyEditedEvent.parse(_be("TEMPLATE_BODY_EDITED", {"template_name": "Promo", "subject": "Sale", "body": "Buy now"}))
    sent = TemplateSentEvent.parse(_be("TEMPLATE_SENT", {"template_name": "Promo", "subject": "Sale", "to": "x@y.com", "body": "Buy now"}))
    assert theme.validate_criteria(ThemeChangedEvent.ValidationCriteria(theme="dark"))
    assert selected.validate_criteria(TemplateSelectedEvent.ValidationCriteria(template_name="Promo", subject="Sale"))
    assert edited.validate_criteria(TemplateBodyEditedEvent.ValidationCriteria(template_name="Promo", subject="Sale", body="Buy now"))
    assert sent.validate_criteria(TemplateSentEvent.ValidationCriteria(template_name="Promo", subject="Sale", to="x@y.com", body="Buy now"))


def test_search_email_criterion_value():
    event = SearchEmailEvent.parse(_be("SEARCH_EMAIL", {"query": "invoice"}))
    assert event.validate_criteria(SearchEmailEvent.ValidationCriteria(query=CriterionValue(operator="contains", value="voice")))
