"""Tests for autocinema_1 utils (constraint parsing and formatting)."""

from unittest.mock import patch

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p01_autocinema import utils as autocinema_utils


class TestParseConstraintsStr:
    def test_empty_returns_empty_list(self):
        assert autocinema_utils.parse_constraints_str("") == []

    def test_single_constraint_year(self):
        result = autocinema_utils.parse_constraints_str("1) year equals 2014")
        assert len(result) == 1
        assert result[0]["field"] == "year"
        assert result[0]["operator"] == ComparisonOperator.EQUALS
        assert result[0]["value"] == 2014

    def test_single_constraint_duration(self):
        result = autocinema_utils.parse_constraints_str("1) duration greater_than 90")
        assert len(result) == 1
        assert result[0]["field"] == "duration"
        assert result[0]["value"] == 90

    def test_single_constraint_rating(self):
        result = autocinema_utils.parse_constraints_str("1) rating equals 4.5")
        assert len(result) == 1
        assert result[0]["field"] == "rating"
        assert result[0]["value"] == 4.5

    def test_single_constraint_genres_single(self):
        result = autocinema_utils.parse_constraints_str("1) genres contains Sci-Fi")
        assert len(result) == 1
        assert result[0]["field"] == "genres"
        assert result[0]["value"] == "Sci-Fi"

    def test_genres_list_format(self):
        result = autocinema_utils.parse_constraints_str("1) genres in_list [Action, Sci-Fi]")
        assert len(result) == 1
        assert result[0]["field"] == "genres"
        assert result[0]["value"] == ["Action", "Sci-Fi"]

    def test_multiple_constraints_and(self):
        result = autocinema_utils.parse_constraints_str("1) year equals 2014 AND 2) genres contains Sci-Fi")
        assert len(result) == 2
        assert result[0]["field"] == "year" and result[0]["value"] == 2014
        assert result[1]["field"] == "genres" and result[1]["value"] == "Sci-Fi"

    def test_other_field_returns_string_value(self):
        result = autocinema_utils.parse_constraints_str("1) name equals Inception")
        assert len(result) == 1
        assert result[0]["field"] == "name"
        assert result[0]["value"] == "Inception"


class TestBuildConstraintsInfo:
    def test_returns_none_when_max_attempts_exhausted(self):
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p01_autocinema.utils.constraints_exist_in_db", return_value=False),
            patch(
                "autoppia_iwa.src.demo_webs.projects.p01_autocinema.generation_functions.generate_constraint_from_solution",
                return_value={"field": "year", "operator": ComparisonOperator.EQUALS, "value": 2014},
            ),
            patch("random.choice", side_effect=[{"year": 2014}, "equals"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["year"]),
        ):
            result = autocinema_utils.build_constraints_info([{"year": 2014}], max_attempts=1)
        assert result is None

    def test_returns_string_when_constraints_valid(self):
        data = [{"year": 2014, "name": "A"}, {"year": 2015, "name": "B"}]
        with (
            patch("autoppia_iwa.src.demo_webs.projects.p01_autocinema.utils.constraints_exist_in_db", return_value=True),
            patch("autoppia_iwa.src.demo_webs.projects.p01_autocinema.generation_functions.generate_constraint_from_solution") as gen,
            patch("random.choice", side_effect=[data[0], "equals"]),
            patch("random.randint", return_value=1),
            patch("random.sample", return_value=["year"]),
        ):
            gen.return_value = {"field": "year", "operator": ComparisonOperator.EQUALS, "value": 2014}
            result = autocinema_utils.build_constraints_info(data, max_attempts=10)
        assert result is not None
        assert "year" in result
        assert "2014" in result
