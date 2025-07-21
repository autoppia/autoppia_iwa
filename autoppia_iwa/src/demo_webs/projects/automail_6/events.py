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
    email_id: str
    subject: str
    from_email: str

    class ValidationCriteria(BaseModel):
        """Criteria for validating registration events"""

        email_id: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.email_id, criteria.email_id),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewEmailEvent":
        """
        Parse a registration event from backend data.
        """
        base_event = Event.parse(backend_event)
        data = backend_event.data
        email_id = data.get("email_id", "")
        subject = data.get("subject", "")
        from_email = data.get("from", "")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            email_id=email_id,
            subject=subject,
            from_email=from_email,
        )


class StarEmailEvent(Event, BaseEventValidator):
    event_name: str = "STAR_AN_EMAIL"
    email_id: str
    subject: str
    from_email: str
    is_starred: bool

    class ValidationCriteria(BaseModel):
        email_id: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None
        isStarred: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.email_id, criteria.email_id),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.from_email, criteria.from_email),
                self._validate_field(self.is_starred, criteria.isStarred),
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
            email_id=data.get("email_id", ""),
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_starred=data.get("is_star", False),
        )


class MarkEmailAsImportantEvent(ViewEmailEvent, BaseEventValidator):
    event_name: str = "MARK_EMAIL_AS_IMPORTANT"
    is_important: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_important: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.email_id, getattr(criteria, "email_id", None)),
                self._validate_field(self.subject, getattr(criteria, "subject", None)),
                self._validate_field(self.from_email, getattr(criteria, "from_email", None)),
                self._validate_field(self.is_important, getattr(criteria, "is_important", None)),
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
            email_id=data.get("email_id", ""),
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_important=data.get("is_important", False),
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
                self._validate_field(self.email_id, getattr(criteria, "email_id", None)),
                self._validate_field(self.subject, getattr(criteria, "subject", None)),
                self._validate_field(self.from_email, getattr(criteria, "from_email", None)),
                self._validate_field(self.is_read, getattr(criteria, "is_read", None)),
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
            email_id=data.get("email_id", ""),
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_read=data.get("is_read", False),
        )


class DeleteEmailEvent(Event, BaseEventValidator):
    event_name: str = "DELETE_EMAIL"
    email_id: str
    subject: str
    from_email: str

    class ValidationCriteria(Event.ValidationCriteria):
        """Criteria for validating delete email events"""

        email_id: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        from_email: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.email_id, criteria.email_id),
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
            email_id=data.get("email_id", ""),
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
                self._validate_field(self.email_id, getattr(criteria, "email_id", None)),
                self._validate_field(self.subject, getattr(criteria, "subject", None)),
                self._validate_field(self.from_email, getattr(criteria, "from_email", None)),
                self._validate_field(self.is_spam, getattr(criteria, "is_spam", None)),
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
            email_id=data.get("email_id", ""),
            subject=data.get("subject", ""),
            from_email=data.get("from", ""),
            is_spam=data.get("is_spam", False),
        )


class AddLabelEvent(Event, BaseEventValidator):
    event_name: str = "ADD_LABEL"
    # label_id: str
    label_name: str
    emails: list[Email] | None = None
    action: str

    class ValidationCriteria(BaseModel):
        # label_id: str | CriterionValue | None = None
        label_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        body: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True

        # Validate label_name and action first
        if not self._validate_field(self.label_name, criteria.label_name):
            return False
        if not self._validate_field(self.action, criteria.action):
            return False

        # Validate subject/body for emails if criteria present
        if (criteria.subject or criteria.body) and self.emails:
            for email in self.emails:
                if not isinstance(email, Email):
                    continue
                if criteria.subject and not self._validate_field(email.subject, criteria.subject):
                    return False
                if criteria.body and not self._validate_field(email.body, criteria.body):
                    return False

        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddLabelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        emails = []
        if "emails" in data and isinstance(data["emails"], list):
            emails = [Email(**e) for e in data["emails"]]
        elif "email_ids" in data and isinstance(data["email_ids"], list):
            emails = [Email(subject="", body="") for _ in data["email_ids"]]
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            # label_id=data.get("label_id", ""),
            label_name=data.get("label_name", ""),
            emails=emails,
            action=data.get("action", ""),
        )


class CreateLabelEvent(Event, BaseEventValidator):
    event_name: str = "CREATE_LABEL"
    label_name: str
    label_color: str

    class ValidationCriteria(BaseModel):
        label_id: str | CriterionValue | None = None
        label_name: str | CriterionValue | None = None
        label_color: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.label_name, criteria.label_name),
                self._validate_field(self.label_color, criteria.label_color),
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
            label_color=data.get("label_color", ""),
        )


# ---------------------------------------------------------------------------
# Compose / Send / Draft
# ---------------------------------------------------------------------------


class ComposeEmailEvent(Event, BaseEventValidator):
    event_name: str = "COMPOSE_EMAIL"
    action: str

    class ValidationCriteria(BaseModel):
        action: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.action, criteria.action)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ComposeEmailEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            action=backend_event.data.get("action", ""),
        )


class SendEmailEvent(Event, BaseEventValidator):
    event_name: str = "SEND_EMAIL"
    to: list[str]
    subject: str

    class ValidationCriteria(BaseModel):
        to: list[str] | CriterionValue | None = None
        subject: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.to, criteria.to),
                self._validate_field(self.subject, criteria.subject),
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
        )


class EmailSaveAsDraftEvent(Event, BaseEventValidator):
    event_name: str = "EMAIL_SAVE_AS_DRAFT"
    to: list[str]
    subject: str
    body_length: int
    attachments_count: int

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        body_length: int | CriterionValue | None = None
        attachments_count: int | CriterionValue | None = None
        to: list[str] | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.to, criteria.to),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.body_length, criteria.body_length),
                self._validate_field(self.attachments_count, criteria.attachments_count),
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
            body_length=data.get("body_length", 0),
            attachments_count=data.get("attachments_count", 0),
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


EVENTS = [
    ViewEmailEvent,
    StarEmailEvent,
    MarkEmailAsImportantEvent,
    MarkAsUnreadEvent,
    DeleteEmailEvent,
    MarkAsSpamEvent,
    AddLabelEvent,
    CreateLabelEvent,
    ComposeEmailEvent,
    SendEmailEvent,
    EmailSaveAsDraftEvent,
    ThemeChangedEvent,
    SearchEmailEvent,
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
    "COMPOSE_EMAIL": ComposeEmailEvent,
    "SEND_EMAIL": SendEmailEvent,
    "EMAIL_SAVE_AS_DRAFT": EmailSaveAsDraftEvent,
    "THEME_CHANGED": ThemeChangedEvent,
    "SEARCH_EMAIL": SearchEmailEvent,
}
