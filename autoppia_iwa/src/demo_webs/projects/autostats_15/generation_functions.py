"""Constraint generators for autostats_15. Server data only (single source of truth); no local/synthetic fallback."""

import random
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    FIELD_OPERATORS_MAP_CONNECT_WALLET,
    FIELD_OPERATORS_MAP_DISCONNECT_WALLET,
    FIELD_OPERATORS_MAP_EXECUTE_BUY,
    FIELD_OPERATORS_MAP_EXECUTE_SELL,
    FIELD_OPERATORS_MAP_FAVORITE_SUBNET,
    FIELD_OPERATORS_MAP_TRANSFER_COMPLETE,
    FIELD_OPERATORS_MAP_VIEW_ACCOUNT,
    FIELD_OPERATORS_MAP_VIEW_BLOCK,
    FIELD_OPERATORS_MAP_VIEW_SUBNET,
    FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
    INTEGER_FIELDS_EXECUTE_BUY,
    INTEGER_FIELDS_EXECUTE_SELL,
    INTEGER_FIELDS_FAVORITE_SUBNET,
    INTEGER_FIELDS_TRANSFER_COMPLETE,
    INTEGER_FIELDS_VIEW_ACCOUNT,
    INTEGER_FIELDS_VIEW_BLOCK,
    INTEGER_FIELDS_VIEW_VALIDATOR,
    SELECTED_FIELDS_CONNECT_WALLET,
    SELECTED_FIELDS_DISCONNECT_WALLET,
    SELECTED_FIELDS_EXECUTE_BUY,
    SELECTED_FIELDS_EXECUTE_SELL,
    SELECTED_FIELDS_FAVORITE_SUBNET,
    SELECTED_FIELDS_TRANSFER_COMPLETE,
    SELECTED_FIELDS_VIEW_ACCOUNT,
    SELECTED_FIELDS_VIEW_BLOCK,
    SELECTED_FIELDS_VIEW_SUBNET,
    SELECTED_FIELDS_VIEW_VALIDATOR,
    VISIBLE_FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
    VISIBLE_FIELD_VIEW_ACCOUNT,
    VISIBLE_FIELD_VIEW_BLOCK,
    VISIBLE_FIELD_VIEW_SUBNET,
    VISIBLE_FIELDS_TRANSFER_COMPLETE,
    WALLET_NAMES,
)

# UI display: emission always in M; marketCap/volume24h use formatLargeNumber (B/M/K by magnitude).
_EMISSION_DIVISOR_M = 1_000_000


def _scale_large_number(value: float) -> str:
    """Scale value like UI formatLargeNumber; always 2 decimals (e.g. 6.70K) to match formatNumber(value, 2)."""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.2f}"


async def _ensure_autostats_dataset(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    *,
    entity_type: str,
) -> dict[str, list[dict[str, Any]]]:
    """
    Fetch entity data using seed from task_url (same flow as autocrm_5 _ensure_crm_dataset).
    Returns a dictionary with entity_type as the key.
    """
    _ = dataset  # Unused parameter kept for backward compatibility
    from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

    from .data_utils import fetch_data

    seed = get_seed_from_url(task_url)
    fetched = await fetch_data(
        entity_type=entity_type,
        seed_value=seed,
        count=50,
    )
    return {entity_type: fetched or []}


async def _get_autostats_entity_list(
    task_url: str | None,
    dataset: dict[str, list[dict[str, Any]]] | None,
    entity_type: str,
) -> list[dict[str, Any]]:
    """Fetch autostats dataset for entity_type and return the list. Same pattern as _get_crm_entity_list."""
    data_dict = await _ensure_autostats_dataset(task_url, dataset, entity_type=entity_type)
    return data_dict.get(entity_type, [])


def _build_wallet_dataset() -> list[dict[str, Any]]:
    """Local data from WALLET_NAMES for CONNECT_WALLET / DISCONNECT_WALLET constraint generation (names only)."""
    return [{"wallet_name": name} for name in WALLET_NAMES]


def _to_float_safe(value: Any) -> float | None:
    """Coerce value to float for numeric constraint generation (matches autocrm_5)."""
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "").strip())
        except Exception:
            return None
    return None


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    """Generate a constraint value for the given operator (same pattern as autocrm_5)."""
    if operator == ComparisonOperator.EQUALS:
        return field_value

    if operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) != field_value and v.get(field) is not None]
        return random.choice(valid) if valid else None

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        return random.choice(valid) if valid else None

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        base = _to_float_safe(field_value)
        if base is None:
            return None
        delta = random.uniform(1, 3)
        if operator == ComparisonOperator.GREATER_THAN:
            return round(base - delta, 2)
        if operator == ComparisonOperator.LESS_THAN:
            return round(base + delta, 2)
        if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
            return round(base, 2)

    return None


def _generate_constraints_static(
    dataset: list[dict[str, Any]],
    field_operators: dict[str, list],
    selected_fields: list[str],
    *,
    num_constraints: int = 2,
    integer_fields: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Build constraints from a static dataset; pick one item and 1..num_constraints fields.
    integer_fields: field names that must have integer constraint values (e.g. rank, eventsCount).
    """
    if not dataset:
        return []
    integer_fields = integer_fields or set()
    sample = random.choice(dataset)
    fields = random.sample(selected_fields, min(num_constraints, len(selected_fields)))
    constraints = []
    for field in fields:
        if field not in sample or field not in field_operators:
            continue
        value = sample[field]
        if value is None:
            continue
        allowed = field_operators[field]
        op_str = random.choice(allowed)
        op = ComparisonOperator(op_str)
        constraint_value = _generate_constraint_value(op, value, field, dataset)
        if constraint_value is None:
            continue
        if field in integer_fields and isinstance(constraint_value, int | float):
            constraint_value = round(constraint_value)
        constraints.append(create_constraint_dict(field, op, constraint_value))
    return constraints


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    selected_fields: list[str],
    integer_fields: set[str] | None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure."""
    integer_fields = integer_fields or set()
    available_fields = [f for f in selected_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        logger.warning("Available item fields are less than 2; task generation for Data extraction test needs >= 2.")
        return None
    verify_field = random.choice(available_fields)
    verify_value = selected_item.get(verify_field)
    if verify_value is None:
        logger.warning("Verify field has no value; skipping Data extraction task for this item.")
        return None
    if verify_field in integer_fields and isinstance(verify_value, int | float):
        verify_value = round(verify_value)
    question_candidates = [f for f in available_fields if f != verify_field]
    if not question_candidates:
        logger.warning("There is no field for asking question (no question candidates after verify field).")
        return None
    num_question_fields = min(len(question_candidates), random.randint(1, len(question_candidates)))
    question_fields = random.sample(question_candidates, num_question_fields)
    question_fields_and_values = {}
    for qf in question_fields:
        val = selected_item.get(qf)
        if val is not None:
            if qf in integer_fields and isinstance(val, int | float):
                val = round(val)
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        logger.warning("There is no field for asking question.")
        return None
    constraints = [create_constraint_dict(verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


async def generate_view_subnet_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_SUBNET from server data only."""
    data = await _get_autostats_entity_list(task_url, dataset, "subnets")
    if not data:
        return []
    if test_types == "data_extraction_only":
        selected_item = random.choice(data)
        price = selected_item.get("price")
        emission = selected_item.get("emission")
        market_cap = selected_item.get("marketCap")
        volume24h = selected_item.get("volume24h")
        selected_item["price"] = f"τ{round(price, 4)}"
        # Emission: always M (UI); marketCap/volume24h: B/M/K by magnitude (formatLargeNumber), 2 decimals
        selected_item["emission"] = f"{round((emission or 0) / _EMISSION_DIVISOR_M, 2)}M"
        selected_item["marketCap"] = _scale_large_number(market_cap)
        selected_item["volume24h"] = _scale_large_number(volume24h)
        result = _build_data_extraction_result(
            selected_item,
            VISIBLE_FIELD_VIEW_SUBNET,
            None,
        )
        return result if result is not None else []
    return _generate_constraints_static(data, FIELD_OPERATORS_MAP_VIEW_SUBNET, SELECTED_FIELDS_VIEW_SUBNET, num_constraints=2)


async def generate_view_validator_constraints(
    task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None, test_types: str | None = None
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_VALIDATOR from server data only."""
    data = await _get_autostats_entity_list(task_url, dataset, "validators")
    if not data:
        return []
    if test_types == "data_extraction_only":
        selected_item = random.choice(data)
        if selected_item.get("totalWeight") is not None:
            selected_item["totalWeight"] = f"τ{_scale_large_number(float(selected_item['totalWeight']))}"
        if selected_item.get("rootStake") is not None:
            selected_item["rootStake"] = f"τ{_scale_large_number(float(selected_item['rootStake']))}"
        if selected_item.get("alphaStake") is not None:
            selected_item["alphaStake"] = f"τ{_scale_large_number(float(selected_item['alphaStake']))}"
        if selected_item.get("dominance") is not None:
            selected_item["dominance"] = f"{round(float(selected_item['dominance']), 2)}%"
        if selected_item.get("commission") is not None:
            selected_item["commission"] = f"{round(float(selected_item['commission']), 2)}%"
        result = _build_data_extraction_result(
            selected_item,
            VISIBLE_FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
            INTEGER_FIELDS_VIEW_VALIDATOR,
        )
        return result if result is not None else []
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
        SELECTED_FIELDS_VIEW_VALIDATOR,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_VALIDATOR,
    )


async def generate_view_block_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_BLOCK from server data only."""
    data = await _get_autostats_entity_list(task_url, dataset, "blocks")
    if not data:
        return []
    if test_types == "data_extraction_only":
        selected_item = random.choice(data)
        result = _build_data_extraction_result(
            selected_item,
            VISIBLE_FIELD_VIEW_BLOCK,
            INTEGER_FIELDS_VIEW_BLOCK,
        )
        return result if result is not None else []
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_BLOCK,
        SELECTED_FIELDS_VIEW_BLOCK,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_BLOCK,
    )


async def generate_view_account_constraints(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
    test_types: str | None = None,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for VIEW_ACCOUNT from server data only.
    When test_types is 'data_extraction_only', returns a dict with
    constraints (verify field only, equals) and question_fields_and_values for LLM prompt.
    """
    data = await _get_autostats_entity_list(task_url, dataset, "accounts")
    if not data:
        return []

    if test_types == "data_extraction_only":
        selected_item = random.choice(data)
        # UI display format: τ + B/M/K for balance and stakedAmount; % for ratio and 24h; address unchanged
        balance = selected_item.get("balance")
        staked = selected_item.get("stakedAmount")
        staking_ratio = selected_item.get("stakingRatio")
        selected_item["balance"] = f"τ{_scale_large_number(float(balance))}"
        selected_item["stakedAmount"] = f"τ{_scale_large_number(float(staked))}"
        selected_item["stakingRatio"] = f"{round(staking_ratio, 1)}%"
        result = _build_data_extraction_result(
            selected_item,
            VISIBLE_FIELD_VIEW_ACCOUNT,
            INTEGER_FIELDS_VIEW_ACCOUNT,
        )
        return result if result is not None else []

    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_ACCOUNT,
        SELECTED_FIELDS_VIEW_ACCOUNT,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_ACCOUNT,
    )


async def generate_execute_buy_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for EXECUTE_BUY from server subnets only."""
    subnets = await _get_autostats_entity_list(task_url, dataset, "subnets")
    if not subnets:
        return []
    data = [
        {
            "subnet_name": s.get("subnet_name", s.get("name", "")),
            "amountTAU": 10 + random.randint(0, 90),
            "amountAlpha": 5 + random.randint(0, 45),
        }
        for s in subnets
    ]
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_EXECUTE_BUY,
        SELECTED_FIELDS_EXECUTE_BUY,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_EXECUTE_BUY,
    )


async def generate_execute_sell_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for EXECUTE_SELL from server subnets only."""
    subnets = await _get_autostats_entity_list(task_url, dataset, "subnets")
    if not subnets:
        return []
    data = [
        {
            "subnet_name": s.get("subnet_name", s.get("name", "")),
            "amountTAU": 1 + random.randint(0, 9),
            "amountAlpha": 10 + random.randint(0, 90),
        }
        for s in subnets
    ]
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_EXECUTE_SELL,
        SELECTED_FIELDS_EXECUTE_SELL,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_EXECUTE_SELL,
    )


def generate_connect_wallet_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for CONNECT_WALLET from local WALLET_NAMES data."""
    _ = task_url, dataset
    data = _build_wallet_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_CONNECT_WALLET,
        SELECTED_FIELDS_CONNECT_WALLET,
        num_constraints=2,
    )


def generate_disconnect_wallet_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for DISCONNECT_WALLET from local WALLET_NAMES data."""
    _ = task_url, dataset
    data = _build_wallet_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_DISCONNECT_WALLET,
        SELECTED_FIELDS_DISCONNECT_WALLET,
        num_constraints=2,
    )


async def generate_transfer_complete_constraints(
    task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None, test_types: str | None = None
) -> list[dict[str, Any]] | dict[str, Any]:
    """Generate constraints for TRANSFER_COMPLETE from server data only."""
    data = await _get_autostats_entity_list(task_url, dataset, "transfers")
    if not data:
        return []
    if test_types == "data_extraction_only":
        selected_item = random.choice(data)
        selected_item["amount"] = _scale_large_number(float(selected_item.get("amount") or 0))
        result = _build_data_extraction_result(
            selected_item,
            VISIBLE_FIELDS_TRANSFER_COMPLETE,
            INTEGER_FIELDS_TRANSFER_COMPLETE,
        )
        return result if result is not None else []
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_TRANSFER_COMPLETE,
        SELECTED_FIELDS_TRANSFER_COMPLETE,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_TRANSFER_COMPLETE,
    )


async def generate_favorite_subnet_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for FAVORITE_SUBNET from server subnets (subnet_name only)."""
    data = await _get_autostats_entity_list(task_url, dataset, "subnets")
    if not data:
        return []
    data = [{"subnet_name": s.get("subnet_name", s.get("name", ""))} for s in data]
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_FAVORITE_SUBNET,
        SELECTED_FIELDS_FAVORITE_SUBNET,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_FAVORITE_SUBNET,
    )
