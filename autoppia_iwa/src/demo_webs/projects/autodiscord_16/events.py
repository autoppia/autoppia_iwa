# Event classes for autodiscord_16 — aligned with web_16_autodiscord src/library/events.ts
# Payload fields from logEvent() in ServerList, ChannelSidebar, ChatPanel, etc.

from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue

# =============================================================================
#                           EVENT CLASSES
# =============================================================================


class ViewServersEvent(Event, BaseEventValidator):
    """User clicks the Home (servers) icon."""

    event_name: str = "VIEW_SERVERS"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewServersEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
        )


class ViewDmsEvent(Event, BaseEventValidator):
    """User clicks the Direct Messages icon."""

    event_name: str = "VIEW_DMS"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "ViewDmsEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
        )


class SelectServerEvent(Event, BaseEventValidator):
    """User selects a server. Payload: server_name."""

    event_name: str = "SELECT_SERVER"
    server_name: str

    class ValidationCriteria(BaseModel):
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.server_name, criteria.server_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectServerEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            server_name=data.get("server_name", ""),
        )


class SelectChannelEvent(Event, BaseEventValidator):
    """User selects a channel. Payload: channel_name, server_name."""

    event_name: str = "SELECT_CHANNEL"
    channel_name: str
    server_name: str

    class ValidationCriteria(BaseModel):
        channel_name: str | CriterionValue | None = None
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all([self._validate_field(self.channel_name, criteria.channel_name), self._validate_field(self.server_name, criteria.server_name)])

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectChannelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_name=data.get("channel_name", ""),
            server_name=data.get("server_name", ""),
        )


class SendMessageEvent(Event, BaseEventValidator):
    """User sends a message in a channel. Payload: channel_name, content."""

    event_name: str = "SEND_MESSAGE"
    channel_name: str
    content: str

    class ValidationCriteria(BaseModel):
        channel_name: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.channel_name, criteria.channel_name),
                self._validate_field(self.content, criteria.content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SendMessageEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_name=data.get("channel_name", ""),
            content=data.get("content", ""),
        )


class AddReactionEvent(Event, BaseEventValidator):
    """User adds a reaction. Payload: message_id, channel_name."""

    event_name: str = "ADD_REACTION"
    message_id: str
    channel_name: str

    class ValidationCriteria(BaseModel):
        message_id: str | CriterionValue | None = None
        channel_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.message_id, criteria.message_id),
                self._validate_field(self.channel_name, criteria.channel_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "AddReactionEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            message_id=data.get("message_id", ""),
            channel_name=data.get("channel_name", ""),
        )


class SelectDmEvent(Event, BaseEventValidator):
    """User selects a DM conversation. Payload: display_name."""

    event_name: str = "SELECT_DM"
    display_name: str

    class ValidationCriteria(BaseModel):
        display_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.display_name, criteria.display_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SelectDmEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            display_name=data.get("display_name", ""),
        )


class SendDmMessageEvent(Event, BaseEventValidator):
    """User sends a message in a DM. Payload: peer_display_name, content."""

    event_name: str = "SEND_DM_MESSAGE"
    peer_display_name: str
    content: str

    class ValidationCriteria(BaseModel):
        peer_display_name: str | CriterionValue | None = None
        content: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.peer_display_name, criteria.peer_display_name),
                self._validate_field(self.content, criteria.content),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SendDmMessageEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            peer_display_name=data.get("peer_display_name", ""),
            content=data.get("content", ""),
        )


class OpenSettingsEvent(Event, BaseEventValidator):
    """User opens the Settings page."""

    event_name: str = "OPEN_SETTINGS"

    class ValidationCriteria(BaseModel):
        pass

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        return True

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "OpenSettingsEvent":
        base = Event.parse(backend_event)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
        )


class SettingsAppearanceEvent(Event, BaseEventValidator):
    """User changes theme. Payload: theme."""

    event_name: str = "SETTINGS_APPEARANCE"
    theme: str

    class ValidationCriteria(BaseModel):
        theme: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.theme, criteria.theme)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SettingsAppearanceEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            theme=data.get("theme", ""),
        )


class SettingsNotificationsEvent(Event, BaseEventValidator):
    """User toggles notifications. Payload: enabled (bool)."""

    event_name: str = "SETTINGS_NOTIFICATIONS"
    enabled: bool

    class ValidationCriteria(BaseModel):
        enabled: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.enabled, criteria.enabled)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SettingsNotificationsEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        raw = data.get("enabled")
        enabled = bool(raw) if raw is not None else False
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            enabled=enabled,
        )


class SettingsAccountEvent(Event, BaseEventValidator):
    """User saves display name. Payload: display_name."""

    event_name: str = "SETTINGS_ACCOUNT"
    display_name: str

    class ValidationCriteria(BaseModel):
        display_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.display_name, criteria.display_name)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "SettingsAccountEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            display_name=data.get("display_name", ""),
        )


class CreateServerEvent(Event, BaseEventValidator):
    """User creates a server. Payload: server_name."""

    event_name: str = "CREATE_SERVER"
    server_name: str

    class ValidationCriteria(BaseModel):
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return self._validate_field(self.server_name, criteria.server_name)

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CreateServerEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            server_name=data.get("server_name", ""),
        )


class OpenServerSettingsEvent(Event, BaseEventValidator):
    """User opens server settings. Payload: server_name."""

    event_name: str = "OPEN_SERVER_SETTINGS"
    server_name: str

    class ValidationCriteria(BaseModel):
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.server_name, criteria.server_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "OpenServerSettingsEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            server_name=data.get("server_name", ""),
        )


class DeleteServerEvent(Event, BaseEventValidator):
    """User deletes a server. Payload: server_name."""

    event_name: str = "DELETE_SERVER"
    server_name: str = ""

    class ValidationCriteria(BaseModel):
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.server_name, criteria.server_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "DeleteServerEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            server_name=data.get("server_name", ""),
        )


class CreateChannelEvent(Event, BaseEventValidator):
    """User creates a channel. Payload: server_name, channel_name."""

    event_name: str = "CREATE_CHANNEL"
    server_name: str
    channel_name: str
    channel_type: str

    class ValidationCriteria(BaseModel):
        server_name: str | CriterionValue | None = None
        channel_name: str | CriterionValue | None = None
        channel_type: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.channel_type, criteria.channel_type),
                self._validate_field(self.server_name, criteria.server_name),
                self._validate_field(self.channel_name, criteria.channel_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "CreateChannelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_type=data.get("channel_type", ""),
            server_name=data.get("server_name", ""),
            channel_name=data.get("channel_name", ""),
        )


class JoinVoiceChannelEvent(Event, BaseEventValidator):
    """User joins a voice channel. Payload: channel_name, server_name."""

    event_name: str = "JOIN_VOICE_CHANNEL"
    channel_name: str
    server_name: str

    class ValidationCriteria(BaseModel):
        channel_name: str | CriterionValue | None = None
        server_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.channel_name, criteria.channel_name),
                self._validate_field(self.server_name, criteria.server_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "JoinVoiceChannelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_name=data.get("channel_name", ""),
            server_name=data.get("server_name", ""),
        )


class LeaveVoiceChannelEvent(Event, BaseEventValidator):
    """User leaves a voice channel. Payload: channel_name."""

    event_name: str = "LEAVE_VOICE_CHANNEL"
    channel_name: str

    class ValidationCriteria(BaseModel):
        channel_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.channel_name, criteria.channel_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "LeaveVoiceChannelEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_name=data.get("channel_name", ""),
        )


class VoiceMuteToggleEvent(Event, BaseEventValidator):
    """User toggles mute in voice. Payload: channel_name, muted."""

    event_name: str = "VOICE_MUTE_TOGGLE"
    channel_name: str
    muted: bool

    class ValidationCriteria(BaseModel):
        channel_name: str | CriterionValue | None = None
        muted: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.channel_name, criteria.channel_name),
                self._validate_field(self.muted, criteria.muted),
            ]
        )

    @classmethod
    def parse(cls, backend_event: BackendEvent) -> "VoiceMuteToggleEvent":
        base = Event.parse(backend_event)
        data = backend_event.data or {}
        raw = data.get("muted")
        muted = bool(raw) if raw is not None else False
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            channel_name=data.get("channel_name", ""),
            muted=muted,
        )


# =============================================================================
#                    AVAILABLE EVENTS AND BACKEND MAP
# =============================================================================

EVENTS = [
    ViewServersEvent,
    ViewDmsEvent,
    SelectServerEvent,
    SelectChannelEvent,
    SendMessageEvent,
    AddReactionEvent,
    SelectDmEvent,
    SendDmMessageEvent,
    OpenSettingsEvent,
    SettingsAppearanceEvent,
    SettingsNotificationsEvent,
    SettingsAccountEvent,
    CreateServerEvent,
    OpenServerSettingsEvent,
    DeleteServerEvent,
    CreateChannelEvent,
    JoinVoiceChannelEvent,
    LeaveVoiceChannelEvent,
    VoiceMuteToggleEvent,
]

BACKEND_EVENT_TYPES = {
    "VIEW_SERVERS": ViewServersEvent,
    "VIEW_DMS": ViewDmsEvent,
    "SELECT_SERVER": SelectServerEvent,
    "SELECT_CHANNEL": SelectChannelEvent,
    "SEND_MESSAGE": SendMessageEvent,
    "ADD_REACTION": AddReactionEvent,
    "SELECT_DM": SelectDmEvent,
    "SEND_DM_MESSAGE": SendDmMessageEvent,
    "OPEN_SETTINGS": OpenSettingsEvent,
    "SETTINGS_APPEARANCE": SettingsAppearanceEvent,
    "SETTINGS_NOTIFICATIONS": SettingsNotificationsEvent,
    "SETTINGS_ACCOUNT": SettingsAccountEvent,
    "CREATE_SERVER": CreateServerEvent,
    "OPEN_SERVER_SETTINGS": OpenServerSettingsEvent,
    "DELETE_SERVER": DeleteServerEvent,
    "CREATE_CHANNEL": CreateChannelEvent,
    "JOIN_VOICE_CHANNEL": JoinVoiceChannelEvent,
    "LEAVE_VOICE_CHANNEL": LeaveVoiceChannelEvent,
    "VOICE_MUTE_TOGGLE": VoiceMuteToggleEvent,
}
