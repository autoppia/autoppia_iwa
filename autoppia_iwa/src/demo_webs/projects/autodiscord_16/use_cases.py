"""Use cases for web_16_autodiscord (AutoDiscord).

Aligned with USE_CASES.md and iwa-module/use_cases.json in the demo-webs repo.
Each use case has a name, description, event type, and example prompts for task generation.
"""

from typing import Type

from autoppia_iwa.src.demo_webs.classes import UseCase
from autoppia_iwa.src.demo_webs.projects.base_events import Event

from .events import (
    AddReactionEvent,
    CreateServerEvent,
    DeleteServerEvent,
    OpenServerSettingsEvent,
    OpenSettingsEvent,
    SelectChannelEvent,
    SelectDmEvent,
    SelectServerEvent,
    SendDmMessageEvent,
    SendMessageEvent,
    SettingsAccountEvent,
    SettingsAppearanceEvent,
    SettingsNotificationsEvent,
    ViewDmsEvent,
    ViewServersEvent,
)


def _make_use_case(
    name: str,
    description: str,
    event_class: Type[Event],
    *example_prompts: str,
) -> UseCase:
    if not example_prompts:
        raise ValueError(f"Use case {name} must have at least one example prompt")
    examples = [
        {"prompt": p, "prompt_for_task_generation": p}
        for p in example_prompts
    ]
    return UseCase(
        name=name,
        description=description,
        event=event_class,
        event_source_code=event_class.get_source_code_of_class(),
        constraints_generator=False,
        constraints=[],
        examples=examples,
    )


UC1_SEND_MESSAGE = _make_use_case(
    "SEND_MESSAGE_IN_CHANNEL",
    "The user sends a message in a channel (select server, select channel, type and submit).",
    SendMessageEvent,
    "Send a message in the #general channel.",
    "Post 'Hello everyone' in the selected text channel.",
)

UC2_ADD_REACTION = _make_use_case(
    "ADD_REACTION",
    "The user adds a reaction (e.g. thumbs up) to a message.",
    AddReactionEvent,
    "Add a thumbs-up reaction to a message in the channel.",
    "React to the latest message with a thumbs up.",
)

UC3_OPEN_DMS_SEND_MESSAGE = _make_use_case(
    "OPEN_DMS_AND_SEND_MESSAGE",
    "The user opens DMs, selects a user, and sends a message.",
    SendDmMessageEvent,
    "Open Direct Messages, select a user, and send them a message.",
    "Send a DM to a user from the server list.",
)

UC4_CHANGE_SETTINGS = _make_use_case(
    "CHANGE_SETTINGS",
    "The user opens Settings and changes Appearance, Notifications, and/or Account (display name).",
    SettingsAccountEvent,
    "Open Settings, change theme to Light, toggle notifications, and save a new display name.",
    "Change appearance to dark and update your display name in Account.",
)

UC5_CREATE_SERVER = _make_use_case(
    "CREATE_SERVER",
    "The user creates a new server via the Add server button.",
    CreateServerEvent,
    "Click Add server and create a server named 'Test Server'.",
    "Create a new server with the green plus button.",
)

UC6_OPEN_SERVER_SETTINGS = _make_use_case(
    "OPEN_SERVER_SETTINGS",
    "The user opens server settings (gear next to server name).",
    OpenServerSettingsEvent,
    "Select a server and click the gear icon next to the server name to open Server settings.",
    "Open the settings for the current server.",
)

UC7_DELETE_SERVER = _make_use_case(
    "DELETE_SERVER",
    "The user deletes a locally created server via Server settings.",
    DeleteServerEvent,
    "Create a server, then open Server settings and delete it.",
    "Delete a server you created from Server settings.",
)

UC8_SWITCH_SERVERS_CHANNELS = _make_use_case(
    "SWITCH_SERVERS_AND_CHANNELS",
    "The user switches between servers and channels (Home, server A, channel, server B, channel).",
    SelectChannelEvent,
    "Click Home, select server A and a channel, then select server B and a different channel.",
    "Switch between two servers and select a channel in each.",
)

UC9_RETURN_TO_SERVERS_FROM_DMS = _make_use_case(
    "RETURN_TO_SERVERS_FROM_DMS",
    "The user opens DMs then returns to the server list via Home.",
    ViewServersEvent,
    "Click Direct Messages, then click Home to return to the server list.",
    "Go to DMs and then back to servers.",
)

UC10_FULL_CHANNEL_CONVERSATION = _make_use_case(
    "FULL_CHANNEL_CONVERSATION",
    "The user sends multiple messages and adds reactions in a channel.",
    AddReactionEvent,
    "In a channel, send two messages and add reactions to at least two messages.",
    "Send several messages and react to them with thumbs up.",
)

UC11_CREATE_SERVER_OPEN_SETTINGS = _make_use_case(
    "CREATE_SERVER_THEN_OPEN_SETTINGS",
    "The user creates a server then opens its Server settings.",
    OpenServerSettingsEvent,
    "Create a server named 'Test Server', then open the gear next to its name to open Server settings.",
    "Add a new server and open its settings.",
)

UC12_OPEN_SETTINGS_ONE_OPTION = _make_use_case(
    "OPEN_SETTINGS_ONE_OPTION",
    "The user opens Settings and changes one option (Appearance or Notifications) then goes back.",
    SettingsAppearanceEvent,
    "Open Settings, change Appearance to Light, then click Back.",
    "Go to Settings and switch to Light theme.",
)

UC13_SWITCH_DM_CONVERSATIONS = _make_use_case(
    "SWITCH_DM_CONVERSATIONS",
    "The user switches between two DM conversations.",
    SelectDmEvent,
    "Open DMs, select user A, then select user B.",
    "Switch between two different DM conversations.",
)

UC14_CREATE_SERVER_DELETE = _make_use_case(
    "CREATE_SERVER_THEN_DELETE",
    "The user creates a server then deletes it via Server settings.",
    DeleteServerEvent,
    "Create a server, open Server settings, and delete the server.",
    "Create a server and then delete it.",
)

UC15_VIEW_EMPTY_SERVER = _make_use_case(
    "VIEW_EMPTY_SERVER",
    "The user creates a server (no channels) and views the empty state.",
    SelectServerEvent,
    "Create a server and leave it selected to see 'No channels in this server'.",
    "View the main area after creating a new server with no channels.",
)

UC16_E2E_SERVER_LIFECYCLE = _make_use_case(
    "E2E_SERVER_LIFECYCLE",
    "End-to-end: Home, create server, open Server settings, delete server.",
    DeleteServerEvent,
    "Click Home, create a server named 'E2E Test', open its settings, and delete it.",
    "Complete the full server lifecycle: create then delete a server.",
)

ALL_USE_CASES: list[UseCase] = [
    UC1_SEND_MESSAGE,
    UC2_ADD_REACTION,
    UC3_OPEN_DMS_SEND_MESSAGE,
    UC4_CHANGE_SETTINGS,
    UC5_CREATE_SERVER,
    UC6_OPEN_SERVER_SETTINGS,
    UC7_DELETE_SERVER,
    UC8_SWITCH_SERVERS_CHANNELS,
    UC9_RETURN_TO_SERVERS_FROM_DMS,
    UC10_FULL_CHANNEL_CONVERSATION,
    UC11_CREATE_SERVER_OPEN_SETTINGS,
    UC12_OPEN_SETTINGS_ONE_OPTION,
    UC13_SWITCH_DM_CONVERSATIONS,
    UC14_CREATE_SERVER_DELETE,
    UC15_VIEW_EMPTY_SERVER,
    UC16_E2E_SERVER_LIFECYCLE,
]
