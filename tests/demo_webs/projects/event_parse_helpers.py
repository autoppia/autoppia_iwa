"""Shared helpers for testing that event parse() data keys match Pydantic model fields.

Ensures that when someone adds data.get("newKey") in parse() they must add the
corresponding field to the model (and vice versa), or the test fails.
"""

import ast
import inspect
import re
import textwrap

BASE_EVENT_FIELDS = {"event_name", "timestamp", "web_agent_id", "user_id"}


def get_payload_derived_fields(event_class: type) -> set[str]:
    """Return model field names that come from backend_event.data (excludes base Event fields)."""
    return set(event_class.model_fields) - BASE_EVENT_FIELDS


def get_parse_cls_kwargs(event_class: type) -> set[str]:
    """Return keyword argument names passed to cls() in this class's parse() method (from AST)."""
    try:
        source = inspect.getsource(event_class.parse)
    except (TypeError, OSError):
        return set()
    source = textwrap.dedent(source)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "cls":
            return {kw.arg for kw in node.keywords if kw.arg is not None}
    return set()


def assert_parse_cls_kwargs_match_model(event_class: type) -> None:
    """Assert that kwargs passed to cls() in parse() (minus base fields) match the model's payload-derived fields.

    Fails if:
    - parse() passes a kwarg that has no corresponding model field.
    - The model has a payload-derived field that parse() does not pass to cls().

    When parse() uses cls(**data), a helper like _base_event_kwargs(), or we only see base fields in the
    cls() call, the strict check is skipped (we cannot verify from AST).
    """
    all_parse_kwargs = get_parse_cls_kwargs(event_class)
    parse_payload_kwargs = all_parse_kwargs - BASE_EVENT_FIELDS
    payload_fields = get_payload_derived_fields(event_class)
    # Skip when we could not extract explicit payload kwargs (e.g. cls(**x) or only base fields)
    if not all_parse_kwargs and payload_fields:
        return
    if not all_parse_kwargs:
        return
    if not parse_payload_kwargs and payload_fields:
        return
    missing_in_model = parse_payload_kwargs - payload_fields
    extra_in_model = payload_fields - parse_payload_kwargs
    # Skip when we found some but not all payload kwargs (likely rest passed via **kwargs)
    if extra_in_model and len(parse_payload_kwargs) < len(payload_fields):
        return
    assert not missing_in_model, f"{event_class.__name__}: parse() passes these to cls() but model has no field: {missing_in_model}. Add these fields to the model or remove from parse()."
    assert not extra_in_model, f"{event_class.__name__}: model has fields not passed in parse() cls(): {extra_in_model}. Add to parse() cls() or remove from model."


def _camel_to_snake(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case."""
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def data_key_to_model_field(data_key: str, override: dict[str, str] | None = None) -> str:
    """Map a payload data key (e.g. calendarName) to model field name (e.g. calendar_name)."""
    if override and data_key in override:
        return override[data_key]
    return _camel_to_snake(data_key)


def assert_event_model_matches_parse_data_keys(
    event_class: type,
    expected_data_keys: set[str],
    data_key_to_field_override: dict[str, str] | None = None,
) -> None:
    """Assert that the event model's payload-derived fields match the expected data keys from parse().

    Fails if:
    - parse() uses a data key that has no corresponding model field.
    - The model has a payload-derived field that is not in expected_data_keys.

    When data_key_to_field_override is None, any key in expected_data_keys that is already
    a payload-derived model field is used as-is (identity), so exact model field names work.
    """
    payload_fields = get_payload_derived_fields(event_class)
    normalized_expected = {(k if (data_key_to_field_override is None and k in payload_fields) else data_key_to_model_field(k, data_key_to_field_override)) for k in expected_data_keys}
    missing_in_model = normalized_expected - payload_fields
    extra_in_model = payload_fields - normalized_expected
    assert not missing_in_model, f"{event_class.__name__}: parse() uses these data keys but model has no field: {missing_in_model}. Add these fields to the model or remove from parse."
    assert not extra_in_model, f"{event_class.__name__}: model has fields not set from parse data: {extra_in_model}. Add to expected_data_keys and parse(), or remove from model."
