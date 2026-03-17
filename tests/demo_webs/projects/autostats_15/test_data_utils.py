"""Unit tests for autostats_15 data_utils (helpers + fetch_data with mocked backend)."""

from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.demo_webs.projects.autostats_15.data_utils import (
    _account_to_account_with_details,
    _add_trends_to_subnets,
    _block_to_block_with_details,
    _generate_trend_data,
    _normalize_account,
    _normalize_block,
    _normalize_transfer,
    _scale_large_number,
    _seed_random,
    fetch_data,
)


class TestSeedRandom:
    def test_deterministic(self):
        rng1 = _seed_random(42)
        rng2 = _seed_random(42)
        for _ in range(10):
            assert rng1() == rng2()

    def test_values_in_unit_interval(self):
        rng = _seed_random(123)
        for _ in range(100):
            x = rng()
            assert 0 <= x < 1

    def test_different_seeds_differ(self):
        rng_a = _seed_random(1)
        rng_b = _seed_random(2)
        assert rng_a() != rng_b()


class TestGenerateTrendData:
    def test_length(self):
        data = _generate_trend_data(7, 1, "neutral")
        assert len(data) == 7

    def test_values_in_range(self):
        data = _generate_trend_data(30, 1, "neutral")
        assert all(0 <= x <= 100 for x in data)

    def test_deterministic_for_same_seed_trend(self):
        a = _generate_trend_data(10, 5, "up")
        b = _generate_trend_data(10, 5, "up")
        assert a == b

    @pytest.mark.parametrize("trend", ["up", "down", "neutral"])
    def test_trend_param_accepted(self, trend):
        data = _generate_trend_data(5, 1, trend)
        assert len(data) == 5


class TestNormalizeBlock:
    def test_adds_extrinsics_if_missing(self):
        raw = {"number": 100}
        out = _normalize_block(raw)
        assert out["extrinsics"] == []
        assert raw.get("extrinsics") is None

    def test_keeps_existing_extrinsics(self):
        raw = {"number": 100, "extrinsics": [{"id": 1}]}
        out = _normalize_block(raw)
        assert out["extrinsics"] == [{"id": 1}]

    def test_does_not_mutate_input(self):
        raw = {"number": 100}
        _normalize_block(raw)
        assert "extrinsics" not in raw


class TestNormalizeAccount:
    def test_adds_delegations_and_transactions_if_missing(self):
        raw = {"address": "0x1"}
        out = _normalize_account(raw)
        assert out["delegations"] == []
        assert out["transactions"] == []
        assert out["balance"] == 0
        assert out["stakedAmount"] == 0

    def test_balance_staked_default_zero_when_none(self):
        raw = {"balance": None, "stakedAmount": None}
        out = _normalize_account(raw)
        assert out["balance"] == 0
        assert out["stakedAmount"] == 0

    def test_preserves_balance_and_staked_when_set(self):
        raw = {"balance": 100, "stakedAmount": 50}
        out = _normalize_account(raw)
        assert out["balance"] == 100
        assert out["stakedAmount"] == 50

    def test_does_not_mutate_input(self):
        raw = {"address": "0x1"}
        _normalize_account(raw)
        assert "delegations" not in raw
        assert "transactions" not in raw


class TestNormalizeTransfer:
    def test_adds_block_number_from_block_number(self):
        raw = {"hash": "0xabc", "blockNumber": 12345}
        out = _normalize_transfer(raw)
        assert out["block_number"] == 12345
        assert out["hash"] == "0xabc"

    def test_does_not_overwrite_existing_block_number(self):
        raw = {"blockNumber": 100, "block_number": 99}
        out = _normalize_transfer(raw)
        assert out["block_number"] == 99

    def test_no_block_number_when_block_number_absent(self):
        raw = {"hash": "0x"}
        out = _normalize_transfer(raw)
        assert "block_number" not in out


class TestAddTrendsToSubnets:
    def test_empty_list(self):
        assert _add_trends_to_subnets([], 1) == []

    def test_subnet_name_from_name(self):
        subnets = [{"id": 1, "name": "My Subnet"}]
        out = _add_trends_to_subnets(subnets, 42)
        assert len(out) == 1
        assert out[0]["subnet_name"] == "My Subnet"
        assert out[0]["subnet_id"] == 1

    def test_root_has_price_one(self):
        subnets = [{"id": 0, "name": "Root"}]
        out = _add_trends_to_subnets(subnets, 99)
        assert out[0]["price"] == 1.0

    def test_root_has_large_market_cap_and_volume(self):
        subnets = [{"id": 0, "name": "Root"}]
        out = _add_trends_to_subnets(subnets, 99)
        # M-scaled, 2 decimals: 50M to 100M → 50.0 to 100.0, 5M to 10M → 5.0 to 10.0
        assert out[0]["marketCap"] >= 50.0
        assert out[0]["volume24h"] >= 5.0

    def test_non_root_has_derived_price_and_caps(self):
        subnets = [{"id": 5, "name": "Other"}]
        out = _add_trends_to_subnets(subnets, 10)
        assert "price" in out[0]
        assert "marketCap" in out[0]
        assert "volume24h" in out[0]
        assert "trendData" in out[0]
        assert len(out[0]["trendData"]) == 7

    def test_scale_large_number_b_m_k(self):
        """_scale_large_number matches UI: >=1e9→B, >=1e6→M, >=1e3→K, else as-is; 2 decimals."""
        assert _scale_large_number(2_500_000_000) == 2.5
        assert _scale_large_number(1_000_000_000) == 1.0
        assert _scale_large_number(50_000_000) == 50.0
        assert _scale_large_number(1_500_000) == 1.5
        assert _scale_large_number(5_000) == 5.0
        assert _scale_large_number(999) == 999.0
        assert _scale_large_number(100.5) == 100.5

    def test_m_normalized_fields_match_ui_two_decimals(self):
        """emission always M; marketCap/volume24h use B/M/K by magnitude; all 2 decimals."""
        subnets = [
            {"id": 0, "name": "Root", "emission": 38_551.84},
            {"id": 3, "name": "Compute", "emission": 950_725.02},
        ]
        out = _add_trends_to_subnets(subnets, 99)
        assert len(out) == 2
        assert out[0]["emission"] == 0.04
        assert out[1]["emission"] == 0.95
        assert out[0]["marketCap"] == round(out[0]["marketCap"], 2)
        assert out[0]["volume24h"] == round(out[0]["volume24h"], 2)

    def test_emission_zero_when_missing(self):
        subnets = [{"id": 1, "name": "NoEmission"}]
        out = _add_trends_to_subnets(subnets, 0)
        assert out[0]["emission"] == 0.0

    def test_deterministic_for_same_seed(self):
        subnets = [{"id": 3, "name": "X"}]
        a = _add_trends_to_subnets(subnets, 7)
        b = _add_trends_to_subnets(subnets, 7)
        assert a[0]["price"] == b[0]["price"]
        assert a[0]["trendData"] == b[0]["trendData"]


class TestBlockToBlockWithDetails:
    def test_epoch_from_number(self):
        block = {"number": 720, "extrinsics": []}
        out = _block_to_block_with_details(block)
        assert out["epoch"] == 720 // 360

    def test_extrinsics_count_and_events_count(self):
        block = {"number": 100, "extrinsics": [1, 2, 3]}
        out = _block_to_block_with_details(block)
        assert out["extrinsicsCount"] == 3
        assert out["eventsCount"] == 6

    def test_setdefault_does_not_overwrite(self):
        block = {"number": 100, "extrinsics": [], "extrinsicsCount": 10, "eventsCount": 20}
        out = _block_to_block_with_details(block)
        assert out["extrinsicsCount"] == 10
        assert out["eventsCount"] == 20

    def test_number_defaults_to_zero_for_epoch(self):
        block = {}
        out = _block_to_block_with_details(block)
        assert out["epoch"] == 0


class TestAccountToAccountWithDetails:
    def test_rank_is_index_plus_one(self):
        account = {"balance": 0, "stakedAmount": 0}
        out = _account_to_account_with_details(account, 2)
        assert out["rank"] == 3

    def test_account_type_validator(self):
        account = {"balance": 0, "stakedAmount": 150000}
        out = _account_to_account_with_details(account, 0)
        assert out["accountType"] == "validator"

    def test_account_type_nominator(self):
        account = {"balance": 0, "stakedAmount": 15000}
        out = _account_to_account_with_details(account, 0)
        assert out["accountType"] == "nominator"

    def test_account_type_regular(self):
        account = {"balance": 1000, "stakedAmount": 0}
        out = _account_to_account_with_details(account, 0)
        assert out["accountType"] == "regular"

    def test_staking_ratio(self):
        account = {"balance": 100, "stakedAmount": 100}
        out = _account_to_account_with_details(account, 0)
        assert out["stakingRatio"] == 50.0
        assert out["totalValue"] == 200

    def test_staking_ratio_zero_when_no_value(self):
        account = {"balance": 0, "stakedAmount": 0}
        out = _account_to_account_with_details(account, 0)
        assert out["stakingRatio"] == 0.0

    def test_first_seen_last_active_from_transactions(self):
        account = {
            "balance": 0,
            "stakedAmount": 0,
            "transactions": [{"timestamp": "2024-01-01T00:00:00Z"}],
        }
        out = _account_to_account_with_details(account, 0)
        assert out["firstSeen"] == "2024-01-01T00:00:00Z"
        assert out["lastActive"] == "2024-01-01T00:00:00Z"

    def test_balance_change_24h_zero(self):
        account = {"balance": 0, "stakedAmount": 0}
        out = _account_to_account_with_details(account, 0)
        assert out["balanceChange24h"] == 0

    def test_balance_trend_present(self):
        account = {"balance": 0, "stakedAmount": 0}
        out = _account_to_account_with_details(account, 0)
        assert "balanceTrend" in out
        assert len(out["balanceTrend"]) == 30


_MODULE = "autoppia_iwa.src.demo_webs.projects.autostats_15.data_utils"


@pytest.mark.asyncio
class TestFetchData:
    """fetch_data with mocked get_backend_service_url and load_dataset_data."""

    async def test_validators_returns_raw(self):
        raw = [{"hotkey": "0xabc", "rank": 1}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("validators", 1, count=10)
        assert result == raw

    async def test_subnets_returns_with_trends(self):
        raw = [{"id": 1, "name": "Sub1"}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("subnets", 42, count=10)
        assert len(result) == 1
        assert result[0]["subnet_name"] == "Sub1"
        assert "price" in result[0]
        assert "trendData" in result[0]

    async def test_blocks_returns_normalized_with_details(self):
        raw = [{"number": 720, "extrinsics": [1, 2]}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("blocks", 1, count=10)
        assert len(result) == 1
        assert result[0]["epoch"] == 2
        assert result[0]["extrinsicsCount"] == 2
        assert result[0]["eventsCount"] == 4

    async def test_accounts_returns_normalized_with_details(self):
        raw = [{"balance": 100, "stakedAmount": 50}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("accounts", 1, count=10)
        assert len(result) == 1
        assert result[0]["rank"] == 1
        assert result[0]["accountType"] == "regular"
        assert "balanceTrend" in result[0]

    async def test_transfers_returns_normalized_only(self):
        raw = [{"hash": "0x1", "blockNumber": 100}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("transfers", 1, count=10)
        assert len(result) == 1
        assert result[0]["block_number"] == 100
        assert "method" not in result[0]

    async def test_unknown_entity_returns_raw(self):
        raw = [{"foo": "bar"}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw):
            result = await fetch_data("other", 1, count=10)
        assert result == raw

    async def test_empty_raw_returns_empty_list(self):
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=[]):
            result = await fetch_data("validators", 1, count=10)
        assert result == []

    async def test_exception_returns_empty_list(self):
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, side_effect=RuntimeError("network")):
            result = await fetch_data("validators", 1, count=10)
        assert result == []

    async def test_limit_capped_and_passed_to_load_dataset(self):
        raw = [{"hotkey": "x"}]
        with patch(f"{_MODULE}.get_backend_service_url", return_value="http://test/"), patch(f"{_MODULE}.load_dataset_data", new_callable=AsyncMock, return_value=raw) as mock_load:
            await fetch_data("validators", 1, count=0)
            mock_load.assert_awaited_once()
            assert mock_load.call_args.kwargs["limit"] == 1
            mock_load.reset_mock()
            await fetch_data("validators", 1, count=100)
            assert mock_load.call_args.kwargs["limit"] == 50
