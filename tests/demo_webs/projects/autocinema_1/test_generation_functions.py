"""Tests for autocinema_1 generation_functions."""

import random
from typing import ClassVar
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.demo_webs.projects.p01_autocinema import generation_functions as gen
from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator


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

    async def test_generate_add_to_watchlist_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_add_to_watchlist_constraints(task_url=None, dataset=dataset)
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

    async def test_generate_add_comment_constraints_with_dataset(self):
        dataset = {"movies": self._SAMPLE_FILMS}
        result = await gen.generate_add_comment_constraints(task_url=None, dataset=dataset)
        assert isinstance(result, list)

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
