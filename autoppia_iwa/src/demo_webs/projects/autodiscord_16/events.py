"""Event classes for web_16_autodiscord (AutoDiscord).

Backend receives event_name + data from POST /api/log-event. Each event type
maps to a class that parses BackendEvent and optionally extracts payload fields.
"""

from typing import Any, TypeVar

from autoppia_iwa.src.demo_webs.classes import BackendEvent
from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event

_T = TypeVar("_T", bound="Event")


def _parse_data(backend_event: BackendEvent | None) -> dict[str, Any]:
    """Extract the inner payload dict from a backend event. Returns a dict never None."""
    if backend_event is None:
        return {}
    raw = getattr(backend_event, "data", None)
    if not isinstance(raw, dict):
        return {}
    inner = raw.get("data")
    return inner if isinstance(inner, dict) else {}


class AutodiscordEventBase(Event, BaseEventValidator):
    """Base for AutoDiscord events. Subclasses define event_name and optionally _payload_from_data."""

    def _validate_criteria(self, criteria: Any = None) -> bool:
        return True

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Build kwargs for the event from the backend payload. Override in subclasses with payload."""
        return {}

    @classmethod
    def parse(cls: type[_T], backend_event: BackendEvent) -> _T:
        base = Event.parse(backend_event)
        data = _parse_data(backend_event)
        payload = cls._payload_from_data(data)
        return cls(
            event_name=base.event_name,
            timestamp=base.timestamp,
            web_agent_id=base.web_agent_id,
            user_id=base.user_id,
            **payload,
        )


class ViewServersEvent(AutodiscordEventBase):
    event_name: str = "VIEW_SERVERS"


class ViewDmsEvent(AutodiscordEventBase):
    event_name: str = "VIEW_DMS"


class SelectServerEvent(AutodiscordEventBase):
    event_name: str = "SELECT_SERVER"
    server_id: str | None = None
    server_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "server_id": data.get("server_id"),
            "server_name": data.get("server_name"),
        }


class SelectChannelEvent(AutodiscordEventBase):
    event_name: str = "SELECT_CHANNEL"
    channel_id: str | None = None
    channel_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "channel_id": data.get("channel_id"),
            "channel_name": data.get("channel_name"),
        }


class SendMessageEvent(AutodiscordEventBase):
    event_name: str = "SEND_MESSAGE"
    channel_id: str | None = None
    content: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "channel_id": data.get("channel_id"),
            "content": data.get("content"),
        }


class AddReactionEvent(AutodiscordEventBase):
    event_name: str = "ADD_REACTION"
    message_id: str | None = None
    emoji: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "message_id": data.get("message_id"),
            "emoji": data.get("emoji"),
        }


class SelectDmEvent(AutodiscordEventBase):
    event_name: str = "SELECT_DM"
    peer_id: str | None = None
    peer_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "peer_id": data.get("peer_id"),
            "peer_name": data.get("peer_name"),
        }


class SendDmMessageEvent(AutodiscordEventBase):
    event_name: str = "SEND_DM_MESSAGE"
    peer_id: str | None = None
    content: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "peer_id": data.get("peer_id"),
            "content": data.get("content"),
        }


class OpenSettingsEvent(AutodiscordEventBase):
    event_name: str = "OPEN_SETTINGS"


class SettingsAppearanceEvent(AutodiscordEventBase):
    event_name: str = "SETTINGS_APPEARANCE"
    theme: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {"theme": data.get("theme")}


class SettingsNotificationsEvent(AutodiscordEventBase):
    event_name: str = "SETTINGS_NOTIFICATIONS"
    enabled: bool | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {"enabled": data.get("enabled")}


class SettingsAccountEvent(AutodiscordEventBase):
    event_name: str = "SETTINGS_ACCOUNT"
    display_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {"display_name": data.get("display_name")}


class CreateServerEvent(AutodiscordEventBase):
    event_name: str = "CREATE_SERVER"
    server_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {"server_name": data.get("server_name")}


class OpenServerSettingsEvent(AutodiscordEventBase):
    event_name: str = "OPEN_SERVER_SETTINGS"
    server_id: str | None = None
    server_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "server_id": data.get("server_id"),
            "server_name": data.get("server_name"),
        }


class DeleteServerEvent(AutodiscordEventBase):
    event_name: str = "DELETE_SERVER"
    server_id: str | None = None
    server_name: str | None = None

    @classmethod
    def _payload_from_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "server_id": data.get("server_id"),
            "server_name": data.get("server_name"),
        }


EVENTS: list[type[Event]] = [
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
]

BACKEND_EVENT_TYPES: dict[str, type[Event]] = {
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
}
