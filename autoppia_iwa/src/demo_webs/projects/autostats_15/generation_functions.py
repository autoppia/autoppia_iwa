"""Constraint generators for autostats_15. Data is synthetic (no DB); constraints built from static pools."""

import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.shared_utils import create_constraint_dict

from .data import (
    ACCOUNT_TYPES,
    FIELD_OPERATORS_MAP_EXECUTE_BUY,
    FIELD_OPERATORS_MAP_EXECUTE_SELL,
    FIELD_OPERATORS_MAP_VIEW_ACCOUNT,
    FIELD_OPERATORS_MAP_VIEW_BLOCK,
    FIELD_OPERATORS_MAP_VIEW_SUBNET,
    FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
    INTEGER_FIELDS_EXECUTE_BUY,
    INTEGER_FIELDS_EXECUTE_SELL,
    INTEGER_FIELDS_VIEW_ACCOUNT,
    INTEGER_FIELDS_VIEW_BLOCK,
    INTEGER_FIELDS_VIEW_VALIDATOR,
    SELECTED_FIELDS_EXECUTE_BUY,
    SELECTED_FIELDS_EXECUTE_SELL,
    SELECTED_FIELDS_VIEW_ACCOUNT,
    SELECTED_FIELDS_VIEW_BLOCK,
    SELECTED_FIELDS_VIEW_SUBNET,
    SELECTED_FIELDS_VIEW_VALIDATOR,
    SUBNET_NAMES,
)


def _build_subnet_dataset() -> list[dict[str, Any]]:
    """Synthetic subnets for constraint generation (matches web_15 SUBNET_NAMES + plausible metrics)."""
    return [
        {
            "subnet_name": name,
            "emission": 100_000 * (i + 1) + random.randint(0, 50000),
            "price": 1.0 if i == 0 else round(0.01 + random.random() * 1.99, 4),
            "marketCap": (50_000_000 if i == 0 else 1_000_000 + random.randint(0, 10_000_000)),
            "volume24h": (5_000_000 if i == 0 else 100_000 + random.randint(0, 1_000_000)),
        }
        for i, name in enumerate(SUBNET_NAMES)
    ]


def _build_validator_dataset() -> list[dict[str, Any]]:
    """Synthetic validators for constraint generation."""
    return [
        {
            "hotkey": f"5JhG4H2f...zRxQJA{i}",
            "rank": i + 1,
            "dominance": round(0.5 + random.random() * 4.5, 2),
            "nominatorCount": 20 + random.randint(0, 80),
            "totalWeight": 100_000 + random.randint(0, 900_000),
            "rootStake": 10_000 + random.randint(0, 150_000),
            "alphaStake": 50_000 + random.randint(0, 850_000),
            "commission": round(1.0 + random.random() * 15, 2),
        }
        for i in range(20)
    ]


def _build_block_dataset() -> list[dict[str, Any]]:
    """Synthetic blocks for constraint generation."""
    return [
        {
            "number": 1_000_000 - i,
            "hash": f"0x{'a' * 16}{i:04x}{'b' * 40}",
            "validator": f"5Validator{i}...",
            "epoch": (1_000_000 - i) // 360,
            "extrinsicsCount": 4 + random.randint(0, 8),
            "eventsCount": 8 + random.randint(0, 16),
        }
        for i in range(50)
    ]


def _build_account_dataset() -> list[dict[str, Any]]:
    """Synthetic accounts for constraint generation."""
    return [
        {
            "rank": i + 1,
            "address": f"5BiteWLX...9y{i:02d}",
            "balance": 20_000 + random.randint(0, 100_000),
            "stakedAmount": 400_000 + random.randint(0, 100_000),
            "stakingRatio": round(70 + random.random() * 25, 1),
            "accountType": random.choice(ACCOUNT_TYPES),
        }
        for i in range(30)
    ]


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
        constraint_value = value
        if op in (ComparisonOperator.GREATER_THAN, ComparisonOperator.GREATER_EQUAL) and isinstance(value, int | float):
            constraint_value = value - (random.random() * 0.1 * abs(value) if value else 0)
        elif op in (ComparisonOperator.LESS_THAN, ComparisonOperator.LESS_EQUAL) and isinstance(value, int | float):
            constraint_value = value + (random.random() * 0.1 * abs(value) if value else 0)
        if field in integer_fields and isinstance(constraint_value, int | float):
            constraint_value = round(constraint_value)
        constraints.append(create_constraint_dict(field, op, constraint_value))
    return constraints


async def generate_view_subnet_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_SUBNET from static subnet names and metrics."""
    del task_url, dataset
    data = _build_subnet_dataset()
    return _generate_constraints_static(data, FIELD_OPERATORS_MAP_VIEW_SUBNET, SELECTED_FIELDS_VIEW_SUBNET, num_constraints=2)


async def generate_view_validator_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_VALIDATOR from synthetic validator data."""
    del task_url, dataset
    data = _build_validator_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
        SELECTED_FIELDS_VIEW_VALIDATOR,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_VALIDATOR,
    )


async def generate_view_block_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_BLOCK from synthetic block data."""
    del task_url, dataset
    data = _build_block_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_BLOCK,
        SELECTED_FIELDS_VIEW_BLOCK,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_BLOCK,
    )


async def generate_view_account_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for VIEW_ACCOUNT from synthetic account data."""
    del task_url, dataset
    data = _build_account_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_VIEW_ACCOUNT,
        SELECTED_FIELDS_VIEW_ACCOUNT,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_VIEW_ACCOUNT,
    )


def _build_execute_buy_dataset() -> list[dict[str, Any]]:
    """Synthetic buy orders per subnet so prompts like 'compra 10 TAU en la subnet Text Prompting' are verifiable."""
    return [
        {
            "subnet_name": name,
            "orderType": "market",
            "amountTAU": 10 + random.randint(0, 90),
            "amountAlpha": 5 + random.randint(0, 45),
            "priceImpact": round(random.random() * 0.2, 4),
            "maxAvailableTAU": 500 + random.randint(0, 1500),
        }
        for name in SUBNET_NAMES
    ]


def _build_execute_sell_dataset() -> list[dict[str, Any]]:
    """Synthetic sell orders per subnet so prompts like 'vende 20 alpha en la subnet Text Prompting' are verifiable."""
    return [
        {
            "subnet_name": name,
            "orderType": "market",
            "amountTAU": 0,
            "amountAlpha": 10 + random.randint(0, 90),
            "priceImpact": round(random.random() * 0.2, 4),
            "maxDelegatedAlpha": 100 + random.randint(0, 400),
        }
        for name in SUBNET_NAMES
    ]


async def generate_execute_buy_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for EXECUTE_BUY (subnet_name + amountTAU/amountAlpha) so prompts are verifiable."""
    del task_url, dataset
    data = _build_execute_buy_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_EXECUTE_BUY,
        SELECTED_FIELDS_EXECUTE_BUY,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_EXECUTE_BUY,
    )


async def generate_execute_sell_constraints(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """Generate constraints for EXECUTE_SELL (subnet_name + amountAlpha/maxDelegatedAlpha) so prompts are verifiable."""
    del task_url, dataset
    data = _build_execute_sell_dataset()
    return _generate_constraints_static(
        data,
        FIELD_OPERATORS_MAP_EXECUTE_SELL,
        SELECTED_FIELDS_EXECUTE_SELL,
        num_constraints=2,
        integer_fields=INTEGER_FIELDS_EXECUTE_SELL,
    )
