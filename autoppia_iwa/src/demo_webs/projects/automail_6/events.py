from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue, validate_criterion

# =============================================================================
#                            USER EVENTS
# =============================================================================


class ViewEmailEvent(Event):
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
        """
        Validate if this registration event meets the criteria.
        """
        if not criteria:
            return True
        if criteria.email_id is not None:
            return validate_criterion(self.email_id, criteria.email_id)
        if criteria.subject is not None:
            return validate_criterion(self.subject, criteria.subject)
        if criteria.from_email is not None:
            return validate_criterion(self.from_email, criteria.from_email)
        return True

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


class StarEmailEvent(Event):
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
        if criteria.email_id is not None:
            return validate_criterion(self.email_id, criteria.email_id)
        if criteria.subject is not None:
            return validate_criterion(self.subject, criteria.subject)
        if criteria.from_email is not None:
            return validate_criterion(self.from_email, criteria.from_email)
        if criteria.isStarred is not None:
            return validate_criterion(self.is_starred, criteria.isStarred)
        return True

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


class MarkEmailAsImportantEvent(ViewEmailEvent):
    event_name: str = "MARK_EMAIL_AS_IMPORTANT"
    is_important: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_important: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not self._validate_common(criteria):
            return False
        if criteria and criteria.is_important is not None:
            return validate_criterion(self.is_important, criteria.is_important)
        return True

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


class MarkAsUnreadEvent(ViewEmailEvent):
    event_name: str = "MARK_AS_UNREAD"
    is_read: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_read: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not self._validate_common(criteria):
            return False
        if criteria and criteria.is_unread is not None:
            return validate_criterion(self.is_read, criteria.is_read)
        return True

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


class DeleteEmailEvent(ViewEmailEvent):
    event_name: str = "DELETE_EMAIL"
    is_deleted: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_deleted: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not self._validate_common(criteria):
            return False
        if criteria and criteria.is_deleted is not None:
            return validate_criterion(self.is_deleted, criteria.is_deleted)
        return True

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
            is_deleted=data.get("is_deleted", False),
        )


class MarkAsSpamEvent(ViewEmailEvent):
    event_name: str = "MARK_AS_SPAM"
    is_spam: bool

    class ValidationCriteria(ViewEmailEvent.ValidationCriteria):
        is_spam: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not self._validate_common(criteria):
            return False
        if criteria and criteria.is_spam is not None:
            return validate_criterion(self.is_spam, criteria.is_spam)
        return True

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


class AddLabelEvent(Event):
    event_name: str = "ADD_LABEL"
    label_id: str
    label_name: str
    email_ids: list[str]
    action: str

    class ValidationCriteria(BaseModel):
        label_id: str | CriterionValue | None = None
        label_name: str | CriterionValue | None = None
        action: str | CriterionValue | None = None
        email_ids: list[str]

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.label_id is not None:
            return validate_criterion(self.label_id, criteria.label_id)
        if criteria.label_name is not None:
            return validate_criterion(self.label_name, criteria.label_name)
        if criteria.email_ids is not None:
            return validate_criterion(self.email_ids, criteria.email_ids)
        if criteria.action is not None:
            return validate_criterion(self.action, criteria.action)
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddLabelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            label_id=data.get("label_id", ""),
            label_name=data.get("label_name", ""),
            email_ids=data.get("email_ids", []),
            action=data.get("action", ""),
        )


class CreateLabelEvent(Event):
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
        if criteria.label_name is not None:
            return validate_criterion(self.label_name, criteria.label_name)
        if criteria.label_color is not None:
            return validate_criterion(self.label_color, criteria.label_color)
        return True

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


class ComposeEmailEvent(Event):
    event_name: str = "COMPOSE_EMAIL"
    action: str

    class ValidationCriteria(BaseModel):
        action: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.action is not None:
            return validate_criterion(self.action, criteria.action)
        return True

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


class SendEmailEvent(Event):
    event_name: str = "SEND_EMAIL"
    to: list[str]
    subject: str

    class ValidationCriteria(BaseModel):
        to: list[str] | CriterionValue | None = None
        subject: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.to is not None:
            return validate_criterion(self.to, criteria.to)
        if criteria.subject is not None:
            return validate_criterion(self.subject, criteria.subject)
        return True

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


class EmailSaveAsDraftEvent(Event):
    event_name: str = "EMAIL_SAVE_AS_DRAFT"
    to: list[str]
    subject: str
    body_length: int
    attachments_count: int

    class ValidationCriteria(BaseModel):
        subject: str | CriterionValue | None = None
        body_length: int | CriterionValue | None = None
        attachments_count: int | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.to is not None:
            return validate_criterion(self.to, criteria.to)
        if criteria.subject is not None:
            return validate_criterion(self.subject, criteria.subject)
        if criteria.body_length is not None:
            return validate_criterion(self.body_length, criteria.body_length)
        if criteria.attachments_count is not None:
            return validate_criterion(self.attachments_count, criteria.attachments_count)
        return True

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


class ThemeChangedEvent(Event):
    event_name: str = "THEME_CHANGED"
    theme: str

    class ValidationCriteria(BaseModel):
        theme: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.theme is not None:
            return validate_criterion(self.theme, criteria.theme)
        return True

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


class SearchEmailEvent(Event):
    event_name: str = "SEARCH_EMAIL"
    query: str

    class ValidationCriteria(BaseModel):
        query: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        if criteria.query is not None:
            return validate_criterion(self.query, criteria.query)
        return True

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
