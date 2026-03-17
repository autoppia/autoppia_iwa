import asyncio
import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_MAP_ADD_REACTION,
    FIELD_OPERATORS_MAP_CHANNEL,
    FIELD_OPERATORS_MAP_CREATE_CHANNEL,
    FIELD_OPERATORS_MAP_CREATE_SERVER,
    FIELD_OPERATORS_MAP_DM,
    FIELD_OPERATORS_MAP_SEND_MESSAGE,
    FIELD_OPERATORS_MAP_SERVER,
    FIELD_OPERATORS_MAP_SETTINGS_ACCOUNT,
    FIELD_OPERATORS_MAP_SETTINGS_NOTIFICATIONS,
    FIELD_OPERATORS_MAP_VOICE_MUTE,
)


async def _ensure_discord_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
    method: str | None = None,
    filter_key: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Load entity data from pre-loaded dataset or fetch from backend."""
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    from .data_utils import fetch_data

    seed = get_seed_from_url(task_url)
    fetched = await fetch_data(
        entity_type=entity_type,
        method=method,
        filter_key=filter_key,
        seed_value=seed,
    )
    return {entity_type: fetched}


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    if operator == ComparisonOperator.EQUALS:
        return field_value
    if operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) != field_value and v.get(field) is not None]
        return random.choice(valid) if valid else field_value
    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str) and len(field_value) > 2:
        start = random.randint(0, max(0, len(field_value) - 2))
        end = random.randint(start + 1, len(field_value))
        return field_value[start:end]
    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        return random.choice(valid) if valid else None
    return field_value


async def generate_select_server_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        channels_dict, servers_dict = await asyncio.gather(
            _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
            _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
        )
        channels = channels_dict.get("channels", [])
        servers = servers_dict.get("servers", [])
        if not channels or not servers:
            return []
        sample_channel = random.choice(channels)
        resolved_server = next(
            (s for s in servers if s.get("id") == sample_channel.get("serverId")),
            None,
        )
        channel_name = sample_channel.get("name", "")
        server_name = resolved_server.get("name", "") if resolved_server else ""
        if not server_name or not channel_name:
            return []
        return {
            "constraints": [create_constraint_dict("server_name", ComparisonOperator.EQUALS, server_name)],
            "question_fields_and_values": {"channel_name": channel_name},
        }

    data_dict = await _ensure_discord_dataset(task_url, dataset, entity_type="servers")
    servers = data_dict.get("servers", [])
    if not servers:
        return []
    sample = random.choice(servers)
    constraints = []
    for field, data_key in [("server_name", "name")]:
        allowed = FIELD_OPERATORS_MAP_SERVER.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, servers)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_select_channel_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    channels_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    channels = channels_dict.get("channels", [])
    servers = servers_dict.get("servers", [])
    if not channels:
        return []

    sample_channel = random.choice(channels)
    resolved_server = next(
        (s for s in servers if s.get("id") == sample_channel.get("serverId")),
        None,
    )
    channel_name = sample_channel.get("name", "")
    server_name = resolved_server.get("name", "") if resolved_server else ""

    if test_types == "data_extraction_only":
        verify_field = random.choice(["channel_name", "server_name"])
        verify_value = channel_name if verify_field == "channel_name" else server_name
        if not verify_value:
            return []
        # Only the non-verify field goes into question_fields_and_values (entity identifier).
        other_field = "server_name" if verify_field == "channel_name" else "channel_name"
        other_value = server_name if verify_field == "channel_name" else channel_name
        if not other_value:
            return []
        return {
            "constraints": [create_constraint_dict(verify_field, ComparisonOperator.EQUALS, verify_value)],
            "question_fields_and_values": {other_field: other_value},
        }

    constraints: list[dict[str, Any]] = []
    for field, data_key, sample, entity_list in [
        ("channel_name", "name", sample_channel, channels),
        ("server_name", "name", resolved_server, servers),
    ]:
        if sample is None or not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_CHANNEL.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_send_message_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    channels_dict, messages_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="messages"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    channels = channels_dict.get("channels", [])
    messages = messages_dict.get("messages", [])
    servers = servers_dict.get("servers", [])
    if not channels:
        return constraints
    sample_channel = random.choice(channels)
    resolved_server = (
        next(
            (s for s in servers if s.get("id") == sample_channel.get("serverId")),
            None,
        )
        if servers
        else None
    )
    sample_content = random.choice(messages).get("content", "") if messages else random.choice(["Hello", "Need help", "Thanks"])
    content_list = [{"content": m.get("content", "")} for m in messages] if messages else [{"content": sample_content}]
    for field, data_key, sample_entity, entity_list in [
        ("channel_name", "name", sample_channel, channels),
        ("content", "content", {"content": sample_content}, content_list),
        ("server_name", "name", resolved_server, servers),
    ]:
        if sample_entity is None or not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_SEND_MESSAGE.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample_entity.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_add_reaction_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    constraints: list[dict[str, Any]] = []
    messages_dict, channels_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="messages"),
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    messages = messages_dict.get("messages", [])
    channels = channels_dict.get("channels", [])
    servers = servers_dict.get("servers", [])
    if not messages:
        return [] if test_types == "data_extraction_only" else constraints

    sample = random.choice(messages)
    chan_id = sample.get("channelId")
    resolved_channel = next((c for c in channels if c.get("id") == chan_id), None) if chan_id and channels else (random.choice(channels) if channels else None)
    if resolved_channel is None and channels:
        resolved_channel = random.choice(channels)
    resolved_server = (
        next(
            (s for s in servers if s.get("id") == resolved_channel.get("serverId")),
            None,
        )
        if resolved_channel and servers
        else None
    )

    sample_content = sample.get("content", "")
    channel_name = resolved_channel.get("name", "") if resolved_channel else ""
    server_name = resolved_server.get("name", "") if resolved_server else ""

    if test_types == "data_extraction_only":
        # Pick verify field from content and authorUsername; unpicked field goes in question
        verify_field = random.choice(["content", "authorUsername"])
        verify_value = sample.get(verify_field, "")
        if not verify_value:
            return []

        # Question fields: server_name, channel_name, and the unpicked field
        question_fields_and_values: dict[str, Any] = {}
        if server_name:
            question_fields_and_values["server_name"] = server_name
        if channel_name:
            question_fields_and_values["channel_name"] = channel_name
        unpicked = "authorUsername" if verify_field == "content" else "content"
        unpicked_value = sample.get(unpicked, "")
        if unpicked_value:
            question_fields_and_values[unpicked] = unpicked_value

        if not question_fields_and_values:
            return []

        return {
            "constraints": [create_constraint_dict(verify_field, ComparisonOperator.EQUALS, verify_value)],
            "question_fields_and_values": question_fields_and_values,
        }

    content_list = [{"content": m.get("content", "")} for m in messages]
    for field, data_key, sample_entity, entity_list in [
        ("message_id", "id", sample, messages),
        ("channel_name", "name", resolved_channel, channels),
        ("server_name", "name", resolved_server, servers),
        ("content", "content", {"content": sample_content}, content_list),
    ]:
        if sample_entity is None or not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_ADD_REACTION.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample_entity.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_select_dm_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    data_dict = await _ensure_discord_dataset(task_url, dataset, entity_type="members")
    members = data_dict.get("members", [])
    if not members:
        return constraints
    sample = random.choice(members)
    for field, data_key in [("name", "username")]:
        allowed = FIELD_OPERATORS_MAP_DM.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, members)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_send_dm_message_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    members_dict, messages_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="members"),
        _ensure_discord_dataset(task_url, dataset, entity_type="messages"),
    )
    members = members_dict.get("members", [])
    messages = messages_dict.get("messages", [])
    if not members:
        return constraints
    sample_member = random.choice(members)
    sample_content = random.choice(messages).get("content", "") if messages else random.choice(["Hey", "Thanks", "OK"])
    content_list = [{"content": m.get("content", "")} for m in messages] if messages else [{"content": sample_content}]
    content_list = list(content_list)  # in case messages is empty after filter
    for field, data_key, sample_entity, entity_list in [
        ("name", "username", sample_member, members),
        ("content", "content", {"content": sample_content}, content_list),
    ]:
        if not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_DM.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample_entity.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


def generate_settings_appearance_constraints() -> list[dict[str, Any]]:
    themes = ["dark", "light"]
    op = ComparisonOperator.EQUALS
    return [create_constraint_dict("theme", op, random.choice(themes))]


def generate_settings_notifications_constraints() -> list[dict[str, Any]]:
    op = ComparisonOperator(random.choice(FIELD_OPERATORS_MAP_SETTINGS_NOTIFICATIONS["enabled"]))
    return [create_constraint_dict("enabled", op, random.choice([True, False]))]


def generate_settings_account_constraints() -> list[dict[str, Any]]:
    names = [
        "Alex",
        "Jordan",
        "Sam",
        "Casey",
        "Dev User",
        "Test User",
        "Taylor",
        "Morgan",
        "Riley",
        "Avery",
        "Jamie",
        "Cameron",
        "Drew",
        "Skyler",
        "Quinn",
        "Blake",
        "Hayden",
        "Parker",
        "Rowan",
        "Emerson",
    ]
    op = ComparisonOperator(random.choice(FIELD_OPERATORS_MAP_SETTINGS_ACCOUNT["name"]))
    field_value = random.choice(names)
    value = _generate_constraint_value(op, field_value, "name", [{"name": s} for s in names])
    if value is not None:
        return [create_constraint_dict("name", op, value)]
    return [create_constraint_dict("name", op, random.choice(names))]


def generate_create_server_constraints() -> list[dict[str, Any]]:
    sample_names = [
        "Test Server",
        "My Server",
        "Dev Hub",
        "Gaming Zone",
        "Team Chat",
        "Code Central",
        "Study Group",
        "Project Alpha",
        "Tech Talk",
        "Community Lounge",
        "Startup Space",
        "AI Lab",
        "Design Studio",
        "Marketing Crew",
        "Support Desk",
        "Innovation Hub",
        "Developers Den",
        "Creative Corner",
        "Cloud Workspace",
        "Beta Testers",
    ]
    op = ComparisonOperator(random.choice(FIELD_OPERATORS_MAP_CREATE_SERVER["server_name"]))
    field_value = random.choice(sample_names)
    value = _generate_constraint_value(op, field_value, "server_name", [{"server_name": s} for s in sample_names])
    if value is not None:
        return [create_constraint_dict("server_name", op, value)]
    return [create_constraint_dict("server_name", op, random.choice(sample_names))]


async def generate_open_server_settings_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    return await generate_select_server_constraints(task_url, dataset)


async def generate_delete_server_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    return await generate_select_server_constraints(task_url, dataset)


async def generate_create_channel_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    data_dict = await _ensure_discord_dataset(task_url, dataset, entity_type="servers")
    servers = data_dict.get("servers", [])
    if not servers:
        return constraints
    sample = random.choice(servers)
    for field, data_key in [("server_name", "name")]:
        allowed = FIELD_OPERATORS_MAP_CREATE_CHANNEL.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, servers)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    channel_names = [
        "general",
        "random",
        "voice-chat",
        "dev-help",
        "announcements",
        "introductions",
        "off-topic",
        "memes",
        "bug-reports",
        "feature-requests",
        "frontend",
        "backend",
        "ai-discussion",
        "project-updates",
        "resources",
        "showcase",
        "events",
        "q-and-a",
        "support",
        "testing",
    ]
    channel_name_ops = FIELD_OPERATORS_MAP_CREATE_CHANNEL.get("channel_name", [])
    if channel_name_ops:
        op = ComparisonOperator(random.choice(channel_name_ops))
        val = random.choice(channel_names)
        value = _generate_constraint_value(op, val, "channel_name", [{"channel_name": c} for c in channel_names])
        if value is not None:
            constraints.append(create_constraint_dict("channel_name", op, value))
        else:
            constraints.append(create_constraint_dict("channel_name", op, val))
    else:
        constraints.append(create_constraint_dict("channel_name", ComparisonOperator.EQUALS, random.choice(channel_names)))
    channel_types = ["text", "voice"]
    type_ops = FIELD_OPERATORS_MAP_CREATE_CHANNEL.get("channel_type", [])
    if type_ops:
        op_type = ComparisonOperator(random.choice(type_ops))
        constraints.append(create_constraint_dict("channel_type", op_type, random.choice(channel_types)))
    return constraints


async def generate_join_voice_channel_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    constraints: list[dict[str, Any]] = []
    channels_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    channels = channels_dict.get("channels", [])
    servers = servers_dict.get("servers", [])
    voice = [c for c in channels if c.get("type") == "voice"]
    if not voice:
        voice = channels
    if not voice:
        return [] if test_types == "data_extraction_only" else constraints

    sample_channel = random.choice(voice)
    resolved_server = next(
        (s for s in servers if s.get("id") == sample_channel.get("serverId")),
        None,
    )
    channel_name = sample_channel.get("name", "")
    server_name = resolved_server.get("name", "") if resolved_server else ""

    if test_types == "data_extraction_only":
        verify_field = random.choice(["channel_name", "server_name"])
        verify_value = channel_name if verify_field == "channel_name" else server_name
        if not verify_value:
            return []
        other_field = "server_name" if verify_field == "channel_name" else "channel_name"
        other_value = server_name if verify_field == "channel_name" else channel_name
        if not other_value:
            return []
        return {
            "constraints": [create_constraint_dict(verify_field, ComparisonOperator.EQUALS, verify_value)],
            "question_fields_and_values": {other_field: other_value},
        }

    for field, data_key, sample, entity_list in [
        ("channel_name", "name", sample_channel, voice),
        ("server_name", "name", resolved_server, servers),
    ]:
        if sample is None or not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_CHANNEL.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_leave_voice_channel_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    channels_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    channels = channels_dict.get("channels", [])
    servers = servers_dict.get("servers", [])
    voice = [c for c in channels if c.get("type") == "voice"]
    if not voice:
        voice = channels
    if not voice:
        return constraints
    sample = random.choice(voice)
    resolved_server = (
        next(
            (s for s in servers if s.get("id") == sample.get("serverId")),
            None,
        )
        if servers
        else None
    )
    for field, data_key, sample_entity, entity_list in [
        ("channel_name", "name", sample, voice),
        ("server_name", "name", resolved_server, servers),
    ]:
        if sample_entity is None or not entity_list:
            continue
        allowed = FIELD_OPERATORS_MAP_CHANNEL.get(field, [])
        if not allowed:
            continue
        op = ComparisonOperator(random.choice(allowed))
        val = sample_entity.get(data_key, "")
        value = _generate_constraint_value(op, val, data_key, entity_list)
        if value is not None:
            constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_voice_mute_toggle_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    channels_dict, servers_dict = await asyncio.gather(
        _ensure_discord_dataset(task_url, dataset, entity_type="channels"),
        _ensure_discord_dataset(task_url, dataset, entity_type="servers"),
    )
    channels = channels_dict.get("channels", [])
    servers = servers_dict.get("servers", [])
    voice = [c for c in channels if c.get("type") == "voice"]
    if not voice:
        voice = channels
    if voice:
        sample = random.choice(voice)
        resolved_server = (
            next(
                (s for s in servers if s.get("id") == sample.get("serverId")),
                None,
            )
            if servers
            else None
        )
        for field, data_key, sample_entity, entity_list in [
            ("channel_name", "name", sample, voice),
            ("server_name", "name", resolved_server, servers),
        ]:
            if sample_entity is None or not entity_list:
                continue
            allowed = FIELD_OPERATORS_MAP_VOICE_MUTE.get(field, [])
            if not allowed:
                continue
            op = ComparisonOperator(random.choice(allowed))
            val = sample_entity.get(data_key, "")
            value = _generate_constraint_value(op, val, data_key, entity_list)
            if value is not None:
                constraints.append(create_constraint_dict(field, op, value))
    op = ComparisonOperator.EQUALS
    constraints.append(create_constraint_dict("muted", op, random.choice([True, False])))
    return constraints
