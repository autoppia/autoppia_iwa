# -----------------------------------------------------------------------------
# use_cases.py — AutoDiscord (web_16_autodiscord)
# -----------------------------------------------------------------------------
from autoppia_iwa.src.demo_webs.classes import UseCase

from .events import (
    AddReactionEvent,
    CreateChannelEvent,
    CreateServerEvent,
    DeleteServerEvent,
    JoinVoiceChannelEvent,
    LeaveVoiceChannelEvent,
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
    VoiceMuteToggleEvent,
)
from .generation_functions import (
    generate_add_reaction_constraints,
    generate_create_channel_constraints,
    generate_create_server_constraints,
    generate_delete_server_constraints,
    generate_join_voice_channel_constraints,
    generate_leave_voice_channel_constraints,
    generate_open_server_settings_constraints,
    generate_select_channel_constraints,
    generate_select_dm_constraints,
    generate_select_server_constraints,
    generate_send_dm_message_constraints,
    generate_send_message_constraints,
    generate_settings_account_constraints,
    generate_settings_appearance_constraints,
    generate_settings_notifications_constraints,
    generate_voice_mute_toggle_constraints,
)

# No payload — constraints_generator=False
VIEW_SERVERS_USE_CASE = UseCase(
    name="VIEW_SERVERS",
    description="The user clicks the Home (servers) icon to view the server list.",
    event=ViewServersEvent,
    event_source_code=ViewServersEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Click the Home icon to view servers.", "prompt_for_task_generation": "Click the Home icon to view servers."},
    ],
)

VIEW_DMS_USE_CASE = UseCase(
    name="VIEW_DMS",
    description="The user clicks the Direct Messages icon.",
    event=ViewDmsEvent,
    event_source_code=ViewDmsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Open Direct Messages.", "prompt_for_task_generation": "Open Direct Messages."},
    ],
)

OPEN_SETTINGS_USE_CASE = UseCase(
    name="OPEN_SETTINGS",
    description="The user opens the Settings page.",
    event=OpenSettingsEvent,
    event_source_code=OpenSettingsEvent.get_source_code_of_class(),
    constraints_generator=False,
    examples=[
        {"prompt": "Open Settings.", "prompt_for_task_generation": "Open Settings."},
    ],
)

SELECT_SERVER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Select the server...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

# With payload — use constraints_generator
SELECT_SERVER_USE_CASE = UseCase(
    name="SELECT_SERVER",
    description="The user selects a server from the server list.",
    event=SelectServerEvent,
    event_source_code=SelectServerEvent.get_source_code_of_class(),
    constraints_generator=generate_select_server_constraints,
    additional_prompt_info=SELECT_SERVER_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Select the server where server_name equals 'Dev Squad'.", "prompt_for_task_generation": "Select the server where server_name equals 'Dev Squad'."},
        {"prompt": "Select the server where server_name equals 'Gaming Zone'.", "prompt_for_task_generation": "Select the server where server_name equals 'Gaming Zone'."},
        {"prompt": "Select the server where server_name contains 'Dev'.", "prompt_for_task_generation": "Select the server where server_name contains 'Dev'."},
        {"prompt": "Select the server where server_name not_equals 'Design Hub'.", "prompt_for_task_generation": "Select the server where server_name not_equals 'Design Hub'."},
        {"prompt": "Select the server where server_name not_contains 'Zone'.", "prompt_for_task_generation": "Select the server where server_name not_contains 'Zone'."},
    ],
)

SELECT_CHANNEL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Select the channel...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SELECT_CHANNEL_USE_CASE = UseCase(
    name="SELECT_CHANNEL",
    description="The user selects a channel in the channel list.",
    event=SelectChannelEvent,
    event_source_code=SelectChannelEvent.get_source_code_of_class(),
    constraints_generator=generate_select_channel_constraints,
    additional_prompt_info=SELECT_CHANNEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Select the channel where channel_name equals 'general' and server_name equals 'Dev Squad'.",
            "prompt_for_task_generation": "Select the channel where channel_name equals 'general' and server_name equals 'Dev Squad'.",
        },
        {"prompt": "Select the channel where channel_name equals 'random'.", "prompt_for_task_generation": "Select the channel where channel_name equals 'random'."},
        {"prompt": "Select the channel where channel_name contains 'gen'.", "prompt_for_task_generation": "Select the channel where channel_name contains 'gen'."},
        {"prompt": "Select the channel where channel_name not_equals 'random'.", "prompt_for_task_generation": "Select the channel where channel_name not_equals 'random'."},
        {"prompt": "Select the channel where server_name not_equals 'Design Hub'.", "prompt_for_task_generation": "Select the channel where server_name not_equals 'Design Hub'."},
    ],
)

SEND_MESSAGE_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Send a message...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SEND_MESSAGE_USE_CASE = UseCase(
    name="SEND_MESSAGE",
    description="The user sends a message in a channel.",
    event=SendMessageEvent,
    event_source_code=SendMessageEvent.get_source_code_of_class(),
    constraints_generator=generate_send_message_constraints,
    additional_prompt_info=SEND_MESSAGE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send a message in the channel where channel_name equals 'general' and server_name equals 'Dev Squad' with content that contains 'Hello'.",
            "prompt_for_task_generation": "Send a message in the channel where channel_name equals 'general' and server_name equals 'Dev Squad' with content that contains 'Hello'.",
        },
        {
            "prompt": "Send a message where channel_name equals 'dev-help' and content equals 'Need help with the API'.",
            "prompt_for_task_generation": "Send a message where channel_name equals 'dev-help' and content equals 'Need help with the API'.",
        },
        {
            "prompt": "Send a message where channel_name not_contains 'voice' and content contains 'help'.",
            "prompt_for_task_generation": "Send a message where channel_name not_contains 'voice' and content contains 'help'.",
        },
        {"prompt": "Send a message where content not_equals 'spam'.", "prompt_for_task_generation": "Send a message where content not_equals 'spam'."},
    ],
)

ADD_REACTION_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Add a reaction...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

ADD_REACTION_USE_CASE = UseCase(
    name="ADD_REACTION",
    description="The user adds a reaction to a message.",
    event=AddReactionEvent,
    event_source_code=AddReactionEvent.get_source_code_of_class(),
    constraints_generator=generate_add_reaction_constraints,
    additional_prompt_info=ADD_REACTION_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Add a reaction where channel_name equals 'general' and server_name equals 'Dev Squad' and content that contains 'Hello'.",
            "prompt_for_task_generation": "Add a reaction where channel_name equals 'general' and server_name equals 'Dev Squad' and content that contains 'Hello'.",
        },
        {"prompt": "Add a reaction where channel_name equals 'general'.", "prompt_for_task_generation": "Add a reaction where channel_name equals 'general'."},
        {"prompt": "Add a reaction where channel_name not_equals 'random'.", "prompt_for_task_generation": "Add a reaction where channel_name not_equals 'random'."},
    ],
)

ADD_REACTION_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Add a reaction...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SELECT_DM_USE_CASE = UseCase(
    name="SELECT_DM",
    description="The user selects a DM conversation.",
    event=SelectDmEvent,
    event_source_code=SelectDmEvent.get_source_code_of_class(),
    constraints_generator=generate_select_dm_constraints,
    examples=[
        {"prompt": "Open the DM where name equals 'Alex'.", "prompt_for_task_generation": "Open the DM where name equals 'Alex'."},
        {"prompt": "Select the DM where name equals 'Jordan'.", "prompt_for_task_generation": "Select the DM where name equals 'Jordan'."},
        {"prompt": "Select the DM where name contains 'lex'.", "prompt_for_task_generation": "Select the DM where name contains 'lex'."},
        {"prompt": "Select the DM where name not_equals 'Casey'.", "prompt_for_task_generation": "Select the DM where name not_equals 'Casey'."},
        {"prompt": "Select the DM where name not_equals 'Guest'.", "prompt_for_task_generation": "Select the DM where name not_equals 'Guest'."},
    ],
)

SEND_DM_MESSAGE_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Send a DM..." or "Send a direct message...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SEND_DM_MESSAGE_USE_CASE = UseCase(
    name="SEND_DM_MESSAGE",
    description="The user sends a message in a direct message conversation.",
    event=SendDmMessageEvent,
    event_source_code=SendDmMessageEvent.get_source_code_of_class(),
    constraints_generator=generate_send_dm_message_constraints,
    additional_prompt_info=SEND_DM_MESSAGE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Send a DM where name equals 'Jordan' and content contains 'Hey'.",
            "prompt_for_task_generation": "Send a DM where name equals 'Jordan' and content contains 'Hey'.",
        },
        {"prompt": "Send a direct message to the peer where name equals 'Sam'.", "prompt_for_task_generation": "Send a direct message to the peer where name equals 'Sam'."},
        {
            "prompt": "Send a DM where name contains 'Case' and content not_contains 'secret'.",
            "prompt_for_task_generation": "Send a DM where name contains 'Case' and content not_contains 'secret'.",
        },
        {"prompt": "Send a DM where name not_equals 'Guest'.", "prompt_for_task_generation": "Send a DM where name not_equals 'Guest'."},
    ],
)

SETTINGS_APPEARANCE_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "In Settings...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SETTINGS_APPEARANCE_USE_CASE = UseCase(
    name="SETTINGS_APPEARANCE",
    description="The user changes the theme (Dark/Light) in Settings.",
    event=SettingsAppearanceEvent,
    event_source_code=SettingsAppearanceEvent.get_source_code_of_class(),
    constraints_generator=generate_settings_appearance_constraints,
    additional_prompt_info=SETTINGS_APPEARANCE_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "In Settings, set theme equals 'light'.", "prompt_for_task_generation": "In Settings, set theme equals 'light'."},
        {"prompt": "In Settings, set theme equals 'dark'.", "prompt_for_task_generation": "In Settings, set theme equals 'dark'."},
        {"prompt": "In Settings, set theme not_equals 'dark'.", "prompt_for_task_generation": "In Settings, set theme not_equals 'dark'."},
        {"prompt": "In Settings, set theme contains 'lig'.", "prompt_for_task_generation": "In Settings, set theme contains 'lig'."},
    ],
)

SETTINGS_NOTIFICATIONS_USE_CASE = UseCase(
    name="SETTINGS_NOTIFICATIONS",
    description="The user toggles notifications in Settings.",
    event=SettingsNotificationsEvent,
    event_source_code=SettingsNotificationsEvent.get_source_code_of_class(),
    constraints_generator=generate_settings_notifications_constraints,
    examples=[
        {"prompt": "In Settings, set notifications so that enabled equals true.", "prompt_for_task_generation": "In Settings, set notifications so that enabled equals true."},
        {"prompt": "Toggle notifications so that enabled equals false.", "prompt_for_task_generation": "Toggle notifications so that enabled equals false."},
        {"prompt": "In Settings, set enabled not_equals false.", "prompt_for_task_generation": "In Settings, set enabled not_equals false."},
        {"prompt": "Turn on notifications in Settings (enabled equals true).", "prompt_for_task_generation": "Turn on notifications in Settings (enabled equals true)."},
        {"prompt": "Turn off notifications (enabled equals false).", "prompt_for_task_generation": "Turn off notifications (enabled equals false)."},
    ],
)

SETTINGS_ACCOUNT_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "In setting...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

SETTINGS_ACCOUNT_USE_CASE = UseCase(
    name="SETTINGS_ACCOUNT",
    description="The user saves their display name in Settings.",
    event=SettingsAccountEvent,
    event_source_code=SettingsAccountEvent.get_source_code_of_class(),
    constraints_generator=generate_settings_account_constraints,
    additional_prompt_info=SETTINGS_ACCOUNT_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "In Settings, set name equals 'Test User'.", "prompt_for_task_generation": "In Settings, set name equals 'Test User'."},
        {"prompt": "In Settings, set name equals 'Alex'.", "prompt_for_task_generation": "In Settings, set name equals 'Alex'."},
        {"prompt": "In Settings, set name contains 'Test'.", "prompt_for_task_generation": "In Settings, set name contains 'Test'."},
        {"prompt": "In Settings, set name not_equals 'Guest'.", "prompt_for_task_generation": "In Settings, set name not_equals 'Guest'."},
    ],
)

CREATE_SERVER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Create a server...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

CREATE_SERVER_USE_CASE = UseCase(
    name="CREATE_SERVER",
    description="The user creates a new server.",
    event=CreateServerEvent,
    event_source_code=CreateServerEvent.get_source_code_of_class(),
    constraints_generator=generate_create_server_constraints,
    additional_prompt_info=CREATE_SERVER_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Create a server where server_name equals 'Test Server'.", "prompt_for_task_generation": "Create a server where server_name equals 'Test Server'."},
        {"prompt": "Create a server where server_name equals 'My Server'.", "prompt_for_task_generation": "Create a server where server_name equals 'My Server'."},
        {"prompt": "Create a server where server_name contains 'Server'.", "prompt_for_task_generation": "Create a server where server_name contains 'Server'."},
        {"prompt": "Create a server where server_name not_equals 'Old Name'.", "prompt_for_task_generation": "Create a server where server_name not_equals 'Old Name'."},
    ],
)

OPEN_SERVER_SETTINGS_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Open server settings...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

OPEN_SERVER_SETTINGS_USE_CASE = UseCase(
    name="OPEN_SERVER_SETTINGS",
    description="The user opens server settings (gear next to server name).",
    event=OpenServerSettingsEvent,
    event_source_code=OpenServerSettingsEvent.get_source_code_of_class(),
    constraints_generator=generate_open_server_settings_constraints,
    additional_prompt_info=OPEN_SERVER_SETTINGS_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Open server settings where server_name equals 'Dev Squad'.", "prompt_for_task_generation": "Open server settings where server_name equals 'Dev Squad'."},
        {"prompt": "Open server settings where server_name equals 'Dev Squad'.", "prompt_for_task_generation": "Open server settings where server_name equals 'Dev Squad'."},
        {"prompt": "Open server settings where server_name contains 'Squad'.", "prompt_for_task_generation": "Open server settings where server_name contains 'Squad'."},
        {"prompt": "Open server settings where server_name not_equals 'Design Hub'.", "prompt_for_task_generation": "Open server settings where server_name not_equals 'Design Hub'."},
    ],
)

DELETE_SERVER_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Delete the server...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

DELETE_SERVER_USE_CASE = UseCase(
    name="DELETE_SERVER",
    description="The user deletes a server from server settings.",
    event=DeleteServerEvent,
    event_source_code=DeleteServerEvent.get_source_code_of_class(),
    constraints_generator=generate_delete_server_constraints,
    additional_prompt_info=DELETE_SERVER_ADDITIONAL_PROMPT_INFO,
    examples=[
        {"prompt": "Delete the server where server_name equals 'Dev Squad' from settings.", "prompt_for_task_generation": "Delete the server where server_name equals 'Dev Squad' from settings."},
        {"prompt": "Delete the server where server_name equals 'Design Hub' from settings.", "prompt_for_task_generation": "Delete the server where server_name equals 'Design Hub' from settings."},
        {"prompt": "Delete the server where server_name not_contains 'Hub' from settings.", "prompt_for_task_generation": "Delete the server where server_name not_contains 'Hub' from settings."},
        {
            "prompt": "Delete the server where server_name not_equals 'Dev Squad' from settings.",
            "prompt_for_task_generation": "Delete the server where server_name not_equals 'Dev Squad' from settings.",
        },
    ],
)

CREATE_CHANNEL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Create a channel...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

CREATE_CHANNEL_USE_CASE = UseCase(
    name="CREATE_CHANNEL",
    description="The user creates a new channel in a server.",
    event=CreateChannelEvent,
    event_source_code=CreateChannelEvent.get_source_code_of_class(),
    constraints_generator=generate_create_channel_constraints,
    additional_prompt_info=CREATE_CHANNEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Create a channel where server_name equals 'Dev Squad' and channel_name equals 'announcements'.",
            "prompt_for_task_generation": "Create a channel where server_name equals 'Dev Squad' and channel_name equals 'announcements'.",
        },
        {
            "prompt": "Create a channel where server_name equals 'Dev Squad' and channel_name equals 'general'.",
            "prompt_for_task_generation": "Create a channel where server_name equals 'Dev Squad' and channel_name equals 'general'.",
        },
        {
            "prompt": "Create a channel where channel_name contains 'announce' and server_name not_equals 'Design Hub'.",
            "prompt_for_task_generation": "Create a channel where channel_name contains 'announce' and server_name not_equals 'Design Hub'.",
        },
        {"prompt": "Create a channel where channel_name not_contains 'voice'.", "prompt_for_task_generation": "Create a channel where channel_name not_contains 'voice'."},
    ],
)

JOIN_VOICE_CHANNEL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Join the voice channel...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

JOIN_VOICE_CHANNEL_USE_CASE = UseCase(
    name="JOIN_VOICE_CHANNEL",
    description="The user joins a voice channel.",
    event=JoinVoiceChannelEvent,
    event_source_code=JoinVoiceChannelEvent.get_source_code_of_class(),
    constraints_generator=generate_join_voice_channel_constraints,
    additional_prompt_info=JOIN_VOICE_CHANNEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Join the voice channel where channel_name equals 'voice-chat' and server_name equals 'Dev Squad'.",
            "prompt_for_task_generation": "Join the voice channel where channel_name equals 'voice-chat' and server_name equals 'Dev Squad'.",
        },
        {"prompt": "Join the voice channel where channel_name equals 'voice-chat'.", "prompt_for_task_generation": "Join the voice channel where channel_name equals 'voice-chat'."},
        {
            "prompt": "Join the voice channel where channel_name contains 'voice' and server_name not_equals 'Design Hub'.",
            "prompt_for_task_generation": "Join the voice channel where channel_name contains 'voice' and server_name not_equals 'Design Hub'.",
        },
    ],
)

LEAVE_VOICE_CHANNEL_ADDITIONAL_PROMPT_INFO = """
Critical requirements:
1. The request must start with: "Leave the voice channel...".
2. Do not mention a single constraint more than once in the request.
3. Do not add additional information in the prompt that is not mentioned in the constraints.
""".strip()

LEAVE_VOICE_CHANNEL_USE_CASE = UseCase(
    name="LEAVE_VOICE_CHANNEL",
    description="The user leaves the current voice channel.",
    event=LeaveVoiceChannelEvent,
    event_source_code=LeaveVoiceChannelEvent.get_source_code_of_class(),
    constraints_generator=generate_leave_voice_channel_constraints,
    additional_prompt_info=LEAVE_VOICE_CHANNEL_ADDITIONAL_PROMPT_INFO,
    examples=[
        {
            "prompt": "Leave the voice channel where channel_name equals 'voice-chat' and server_name equals 'Dev Squad'.",
            "prompt_for_task_generation": "Leave the voice channel where channel_name equals 'voice-chat' and server_name equals 'Dev Squad'.",
        },
        {"prompt": "Leave the voice channel where channel_name equals 'general'.", "prompt_for_task_generation": "Leave the voice channel where channel_name equals 'general'."},
        {"prompt": "Leave the voice channel where channel_name not_equals 'general'.", "prompt_for_task_generation": "Leave the voice channel where channel_name not_equals 'general'."},
        {"prompt": "Leave the voice channel where channel_name contains 'voice'.", "prompt_for_task_generation": "Leave the voice channel where channel_name contains 'voice'."},
    ],
)

VOICE_MUTE_TOGGLE_USE_CASE = UseCase(
    name="VOICE_MUTE_TOGGLE",
    description="The user toggles mute in the voice channel.",
    event=VoiceMuteToggleEvent,
    event_source_code=VoiceMuteToggleEvent.get_source_code_of_class(),
    constraints_generator=generate_voice_mute_toggle_constraints,
    examples=[
        {
            "prompt": "In the voice channel where channel_name equals 'voice-chat', and server_name equals 'Dev Squad' and set muted equals true.",
            "prompt_for_task_generation": "In the voice channel where channel_name equals 'voice-chat', and server_name equals 'Dev Squad' and set muted equals true.",
        },
        {"prompt": "Toggle mute so that muted equals false in the current voice channel.", "prompt_for_task_generation": "Toggle mute so that muted equals false in the current voice channel."},
        {"prompt": "In the voice channel, set muted not_equals true.", "prompt_for_task_generation": "In the voice channel, set muted not_equals true."},
        {
            "prompt": "In the voice channel where channel_name contains 'voice', set muted equals false.",
            "prompt_for_task_generation": "In the voice channel where channel_name contains 'voice', set muted equals false.",
        },
    ],
)

ALL_USE_CASES = [
    VIEW_SERVERS_USE_CASE,
    VIEW_DMS_USE_CASE,
    SELECT_SERVER_USE_CASE,
    SELECT_CHANNEL_USE_CASE,
    SEND_MESSAGE_USE_CASE,
    ADD_REACTION_USE_CASE,
    SELECT_DM_USE_CASE,
    SEND_DM_MESSAGE_USE_CASE,
    OPEN_SETTINGS_USE_CASE,
    SETTINGS_APPEARANCE_USE_CASE,
    SETTINGS_NOTIFICATIONS_USE_CASE,
    SETTINGS_ACCOUNT_USE_CASE,
    CREATE_SERVER_USE_CASE,
    OPEN_SERVER_SETTINGS_USE_CASE,
    DELETE_SERVER_USE_CASE,
    CREATE_CHANNEL_USE_CASE,
    JOIN_VOICE_CHANNEL_USE_CASE,
    LEAVE_VOICE_CHANNEL_USE_CASE,
    VOICE_MUTE_TOGGLE_USE_CASE,
]
