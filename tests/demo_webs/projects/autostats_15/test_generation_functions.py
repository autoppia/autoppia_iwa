from __future__ import annotations

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p15_autostats import generation_functions as gf

SUBNETS = [
    {"subnet_name": "Subnet One", "name": "Subnet One", "emission": 10.5, "price": 2.5, "marketCap": 1000, "volume24h": 250},
    {"subnet_name": "Subnet Two", "name": "Subnet Two", "emission": 20.0, "price": 3.0, "marketCap": 1200, "volume24h": 500},
]
VALIDATORS = [
    {"hotkey": "val1", "rank": 1, "dominance": 12.5, "nominatorCount": 20, "totalWeight": 100, "rootStake": 50, "alphaStake": 30, "commission": 5},
    {"hotkey": "val2", "rank": 2, "dominance": 10.0, "nominatorCount": 10, "totalWeight": 90, "rootStake": 40, "alphaStake": 20, "commission": 4},
]
BLOCKS = [
    {"number": 101, "hash": "0xabc", "validator": "val1", "epoch": 7, "extrinsicsCount": 5, "eventsCount": 8},
    {"number": 102, "hash": "0xdef", "validator": "val2", "epoch": 8, "extrinsicsCount": 6, "eventsCount": 9},
]
ACCOUNTS = [
    {"rank": 1, "address": "addr1", "balance": 1000, "stakedAmount": 600, "stakingRatio": 0.6, "accountType": "validator"},
    {"rank": 2, "address": "addr2", "balance": 800, "stakedAmount": 300, "stakingRatio": 0.4, "accountType": "nominator"},
]
TRANSFERS = [
    {"hash": "0xaaa", "from_": "addr1", "to": "addr2", "amount": 10, "block_number": 100},
    {"hash": "0xbbb", "from_": "addr2", "to": "addr1", "amount": 20, "block_number": 101},
]


@pytest.fixture
def deterministic_random(monkeypatch: pytest.MonkeyPatch) -> None:
    def _choice(seq):
        if isinstance(seq, str):
            return seq[-1]
        return next(iter(seq))

    monkeypatch.setattr(gf.random, "choice", _choice)
    monkeypatch.setattr(gf.random, "sample", lambda population, k: list(population)[:k])
    monkeypatch.setattr(gf.random, "shuffle", lambda population: None)
    monkeypatch.setattr(gf.random, "randint", lambda a, b: b)
    monkeypatch.setattr(gf.random, "uniform", lambda a, b: b)


@pytest.fixture
def patched_entities(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_get_entity(task_url, dataset, entity_type):
        mapping = {
            "subnets": SUBNETS,
            "validators": VALIDATORS,
            "blocks": BLOCKS,
            "accounts": ACCOUNTS,
            "transfers": TRANSFERS,
        }
        return mapping[entity_type]

    monkeypatch.setattr(gf, "_get_autostats_entity_list", _fake_get_entity)


def test_build_wallet_dataset_and_float_safe():
    wallets = gf._build_wallet_dataset()
    assert wallets == [{"wallet_name": "Talisman"}, {"wallet_name": "SubWallet"}]
    assert gf._to_float_safe(3) == 3.0
    assert gf._to_float_safe("1,200") == 1200.0
    assert gf._to_float_safe("bad") is None


def test_generate_constraint_value_for_strings_and_numbers(deterministic_random):
    assert gf._generate_constraint_value(ComparisonOperator.EQUALS, "Subnet One", "subnet_name", SUBNETS) == "Subnet One"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Subnet One", "subnet_name", SUBNETS) == "Subnet Two"
    contains_value = gf._generate_constraint_value(ComparisonOperator.CONTAINS, "Subnet One", "subnet_name", SUBNETS)
    assert isinstance(contains_value, str)
    assert contains_value
    assert contains_value in "Subnet One"
    assert gf._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "Subnet One", "subnet_name", SUBNETS) == "Subnet Two"
    assert gf._generate_constraint_value(ComparisonOperator.GREATER_THAN, 10.5, "emission", SUBNETS) < 10.5
    assert gf._generate_constraint_value(ComparisonOperator.LESS_EQUAL, 10.5, "emission", SUBNETS) == 10.5


def test_generate_constraints_static(deterministic_random):
    constraints = gf._generate_constraints_static(
        VALIDATORS,
        gf.FIELD_OPERATORS_MAP_VIEW_VALIDATOR,
        gf.SELECTED_FIELDS_VIEW_VALIDATOR,
        num_constraints=2,
        integer_fields=gf.INTEGER_FIELDS_VIEW_VALIDATOR,
    )
    assert len(constraints) == 2
    assert all(c["field"] in gf.SELECTED_FIELDS_VIEW_VALIDATOR for c in constraints)


@pytest.mark.asyncio
async def test_view_generators(deterministic_random, patched_entities):
    subnet = await gf.generate_view_subnet_constraints("http://localhost/?seed=1")
    validator = await gf.generate_view_validator_constraints("http://localhost/?seed=1")
    block = await gf.generate_view_block_constraints("http://localhost/?seed=1")
    account = await gf.generate_view_account_constraints("http://localhost/?seed=1")
    assert len(subnet) == 2
    assert len(validator) == 2
    assert len(block) == 2
    assert len(account) == 2


@pytest.mark.asyncio
async def test_trade_transfer_and_favorite_generators(deterministic_random, patched_entities):
    buy = await gf.generate_execute_buy_constraints("http://localhost/?seed=1")
    sell = await gf.generate_execute_sell_constraints("http://localhost/?seed=1")
    transfer = await gf.generate_transfer_complete_constraints("http://localhost/?seed=1")
    favorite = await gf.generate_favorite_subnet_constraints("http://localhost/?seed=1")
    assert len(buy) == 2
    assert len(sell) == 2
    assert len(transfer) == 2
    assert len(favorite) == 1


def test_wallet_generators(deterministic_random):
    connect = gf.generate_connect_wallet_constraints()
    disconnect = gf.generate_disconnect_wallet_constraints()
    assert len(connect) == 1
    assert len(disconnect) == 1


@pytest.mark.asyncio
async def test_empty_entity_lists_return_empty(monkeypatch: pytest.MonkeyPatch):
    async def _empty_get_entity(task_url, dataset, entity_type):
        return []

    monkeypatch.setattr(gf, "_get_autostats_entity_list", _empty_get_entity)
    assert await gf.generate_view_subnet_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_view_validator_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_view_block_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_view_account_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_execute_buy_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_execute_sell_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_transfer_complete_constraints("http://localhost/?seed=1") == []
    assert await gf.generate_favorite_subnet_constraints("http://localhost/?seed=1") == []
