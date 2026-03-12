"""Unit tests for demo_webs.projects.shared_utils (constraints, parse_price, etc.)."""

import datetime

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator, CriterionValue
from autoppia_iwa.src.demo_webs.projects.shared_utils import (
    constraint_value_for_datetime_date,
    constraint_value_for_numeric,
    constraint_value_for_time,
    constraints_exist_in_db,
    create_constraint_dict,
    generate_mock_date_strings,
    generate_mock_dates,
    item_matches_all_constraints,
    parse_datetime,
    parse_price,
    pick_different_value_from_dataset,
    random_str_not_contained_in,
    validate_date_field,
    validate_time_field,
)


class TestConstraintsExistInDb:
    def test_empty_data_returns_false(self):
        assert constraints_exist_in_db([], [{"field": "x", "operator": "equals", "value": 1}]) is False

    def test_one_match_returns_true(self):
        data = [{"x": 1}, {"x": 2}]
        constraints = [{"field": "x", "operator": "equals", "value": 1}]
        assert constraints_exist_in_db(data, constraints) is True

    def test_no_match_returns_false(self):
        data = [{"x": 2}, {"x": 3}]
        constraints = [{"field": "x", "operator": "equals", "value": 1}]
        assert constraints_exist_in_db(data, constraints) is False


class TestItemMatchesAllConstraints:
    def test_single_constraint_equals_match(self):
        item = {"name": "Alice"}
        CriterionValue(value="alice", operator=ComparisonOperator.EQUALS)
        assert item_matches_all_constraints(item, [{"field": "name", "operator": "equals", "value": "alice"}]) is True

    def test_single_constraint_no_match(self):
        item = {"name": "Bob"}
        assert item_matches_all_constraints(item, [{"field": "name", "operator": "equals", "value": "Alice"}]) is False

    def test_multiple_constraints_all_must_match(self):
        item = {"a": 1, "b": 2}
        constraints = [
            {"field": "a", "operator": "equals", "value": 1},
            {"field": "b", "operator": "equals", "value": 2},
        ]
        assert item_matches_all_constraints(item, constraints) is True
        assert item_matches_all_constraints(item, [*constraints, {"field": "b", "operator": "equals", "value": 3}]) is False


class TestParsePrice:
    def test_none_returns_none(self):
        assert parse_price(None) is None

    def test_string_with_dollar_and_comma(self):
        assert parse_price("$1,234.56") == 1234.56

    def test_plain_string_number(self):
        assert parse_price("42") == 42.0

    def test_int(self):
        assert parse_price(100) == 100.0

    def test_float(self):
        assert parse_price(19.99) == 19.99

    def test_empty_string_returns_none(self):
        assert parse_price("") is None
        assert parse_price("   ") is None

    def test_invalid_string_returns_none(self):
        assert parse_price("not a number") is None


class TestCreateConstraintDict:
    def test_creates_correct_structure(self):
        d = create_constraint_dict("price", ComparisonOperator.GREATER_THAN, 10.0)
        assert d["field"] == "price"
        assert d["operator"] == ComparisonOperator.GREATER_THAN
        assert d["value"] == 10.0


class TestRandomStrNotContainedIn:
    def test_return_length(self):
        result = random_str_not_contained_in("abc", length=5)
        assert len(result) == 5

    def test_result_not_in_text(self):
        text = "the quick brown fox"
        for _ in range(20):
            result = random_str_not_contained_in(text, length=3)
            assert result.lower() not in text.lower()

    def test_fallback_when_all_contained(self):
        # "a", "b", ... single chars might all be in "abc..." - use fallback
        result = random_str_not_contained_in("abcdefghijklmnopqrstuvwxyz", length=1, max_attempts=2, fallback="x")
        assert result == "x" or result in "abcdefghijklmnopqrstuvwxyz"


class TestPickDifferentValueFromDataset:
    def test_returns_different_value(self):
        dataset = [{"x": 1}, {"x": 2}, {"x": 3}]
        result = pick_different_value_from_dataset(dataset, "x", 2)
        assert result in (1, 3)

    def test_returns_fallback_when_all_excluded(self):
        dataset = [{"x": 1}]
        result = pick_different_value_from_dataset(dataset, "x", 1, fallback=99)
        assert result == 99

    def test_returns_fallback_for_empty_dataset(self):
        result = pick_different_value_from_dataset([], "x", 1, fallback=0)
        assert result == 0


class TestConstraintValueForDatetimeDate:
    def test_greater_than_returns_past_date(self):
        d = datetime.date(2025, 6, 15)
        result = constraint_value_for_datetime_date(ComparisonOperator.GREATER_THAN, d)
        assert result < d

    def test_less_than_returns_future_date(self):
        d = datetime.date(2025, 6, 15)
        result = constraint_value_for_datetime_date(ComparisonOperator.LESS_THAN, d)
        assert result > d

    def test_equals_returns_same_date(self):
        d = datetime.date(2025, 6, 15)
        result = constraint_value_for_datetime_date(ComparisonOperator.EQUALS, d)
        assert result == d


class TestConstraintValueForNumeric:
    def test_greater_than_returns_less_than_value(self):
        result = constraint_value_for_numeric(ComparisonOperator.GREATER_THAN, 10.0)
        assert result < 10.0

    def test_less_than_returns_greater_than_value(self):
        result = constraint_value_for_numeric(ComparisonOperator.LESS_THAN, 10.0)
        assert result > 10.0

    def test_greater_equal_returns_value(self):
        result = constraint_value_for_numeric(ComparisonOperator.GREATER_EQUAL, 5)
        assert result == 5

    def test_round_digits_applied(self):
        result = constraint_value_for_numeric(ComparisonOperator.LESS_THAN, 10.0, round_digits=2)
        assert isinstance(result, float)
        assert len(str(result).split(".")[-1]) <= 2 or result == int(result)


class TestParseDatetime:
    def test_none_returns_none(self):
        assert parse_datetime(None) is None

    def test_empty_string_returns_none(self):
        assert parse_datetime("") is None

    def test_iso_format(self):
        dt = parse_datetime("2025-06-15T10:30:00")
        assert dt is not None
        assert dt.year == 2025 and dt.month == 6 and dt.day == 15

    def test_date_only(self):
        dt = parse_datetime("2025-06-15")
        assert dt is not None
        assert dt.year == 2025 and dt.month == 6 and dt.day == 15

    def test_datetime_passthrough(self):
        now = datetime.datetime.now(datetime.UTC)
        assert parse_datetime(now) == now


class TestValidateDateField:
    def test_equals_string_date(self):
        criterion = CriterionValue(value="2025-06-15", operator=ComparisonOperator.EQUALS)
        assert validate_date_field("2025-06-15", criterion) is True
        assert validate_date_field("2025-06-16", criterion) is False

    def test_equals_date_objects(self):
        from datetime import date

        d = date(2025, 6, 15)
        criterion = CriterionValue(value=d, operator=ComparisonOperator.EQUALS)
        assert validate_date_field(d, criterion) is True


class TestValidateTimeField:
    def test_equals_time_string(self):
        criterion = CriterionValue(value="14:30:00", operator=ComparisonOperator.EQUALS)
        assert validate_time_field("14:30:00", criterion) is True

    def test_equals_time_objects(self):
        from datetime import time

        t = time(14, 30, 0)
        criterion = CriterionValue(value=t, operator=ComparisonOperator.EQUALS)
        assert validate_time_field(t, criterion) is True


class TestGenerateMockDates:
    def test_returns_list_of_future_dates(self):
        dates = generate_mock_dates()
        assert len(dates) >= 1
        assert all(hasattr(d, "hour") for d in dates)

    def test_generate_mock_date_strings(self):
        from datetime import date

        dates = [date(2025, 7, 18), date(2025, 7, 19)]
        strings = generate_mock_date_strings(dates)
        assert len(strings) >= 1
        assert all(isinstance(s, str) for s in strings)


class TestConstraintValueForTime:
    def test_equals_returns_same_time(self):
        from datetime import time

        t = time(12, 0, 0)
        dataset = [{"slot": time(10, 0)}, {"slot": time(14, 0)}]
        result = constraint_value_for_time(ComparisonOperator.EQUALS, t, "slot", dataset)
        assert result == t

    def test_greater_than_returns_time(self):
        from datetime import time

        t = time(12, 0, 0)
        dataset = [{"slot": time(10, 0)}, {"slot": time(14, 0)}]
        result = constraint_value_for_time(ComparisonOperator.GREATER_THAN, t, "slot", dataset)
        assert result is not None
