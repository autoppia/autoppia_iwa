"""Tests for autozone_3 utils (build_constraints_info)."""

from unittest.mock import patch

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p03_autozone import utils as autozone_utils


class TestBuildConstraintsInfo:
    """Tests for build_constraints_info."""

    def test_returns_none_when_max_attempts_exhausted(self):
        data = [{"title": "Widget", "brand": "Acme", "category": "Tools", "rating": 4.5, "price": 19.99}]
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p03_autozone.utils.constraints_exist_in_db", return_value=False),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.generation_functions.generate_constraint_value",
                return_value={"field": "title", "operator": ComparisonOperator.EQUALS, "value": "Widget"},
            ),
            patch("random.choice", side_effect=[data[0], "equals"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["title"]),
        ):
            result = autozone_utils.build_constraints_info(data, max_attempts=1)
        assert result is None

    def test_returns_string_when_constraints_valid_scalar_value(self):
        data = [
            {"title": "Widget", "brand": "Acme", "category": "Tools", "rating": 4.5, "price": 19.99},
            {"title": "Gadget", "brand": "Acme", "category": "Tools", "rating": 4.0, "price": 29.99},
        ]
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p03_autozone.utils.constraints_exist_in_db", return_value=True),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.generation_functions.generate_constraint_value",
                return_value={"field": "title", "operator": ComparisonOperator.EQUALS, "value": "Widget"},
            ),
            patch("random.choice", side_effect=[data[0], "equals"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["title"]),
        ):
            result = autozone_utils.build_constraints_info(data, max_attempts=10)
        assert result is not None
        assert "title" in result
        assert "Widget" in result
        assert "equals" in result

    def test_returns_string_with_list_value_formatting(self):
        """Covers the branch where constraint value is a list (v_str with brackets)."""
        data = [
            {"title": "Widget", "brand": "Acme", "category": "Tools", "rating": 4.5, "price": 19.99},
        ]
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p03_autozone.utils.constraints_exist_in_db", return_value=True),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.generation_functions.generate_constraint_value",
                return_value={"field": "category", "operator": ComparisonOperator.IN_LIST, "value": ["Tools", "Parts"]},
            ),
            patch("random.choice", side_effect=[data[0], "in_list"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["category"]),
        ):
            result = autozone_utils.build_constraints_info(data, max_attempts=10)
        assert result is not None
        assert "category" in result
        assert "[Tools, Parts]" in result or "Tools" in result

    def test_skips_empty_constraint_from_generator(self):
        """When generate_constraint_value returns None/falsy, that constraint is not appended."""
        data = [{"title": "Widget", "brand": "Acme", "category": "Tools", "rating": 4.5, "price": 19.99}]
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p03_autozone.utils.constraints_exist_in_db", return_value=True),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.generation_functions.generate_constraint_value",
                return_value=None,
            ),
            patch("random.choice", side_effect=[data[0], "equals"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["title"]),
        ):
            result = autozone_utils.build_constraints_info(data, max_attempts=1)
        # constraint_list is empty so constraints_exist_in_db(..., []) is False -> no valid constraints -> None
        assert result is None

    def test_recursion_when_first_attempt_fails_then_succeeds(self):
        """When constraints_exist_in_db is False then True, second attempt returns string."""
        data = [
            {"title": "Widget", "brand": "Acme", "category": "Tools", "rating": 4.5, "price": 19.99},
        ]
        exist_side_effect = [False, True]
        # First call: choice(data), choice(operators), randint, sample; recursion. Second: same.
        choice_side_effect = [data[0], "equals", data[0], "equals"]
        sample_side_effect = [["title"], ["title"]]

        with (
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.utils.constraints_exist_in_db",
                side_effect=exist_side_effect,
            ),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p03_autozone.generation_functions.generate_constraint_value",
                return_value={"field": "title", "operator": ComparisonOperator.EQUALS, "value": "Widget"},
            ),
            patch("random.choice", side_effect=choice_side_effect),
            patch("random.randint", return_value=1),
            patch("random.sample", side_effect=sample_side_effect),
        ):
            result = autozone_utils.build_constraints_info(data, max_attempts=3)
        assert result is not None
        assert "title" in result
