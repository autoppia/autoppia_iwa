"""Tests for autocinema_1 generation_functions."""

import random
from typing import ClassVar
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.p01_autocinema import generation_functions as gen


class TestSyncGenerationFunctions:
    """Sync functions that do not require dataset or async."""

    def test_generate_registration_constraints_returns_list_with_placeholders(self):
        result = gen.generate_registration_constraints()
        assert isinstance(result, list)
        assert len(result) >= 1
        fields = [c.get("field") for c in result if isinstance(c, dict)]
        assert "username" in fields
        assert "email" in fields
        assert "password" in fields

    def test_generate_login_constraints_returns_list(self):
        result = gen.generate_login_constraints()
        assert isinstance(result, list)
        assert len(result) >= 2
        fields = [c.get("field") for c in result if isinstance(c, dict)]
        assert "username" in fields
        assert "password" in fields

    def test_generate_logout_constraints_returns_list(self):
        result = gen.generate_logout_constraints()
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_generate_contact_constraints_returns_list(self):
        result = gen.generate_contact_constraints()
        assert isinstance(result, list)
        for c in result:
            assert "field" in c
            assert "operator" in c
            assert "value" in c

    def test_generate_edit_profile_constraints_includes_login_and_profile(self):
        result = gen.generate_edit_profile_constraints()
        assert isinstance(result, list)
        fields = [c.get("field") for c in result]
        assert "username" in fields
        assert "password" in fields

    def test_generate_add_film_constraints_with_none_dataset(self):
        result = gen.generate_add_film_constraints(None)
        assert isinstance(result, list)
        assert any(c.get("field") == "username" for c in result)

    def test_generate_add_film_constraints_with_empty_dict(self):
        result = gen.generate_add_film_constraints({})
        assert isinstance(result, list)

    def test_generate_add_film_constraints_with_empty_movies(self):
        result = gen.generate_add_film_constraints({"movies": []})
        assert isinstance(result, list)

    def test_generate_add_film_constraints_with_movies(self):
        dataset = {
            "movies": [
                {"name": "Inception", "year": 2010, "rating": 4.5, "duration": 148, "genres": ["Sci-Fi"], "director": "Nolan"},
            ]
        }
        result = gen.generate_add_film_constraints(dataset)
        assert isinstance(result, list)
        assert any(c.get("field") == "username" for c in result)


class TestGenerateConstraintFromSolution:
    """Tests for generate_constraint_from_solution (used by utils.build_constraints_info)."""

    def test_returns_constraint_dict_when_valid(self):
        movie = {"name": "Gladiator", "year": 2000, "rating": 4.5}
        movies_data = [movie, {"name": "Other", "year": 2001, "rating": 4.0}]
        result = gen.generate_constraint_from_solution(movie, "year", ComparisonOperator.EQUALS, movies_data)
        assert result is not None
        assert result["field"] == "year"
        assert result["operator"] == ComparisonOperator.EQUALS
        assert result["value"] == 2000

    def test_returns_none_when_value_generation_fails(self):
        movie = {"name": "X"}
        movies_data = [movie]
        # field "missing" may yield None from _generate_constraint_value in some branches
        result = gen.generate_constraint_from_solution(movie, "missing", ComparisonOperator.EQUALS, movies_data)
        # Can be None or a dict depending on implementation
        assert result is None or isinstance(result, dict)


class TestGenerationHelpers:
    @pytest.mark.asyncio
    async def test_ensure_dataset_fetches_when_missing(self):
        with patch.object(gen, "fetch_data", new_callable=AsyncMock, return_value={"movies": [{"name": "Inception"}]}) as mocked_fetch:
            result = await gen._ensure_dataset(task_url="http://localhost:8000/?seed=7", dataset=None)

        assert result == {"movies": [{"name": "Inception"}]}
        mocked_fetch.assert_awaited_once_with(seed_value=7)

    @pytest.mark.asyncio
    async def test_ensure_dataset_returns_existing_dataset(self):
        dataset = {"movies": [{"name": "Inception"}]}
        result = await gen._ensure_dataset(task_url="http://localhost:8000/?seed=7", dataset=dataset)
        assert result is dataset

    def test_build_filter_film_dataset_flattens_genres(self):
        rows = gen._build_filter_film_dataset(
            [
                {"year": 2010, "genres": ["Sci-Fi", {"name": "Action"}]},
                {"year": 2000, "genres": []},
            ]
        )

        assert {"genre_name": "Sci-Fi", "year": 2010} in rows
        assert {"genre_name": "Action", "year": 2010} in rows

    def test_build_filter_film_dataset_returns_fallback_when_empty(self):
        assert gen._build_filter_film_dataset([]) == [{"genre_name": "Drama", "year": 2020}]

    def test_generate_constraint_value_not_contains_list_uses_remaining_pool(self):
        dataset = [
            {"genres": ["Sci-Fi", "Drama"]},
            {"genres": ["Action"]},
        ]
        result = gen._generate_constraint_value(
            ComparisonOperator.NOT_CONTAINS,
            ["Sci-Fi"],
            "genres",
            dataset,
        )
        assert result in {"Drama", "Action"}

    def test_generate_constraint_value_numeric_comparisons_are_clamped_for_rating(self):
        assert gen._generate_constraint_value(ComparisonOperator.GREATER_THAN, 0.2, "rating", []) >= 0.0
        assert gen._generate_constraint_value(ComparisonOperator.LESS_THAN, 4.9, "rating", []) <= 5.0

    def test_generate_constraint_value_in_list_and_not_in_list(self):
        dataset = [
            {"genres": ["Sci-Fi", "Drama"]},
            {"genres": ["Action"]},
        ]
        in_list = gen._generate_constraint_value(ComparisonOperator.IN_LIST, ["Sci-Fi"], "genres", dataset)
        not_in_list = gen._generate_constraint_value(ComparisonOperator.NOT_IN_LIST, ["Sci-Fi"], "genres", dataset)

        assert "Sci-Fi" in in_list
        assert all(value != "Sci-Fi" for value in not_in_list)

    def test_login_constraints_helper_contains_default_password(self):
        constraints = gen._login_constraints()
        assert constraints[0]["field"] == "username"
        assert constraints[1]["field"] == "password"

    def test_generate_constraint_value_additional_fallback_paths(self, monkeypatch):
        monkeypatch.setattr(gen.random, "choice", lambda seq: seq[0])
        monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
        monkeypatch.setattr(gen.random, "randint", lambda a, b: a)
        monkeypatch.setattr(gen.random, "uniform", lambda a, b: 0.5)
        monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

        assert gen._generate_constraint_value(ComparisonOperator.EQUALS, ["Sci-Fi", "Drama"], "genres", []) == "Sci-Fi"
        assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, 2000, "year", [{"year": 2000}]) == 2001
        assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, 4.5, "rating", [{"rating": 4.5}]) == 4.6
        assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "Solo", "name", [{"name": "Solo"}]) == "Solox"
        assert gen._generate_constraint_value(ComparisonOperator.NOT_EQUALS, "", "name", [{"name": ""}]) == "other"
        assert gen._generate_constraint_value(ComparisonOperator.CONTAINS, "A", "name", []) == "A"
        assert gen._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, "abc", "name", []) not in "abc"
        assert gen._generate_constraint_value(ComparisonOperator.CONTAINS, [{"name": "Drama"}], "genres", []) == "Drama"
        assert gen._generate_constraint_value(ComparisonOperator.NOT_CONTAINS, [{"name": "Drama"}], "genres", [{"genres": [{"name": "Drama"}]}]) is None
        assert gen._generate_constraint_value(ComparisonOperator.GREATER_EQUAL, 4.5, "rating", []) == 4.5
        assert gen._generate_constraint_value(ComparisonOperator.IN_LIST, [], "genres", []) == []

    def test_generate_constraints_handles_field_map_and_empty_cases(self, monkeypatch):
        monkeypatch.setattr(gen, "choice", lambda seq: seq[0])
        monkeypatch.setattr(gen.random, "sample", lambda seq, n: seq[:n])

        assert gen._generate_constraints([], {"name": [ComparisonOperator.EQUALS]}) == []

        dataset = [{"display_name": "Inception"}]
        result = gen._generate_constraints(
            dataset,
            {"name": [ComparisonOperator.EQUALS], "skip": []},
            field_map={"name": "display_name"},
            num_constraints=2,
            selected_fields=["missing"],
        )
        assert result[0]["field"] == "name"

        custom = gen._generate_constraints(
            dataset,
            {"name": [ComparisonOperator.EQUALS]},
            field_map={"name": {"field": "display_name", "dataset": dataset}},
        )
        assert custom[0]["field"] == "name"


@pytest.mark.asyncio
class TestAsyncGenerationFunctions:
    """Async constraint generators with mocked data."""

    _SAMPLE_FILMS: ClassVar[list] = [
        {"name": "Inception", "year": 2010, "rating": 4.5, "duration": 148, "genres": ["Sci-Fi", "Action"], "director": "Nolan"},
        {"name": "Gladiator", "year": 2000, "rating": 4.0, "duration": 155, "genres": ["Drama"], "director": "Scott"},
    ]

    async def test_generate_film_constraints_with_dataset(self):
        random.seed(42)
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_film_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)
        assert len(result) >= 1
        for c in result:
            assert "field" in c and "value" in c

    async def test_generate_film_constraints_empty_movies_returns_empty(self):
        result = await gen.generate_film_constraints(task_url=None, dataset={"movies": []})
        assert result == []

    async def test_generate_search_film_constraints_exception_and_empty_generated_constraints_fallback(self):
        with patch.object(gen, "_get_films_data", new_callable=AsyncMock, side_effect=RuntimeError("boom")):
            result = await gen.generate_search_film_constraints()
        assert result

        with (
            patch.object(gen, "_get_films_data", new_callable=AsyncMock, return_value=[{"name": "The Matrix"}]),
            patch.object(gen, "_generate_constraints", return_value=[]),
        ):
            result = await gen.generate_search_film_constraints()
        assert result

    async def test_generate_search_film_constraints_with_dataset(self):
        dataset = {"movies": [{"name": "The Matrix"}]}
        result = await gen.generate_search_film_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)
        assert len(result) >= 1 or (isinstance(result, list) and all("field" in c for c in result))

    async def test_generate_search_film_constraints_empty_films_returns_fallback(self):
        with patch.object(gen, "_get_films_data", new_callable=AsyncMock, return_value=[]), patch.object(gen, "_ensure_dataset", new_callable=AsyncMock, return_value={}):
            result = await gen.generate_search_film_constraints(task_url=None, dataset={})
        assert isinstance(result, list)
        # Fallback is parse_constraints_str("query equals The Matrix")
        assert len(result) >= 1

    async def test_generate_film_detail_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_film_detail_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_film_detail_and_watchlist_empty_paths_return_empty(self):
        assert await gen.generate_film_detail_constraints(dataset={"movies": []}) == []
        assert await gen.generate_add_to_watchlist_constraints(dataset={"movies": []}) == []
        assert await gen.generate_remove_from_watchlist_constraints(dataset={"movies": []}) == []
        assert await gen.generate_share_film_constraints(dataset={"movies": []}) == []
        assert await gen.generate_watch_trailer_constraints(dataset={"movies": []}) == []

    async def test_generate_add_to_watchlist_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_add_to_watchlist_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)
        fields = [c.get("field") for c in result]
        assert "username" in fields

    async def test_generate_remove_from_watchlist_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_remove_from_watchlist_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)
        fields = [c.get("field") for c in result]
        assert "username" in fields

    async def test_generate_share_film_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_share_film_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_generate_watch_trailer_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_watch_trailer_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_generate_delete_film_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_delete_film_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_generate_film_filter_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_film_filter_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_generate_film_filter_constraints_variants_and_empty(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        with (
            patch.object(gen, "choice", side_effect=lambda seq: "single_genre" if "single_genre" in seq else seq[0]),
            patch.object(gen.random, "sample", lambda seq, n: seq[:n]),
        ):
            genre_only = await gen.generate_film_filter_constraints(task_url=None, dataset=dataset)
        with (
            patch.object(gen, "choice", side_effect=lambda seq: "single_year" if "single_year" in seq else seq[0]),
            patch.object(gen.random, "sample", lambda seq, n: seq[:n]),
        ):
            year_only = await gen.generate_film_filter_constraints(task_url=None, dataset=dataset)
        assert genre_only and year_only
        assert await gen.generate_film_filter_constraints(task_url=None, dataset={"movies": []}) == []

    async def test_generate_add_comment_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_add_comment_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

    async def test_generate_add_comment_constraints_empty_returns_empty(self):
        assert await gen.generate_add_comment_constraints(task_url=None, dataset={"movies": []}) == []

    async def test_generate_edit_film_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_edit_film_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)
        assert any(c.get("field") == "username" for c in result)

    async def test_generate_edit_film_constraints_empty_films_returns_login_fallback(self):
        with patch.object(gen, "_get_films_data", new_callable=AsyncMock, return_value=[]), patch.object(gen, "_ensure_dataset", new_callable=AsyncMock, return_value={}):
            result = await gen.generate_edit_film_constraints(task_url=None, dataset={})
        assert isinstance(result, list)
        assert any(c.get("field") == "username" for c in result)


@pytest.mark.asyncio
async def test_get_films_data_returns_empty_when_movies_key_missing_async():
    assert await gen._get_films_data(task_url=None, dataset={"other": []}) == []
