"""Unit tests for demo_webs.projects.criterion_helper (validate_criterion)."""

from autoppia_iwa.src.demo_webs.projects.criterion_helper import (
    ComparisonOperator,
    CriterionValue,
    validate_criterion,
)


class TestValidateCriterionPlainValue:
    """When criterion is not a CriterionValue."""

    def test_bool_exact(self):
        assert validate_criterion(True, True) is True
        assert validate_criterion(False, False) is True
        assert validate_criterion(True, False) is False

    def test_str_contains_normalized(self):
        assert validate_criterion("Hello, World.", "world") is True
        assert validate_criterion("Hello World", "foo") is False

    def test_equality(self):
        assert validate_criterion(42, 42) is True
        assert validate_criterion(42, 43) is False


class TestValidateCriterionEquals:
    def test_string_normalized(self):
        c = CriterionValue(value="Alice", operator=ComparisonOperator.EQUALS)
        assert validate_criterion("alice", c) is True
        assert validate_criterion("ALICE.", c) is True
        assert validate_criterion("Bob", c) is False

    def test_numeric(self):
        c = CriterionValue(value=10, operator=ComparisonOperator.EQUALS)
        assert validate_criterion(10, c) is True
        assert validate_criterion(11, c) is False


class TestValidateCriterionNotEquals:
    def test_string_normalized(self):
        c = CriterionValue(value="x", operator=ComparisonOperator.NOT_EQUALS)
        assert validate_criterion("y", c) is True
        assert validate_criterion("x", c) is False


class TestValidateCriterionContains:
    def test_str_in_str(self):
        c = CriterionValue(value="bar", operator=ComparisonOperator.CONTAINS)
        assert validate_criterion("foobarbaz", c) is True
        assert validate_criterion("foobaz", c) is False

    def test_str_in_list_item(self):
        c = CriterionValue(value="a", operator=ComparisonOperator.CONTAINS)
        assert validate_criterion(["a", "b"], c) is True
        assert validate_criterion(["b", "c"], c) is False

    def test_non_str_returns_false(self):
        c = CriterionValue(value="x", operator=ComparisonOperator.CONTAINS)
        assert validate_criterion(123, c) is False


class TestValidateCriterionNotContains:
    def test_str_not_in_str(self):
        c = CriterionValue(value="x", operator=ComparisonOperator.NOT_CONTAINS)
        assert validate_criterion("abc", c) is True
        assert validate_criterion("abx", c) is False

    def test_not_contains_list(self):
        """Covers line 72: NOT_CONTAINS when actual_value is a list."""
        c = CriterionValue(value="x", operator=ComparisonOperator.NOT_CONTAINS)
        assert validate_criterion(["a", "b"], c) is True
        assert validate_criterion(["a", "x"], c) is False


class TestValidateCriterionNumeric:
    def test_greater_than(self):
        c = CriterionValue(value=10, operator=ComparisonOperator.GREATER_THAN)
        assert validate_criterion(11, c) is True
        assert validate_criterion(10, c) is False
        assert validate_criterion(None, c) is False

    def test_less_than(self):
        c = CriterionValue(value=10, operator=ComparisonOperator.LESS_THAN)
        assert validate_criterion(9, c) is True
        assert validate_criterion(10, c) is False

    def test_greater_equal(self):
        c = CriterionValue(value=10, operator=ComparisonOperator.GREATER_EQUAL)
        assert validate_criterion(10, c) is True
        assert validate_criterion(11, c) is True
        assert validate_criterion(9, c) is False

    def test_less_equal(self):
        c = CriterionValue(value=10, operator=ComparisonOperator.LESS_EQUAL)
        assert validate_criterion(10, c) is True
        assert validate_criterion(9, c) is True
        assert validate_criterion(11, c) is False


class TestValidateCriterionInList:
    def test_in_list_str_normalized(self):
        c = CriterionValue(value=["a", "b"], operator=ComparisonOperator.IN_LIST)
        assert validate_criterion("a", c) is True
        assert validate_criterion("A.", c) is True
        assert validate_criterion("c", c) is False

    def test_in_list_bool(self):
        c = CriterionValue(value=[True, False], operator=ComparisonOperator.IN_LIST)
        assert validate_criterion(True, c) is True
        assert validate_criterion(False, c) is True

    def test_none_returns_false(self):
        c = CriterionValue(value=["a"], operator=ComparisonOperator.IN_LIST)
        assert validate_criterion(None, c) is False

    def test_in_list_value_contains_bool(self):
        """Covers line 99: IN_LIST when criterion value list contains a bool."""
        c = CriterionValue(value=[1, True, "x"], operator=ComparisonOperator.IN_LIST)
        assert validate_criterion(1, c) is True
        assert validate_criterion(True, c) is True


class TestValidateCriterionNotInList:
    def test_not_in_list(self):
        c = CriterionValue(value=["a", "b"], operator=ComparisonOperator.NOT_IN_LIST)
        assert validate_criterion("c", c) is True
        assert validate_criterion("a", c) is False

    def test_not_in_list_bool(self):
        """Covers lines 103, 106: NOT_IN_LIST when actual_value is bool or value contains bool."""
        c = CriterionValue(value=[True, False], operator=ComparisonOperator.NOT_IN_LIST)
        assert validate_criterion(True, c) is False
        c2 = CriterionValue(value=[1, False, "x"], operator=ComparisonOperator.NOT_IN_LIST)
        assert validate_criterion(2, c2) is True

    def test_not_in_list_str_normalized(self):
        """Covers line 108: NOT_IN_LIST with str and normalized comparison."""
        c = CriterionValue(value=["a", "b"], operator=ComparisonOperator.NOT_IN_LIST)
        assert validate_criterion("A.", c) is False
        assert validate_criterion("c", c) is True
