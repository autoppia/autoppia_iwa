from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


# =============================================================================
#                            USER EVENTS
# =============================================================================
class Email(BaseModel):
    body: str
    subject: str

    class Config:
        title = "Email"
        description = "Email from adding a label to a single email or bulk of emails"


class ViewEmailEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_EMAIL"
    subject: str
    from_email: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating registration events"""

        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewEmailEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
        )


class StarEmailEvent(Event, BaseEventValidator):
    event_name: str = "STAR_AN_EMAIL"
    subject: str
    from_email: str
    is_starred: bool

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None
        is_starred: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
                self._validate_field(self.is_starred, criteria.is_starred),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "StarEmailEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            # is_starred=data.get("is_star", False),
            is_starred=not data.get("is_star", False),
        )


class MarkEmailAsImportantEvent(ViewEmailEvent, BaseEventValidator):
    event_name: str = "MARK_EMAIL_AS_IMPORTANT"
    is_important: bool | None = None

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_important: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.is_important, criteria.is_important),
                ViewEmailEvent._validate_criteria(self, criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "MarkEmailAsImportantEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_important=data.get("is_important"),
        )


class MarkAsUnreadEvent(ViewEmailEvent, BaseEventValidator):
    event_name: str = "MARK_AS_UNREAD"
    is_read: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_read: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.is_read, criteria.is_read),
                ViewEmailEvent._validate_criteria(self, criteria),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "MarkAsUnreadEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_read=data.get("is_read", True),
        )


class DeleteEmailEvent(Event, BaseEventValidator):
    event_name: str = "DELETE_EMAIL"
    subject: str
    from_email: str

    class ValidationCriteria(Event.ValidationCriteria):
        """Criteria for validating delete email events"""

        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteEmailEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
        )


class MarkAsSpamEvent(ViewEmailEvent, BaseEventValidator):
    event_name: str = "MARK_AS_SPAM"
    is_spam: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_spam: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                ViewEmailEvent._validate_criteria(self, criteria),
                self._validate_field(self.is_spam, criteria.is_spam),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "MarkAsSpamEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_spam=data.get("is_spam", False),
        )


class AddLabelEvent(Event, BaseEventValidator):
    event_name: str = "ADD_LABEL"
    label_name: str
    emails: list[Email] | None = None

    class ValidationCriteria(BaseModel):
        label_name: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        body: str | CriterionValue | None = None

    def _should_validate_emails(self, criteria: ValidationCriteria) -> bool:
        """Check if email validation is needed."""
        return bool((criteria.subject or criteria.body) and self.emails)

    def _validate_email_fields(self, email: Email, criteria: ValidationCriteria) -> bool:
        """Validate subject and body fields for a single email."""
        if criteria.subject and not self._validate_field(email.subject, criteria.subject):
            return False
        if criteria.body and not self._validate_field(email.body, criteria.body):
            return False
        return True

    def _validate_all_emails(self, criteria: ValidationCriteria) -> bool:
        """Validate all emails in the list."""
        if not self.emails:
            return True
        for email in self.emails:
            if not isinstance(email, Email):
                continue
            if not self._validate_email_fields(email, criteria):
                return False
        return True

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if not self._validate_field(self.label_name, criteria.label_name):
            return False
        if self._should_validate_emails(criteria):
            return self._validate_all_emails(criteria)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddLabelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        emails = [Email(**e) for e in data.get("emails", []) if isinstance(e, dict)]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            label_name=data.get("label_name", ""),
            emails=emails,
        )


class CreateLabelEvent(Event, BaseEventValidator):
    event_name: str = "CREATE_LABEL"
    label_name: str

    class ValidationCriteria(BaseModel):
        label_id: str | CriterionValue | None = None
        label_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.label_name, criteria.label_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CreateLabelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            label_name=data.get("label_name", ""),
        )


# ---------------------------------------------------------------------------
# Send / Draft
# ---------------------------------------------------------------------------


class SendEmailEvent(Event, BaseEventValidator):
    event_name: str = "SEND_EMAIL"
    to: list[str]
    subject: str
    body: str

    class ValidationCriteria(BaseModel):
        to: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        body: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                any(self._validate_field(_to, criteria.to) for _to in self.to),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.body, criteria.body),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SendEmailEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            to=data.get("to", []),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
        )


class EmailSaveAsDraftEvent(Event, BaseEventValidator):
    event_name: str = "EMAIL_SAVE_AS_DRAFT"
    to: list[str]
    subject: str
    body: str

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        body: str | CriterionValue | None = None
        to: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                any(self._validate_field(_to, criteria.to) for _to in self.to),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.body, criteria.body),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmailSaveAsDraftEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            to=data.get("to", []),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
        )


class EditDraftEmailEvent(EmailSaveAsDraftEvent):
    event_name: str = "EDIT_DRAFT_EMAIL"


class ArchiveEmailEvent(ViewEmailEvent):
    event_name: str = "ARCHIVE_EMAIL"


class ReplyEmailEvent(Event, BaseEventValidator):
    event_name: str = "REPLY_EMAIL"
    subject: str
    from_email: str
    to: list[str]

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None
        to: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
                any(self._validate_field(addr, criteria.to) for addr in self.to) if criteria.to else True,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ReplyEmailEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            to=data.get("to", []),
        )


class ForwardEmailEvent(Event, BaseEventValidator):
    event_name: str = "FORWARD_EMAIL"
    subject: str
    from_email: str
    to: list[str]

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None
        to: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
                any(self._validate_field(addr, criteria.to) for addr in self.to) if criteria.to else True,
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ForwardEmailEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            to=data.get("to", []),
        )


# ---------------------------------------------------------------------------
# UI / UX settings
# ---------------------------------------------------------------------------


class ThemeChangedEvent(Event, BaseEventValidator):
    event_name: str = "THEME_CHANGED"
    theme: str

    class ValidationCriteria(BaseModel):
        theme: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.theme, criteria.theme)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ThemeChangedEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            theme=backend_event.data.get("theme", ""),
        )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class SearchEmailEvent(Event, BaseEventValidator):
    event_name: str = "SEARCH_EMAIL"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.query, criteria.query)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SearchEmailEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            query=backend_event.data.get("query", ""),
        )


class ClearSelectionEvent(Event, BaseEventValidator):
    event_name: str = "CLEAR_SELECTION"


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------


class EmailsNextPageEvent(Event, BaseEventValidator):
    event_name: str = "EMAILS_NEXT_PAGE"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "EmailsNextPageEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
        )


class EmailsPrevPageEvent(EmailsNextPageEvent):
    event_name: str = "EMAILS_PREV_PAGE"


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


class TemplatesViewedEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_TEMPLATES"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TemplatesViewedEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
        )


class TemplateSelectedEvent(Event, BaseEventValidator):
    event_name: str = "TEMPLATE_SELECTED"
    template_name: str | None = None
    subject: str | None = None

    class ValidationCriteria(BaseModel):
        template_name: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.template_name, criteria.template_name),
                self._validate_field(self.subject, criteria.subject),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TemplateSelectedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            template_name=data.get("template_name"),
            subject=data.get("subject"),
        )


class TemplateBodyEditedEvent(Event, BaseEventValidator):
    event_name: str = "TEMPLATE_BODY_EDITED"
    template_name: str | None = None
    subject: str | None = None
    body: str | None = None

    class ValidationCriteria(BaseModel):
        template_name: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        body: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.template_name, criteria.template_name),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.body, criteria.body),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TemplateBodyEditedEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            template_name=data.get("template_name"),
            subject=data.get("subject"),
            body=data.get("body"),
        )


class TemplateSentEvent(Event, BaseEventValidator):
    event_name: str = "TEMPLATE_SENT"
    template_name: str | None = None
    subject: str | None = None
    to: str | None = None
    body: str | None = None

    class ValidationCriteria(BaseModel):
        template_name: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        to: str | CriterionValue | None = None
        body: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.template_name, criteria.template_name),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.to, criteria.to),
                self._validate_field(self.body, criteria.body),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "TemplateSentEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            template_name=data.get("template_name"),
            subject=data.get("subject"),
            to=data.get("to"),
            body=data.get("body"),
        )


class TemplateSavedDraftEvent(TemplateSentEvent):
    event_name: str = "TEMPLATE_SAVED_DRAFT"


class TemplateCanceledEvent(TemplateSentEvent):
    event_name: str = "TEMPLATE_CANCELED"


EVENTS = [
    ViewEmailEvent,
    StarEmailEvent,
    MarkEmailAsImportantEvent,
    MarkAsUnreadEvent,
    DeleteEmailEvent,
    MarkAsSpamEvent,
    AddLabelEvent,
    CreateLabelEvent,
    SendEmailEvent,
    EmailSaveAsDraftEvent,
    EditDraftEmailEvent,
    ArchiveEmailEvent,
    ReplyEmailEvent,
    ForwardEmailEvent,
    ThemeChangedEvent,
    SearchEmailEvent,
    ClearSelectionEvent,
    EmailsNextPageEvent,
    EmailsPrevPageEvent,
    TemplatesViewedEvent,
    TemplateSelectedEvent,
    TemplateBodyEditedEvent,
    TemplateSentEvent,
    TemplateSavedDraftEvent,
    TemplateCanceledEvent,
]
BACKEND_EVENT_TYPES = {
    "VIEW_EMAIL": ViewEmailEvent,
    "STAR_AN_EMAIL": StarEmailEvent,
    "MARK_EMAIL_AS_IMPORTANT": MarkEmailAsImportantEvent,
    "MARK_AS_UNREAD": MarkAsUnreadEvent,
    "DELETE_EMAIL": DeleteEmailEvent,
    "MARK_AS_SPAM": MarkAsSpamEvent,
    "ADD_LABEL": AddLabelEvent,
    "CREATE_LABEL": CreateLabelEvent,
    "SEND_EMAIL": SendEmailEvent,
    "EMAIL_SAVE_AS_DRAFT": EmailSaveAsDraftEvent,
    "EDIT_DRAFT_EMAIL": EditDraftEmailEvent,
    "ARCHIVE_EMAIL": ArchiveEmailEvent,
    "REPLY_EMAIL": ReplyEmailEvent,
    "FORWARD_EMAIL": ForwardEmailEvent,
    "THEME_CHANGED": ThemeChangedEvent,
    "SEARCH_EMAIL": SearchEmailEvent,
    "CLEAR_SELECTION": ClearSelectionEvent,
    "EMAILS_NEXT_PAGE": EmailsNextPageEvent,
    "EMAILS_PREV_PAGE": EmailsPrevPageEvent,
    "VIEW_TEMPLATES": TemplatesViewedEvent,
    "TEMPLATE_SELECTED": TemplateSelectedEvent,
    "TEMPLATE_BODY_EDITED": TemplateBodyEditedEvent,
    "TEMPLATE_SENT": TemplateSentEvent,
    "TEMPLATE_SAVED_DRAFT": TemplateSavedDraftEvent,
    "TEMPLATE_CANCELED": TemplateCanceledEvent,
}
