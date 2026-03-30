"""
Fetch autostats_15 data from the webs_server /datasets/load API and apply the same
normalize + derive transformations as the web UI, so constraint generation uses
identical field names and values. All transformation logic lives here for consistency
across projects (no separate server_data module).
"""

from __future__ import annotations

import copy
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.data_provider import load_dataset_data
from autoppia_iwa.src.demo_webs.utils import get_backend_service_url

PROJECT_KEY = "web_15_autostats"


def _seed_random(seed: int):
    """Deterministic RNG matching TypeScript: (value * 1664525 + 1013904223) % 4294967296."""
    value = seed & 0xFFFFFFFF

    def next_() -> float:
        nonlocal value
        value = (value * 1664525 + 1013904223) % 4294967296
        return value / 4294967296

    return next_


def _generate_trend_data(
    length: int,
    seed: int,
    trend: str = "neutral",
) -> list[float]:
    rng = _seed_random(seed)
    data: list[float] = []
    value = 50.0
    trend_bias = {"up": 0.6, "down": -0.6, "neutral": 0.0}[trend]
    for _ in range(length):
        change = (rng() - 0.5) * 10 + trend_bias
        value = max(0.0, min(100.0, value + change))
        data.append(value)
    return data


def _normalize_block(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize block: ensure extrinsics list, keep timestamp as string for JSON."""
    out = copy.deepcopy(raw)
    out.setdefault("extrinsics", [])
    return out


def _normalize_account(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize account: ensure delegations and transactions lists."""
    out = copy.deepcopy(raw)
    out.setdefault("delegations", [])
    out.setdefault("transactions", [])
    out["balance"] = raw.get("balance") if raw.get("balance") is not None else 0
    out["stakedAmount"] = raw.get("stakedAmount") if raw.get("stakedAmount") is not None else 0
    return out


def _normalize_transfer(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize transfer: add block_number from blockNumber for constraint fields."""
    out = copy.deepcopy(raw)
    if "blockNumber" in raw and "block_number" not in out:
        out["block_number"] = raw["blockNumber"]
    return out


def _add_trends_to_subnets(subnets: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    """Add price, marketCap, volume24h, trendData and subnet_name (from name) for constraints."""
    result: list[dict[str, Any]] = []
    for subnet in subnets:
        trend_seed = seed + subnet.get("id", 0)
        rng = _seed_random(trend_seed)
        is_root = subnet.get("id") == 0
        price = 1.0 if is_root else rng() * 1.99 + 0.01
        market_cap = (50_000_000 + rng() * 50_000_000) if is_root else (1_000_000 + rng() * 10_000_000)
        volume24h = (5_000_000 + rng() * 5_000_000) if is_root else (100_000 + rng() * 1_000_000)
        price_change_24h = (rng() - 0.5) * 20
        trend = "up" if price_change_24h > 2 else ("down" if price_change_24h < -2 else "neutral")
        row = copy.deepcopy(subnet)
        row["subnet_name"] = subnet.get("name", "")
        row["subnet_id"] = subnet.get("id", 0)
        row["price"] = price
        row["marketCap"] = market_cap
        row["volume24h"] = volume24h
        row["priceChange1h"] = (rng() - 0.5) * 5
        row["priceChange24h"] = price_change_24h
        row["priceChange1w"] = (rng() - 0.5) * 30
        row["priceChange1m"] = (rng() - 0.5) * 50
        row["trendData"] = _generate_trend_data(7, trend_seed, trend)
        result.append(row)
    return result


def _block_to_block_with_details(block: dict[str, Any]) -> dict[str, Any]:
    """Add only epoch (and setdefault counts). Other fields (successRate, totalFees, sizeKB, extrinsicBreakdown) are not in VIEW_BLOCK event."""
    extrinsics = block.get("extrinsics") or []
    out = copy.deepcopy(block)
    out["epoch"] = int(block.get("number", 0)) // 360
    out.setdefault("extrinsicsCount", len(extrinsics))
    out.setdefault("eventsCount", len(extrinsics) * 2)
    return out


def _account_to_account_with_details(account: dict[str, Any], index: int) -> dict[str, Any]:
    """Add rank, stakingRatio, accountType, balanceTrend, etc. (matches UI accountToAccountWithDetails)."""
    balance = account.get("balance") or 0
    staked = account.get("stakedAmount") or 0
    total_value = balance + staked
    staking_ratio = (staked / total_value * 100) if total_value > 0 else 0.0
    if staked > 100000:
        account_type = "validator"
    elif staked > 10000:
        account_type = "nominator"
    else:
        account_type = "regular"
    delegations = account.get("delegations") or []
    transactions = account.get("transactions") or []
    first_ts = transactions[0].get("timestamp") if transactions else None
    out = copy.deepcopy(account)
    out["rank"] = index + 1
    out["totalValue"] = total_value
    out["stakingRatio"] = staking_ratio
    out["delegationCount"] = len(delegations)
    out["transactionCount"] = len(transactions)
    out["balanceChange24h"] = 0
    out["firstSeen"] = first_ts
    out["lastActive"] = first_ts
    out["accountType"] = account_type
    out["balanceTrend"] = _generate_trend_data(30, index + 9000, "neutral")
    return out


# ---------------------------------------------------------------------------
# Public API: fetch_data
# ---------------------------------------------------------------------------


async def fetch_data(
    entity_type: str,
    seed_value: int,
    count: int = 50,
) -> list[dict]:
    """
    Fetch one entity type from the server and return normalized + derived items
    (same shape as web UI) for constraint generation.

    Called by SimpleTaskGenerator._load_dataset for each entity type when
    project is autostats_15.

    Args:
        entity_type: One of validators, subnets, blocks, accounts, transfers.
        seed_value: Seed for server selection and for deterministic derive (trends, methods).
        count: Max items to fetch (capped to 50 by server).

    Returns:
        List of dicts with UI-aligned fields (subnet_name, rank, epoch, etc.).
    """
    limit = min(max(1, count), 50)
    backend_url = get_backend_service_url().rstrip("/")

    try:
        raw = await load_dataset_data(
            backend_url=backend_url,
            project_key=PROJECT_KEY,
            entity_type=entity_type,
            seed_value=seed_value,
            limit=limit,
        )
    except Exception as e:
        logger.debug("autostats_15 fetch_data failed for {}: {}", entity_type, e)
        return []

    if not raw:
        return []

    if entity_type == "validators":
        # Return server data as-is; VIEW_VALIDATOR event uses only server fields (no performanceTrend/subnetPerformance).
        return raw
    if entity_type == "subnets":
        return _add_trends_to_subnets(raw, seed_value)
    if entity_type == "blocks":
        normalized = [_normalize_block(b) for b in raw]
        return [_block_to_block_with_details(b) for b in normalized]
    if entity_type == "accounts":
        normalized = [_normalize_account(a) for a in raw]
        return [_account_to_account_with_details(a, i) for i, a in enumerate(normalized)]
    if entity_type == "transfers":
        normalized = [_normalize_transfer(t) for t in raw]
        # Return normalized only (block_number from blockNumber). No method/section - not in TRANSFER_COMPLETE event.
        return normalized

    return raw
