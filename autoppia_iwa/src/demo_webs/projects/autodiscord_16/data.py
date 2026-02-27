# AutoDiscord (Web 16) — field/operator maps for constraint generation

from ..operators import CONTAINS, EQUALS, NOT_CONTAINS, NOT_EQUALS

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]

# Server selection / create / delete / settings
FIELD_OPERATORS_MAP_SERVER = {
    "server_name": STRING_OPERATORS,
}

# Channel selection / create / voice
FIELD_OPERATORS_MAP_CHANNEL = {
    "channel_name": STRING_OPERATORS,
    "server_name": STRING_OPERATORS,
}

# Send message (channel)
FIELD_OPERATORS_MAP_SEND_MESSAGE = {
    "channel_name": STRING_OPERATORS,
    "content": STRING_OPERATORS,
    "server_name": STRING_OPERATORS,
}

# Add reaction
FIELD_OPERATORS_MAP_ADD_REACTION = {
    "message_id": STRING_OPERATORS,
    "channel_name": STRING_OPERATORS,
    "server_name": STRING_OPERATORS,
    "content": STRING_OPERATORS,
}

# DM selection / send DM (event payload uses "name" for peer/display)
FIELD_OPERATORS_MAP_DM = {
    "name": STRING_OPERATORS,
    "content": STRING_OPERATORS,
}

# Settings
FIELD_OPERATORS_MAP_SETTINGS_APPEARANCE = {"theme": STRING_OPERATORS}
FIELD_OPERATORS_MAP_SETTINGS_ACCOUNT = {"name": STRING_OPERATORS}
# Settings notifications (enabled is bool — equality only)
FIELD_OPERATORS_MAP_SETTINGS_NOTIFICATIONS = {"enabled": [EQUALS, NOT_EQUALS]}

# Create server (only server_name)
FIELD_OPERATORS_MAP_CREATE_SERVER = {"server_name": STRING_OPERATORS}

# Create channel
FIELD_OPERATORS_MAP_CREATE_CHANNEL = {
    "server_name": STRING_OPERATORS,
    "channel_name": STRING_OPERATORS,
    "channel_type": [EQUALS, NOT_EQUALS],
}

# Voice mute (muted is bool — equality only)
FIELD_OPERATORS_MAP_VOICE_MUTE = {
    "channel_name": STRING_OPERATORS,
    "server_name": STRING_OPERATORS,
    "muted": [EQUALS, NOT_EQUALS],
}
