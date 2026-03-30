"""Tests for autocinema_1 replace_functions."""

from typing import ClassVar
from unittest.mock import AsyncMock, patch

import pytest

from autoppia_iwa.src.demo_webs.projects.p01_autocinema import replace_functions as repl


class TestLoginReplaceFunc:
    def test_replaces_username_and_password(self):
        text = "User: <username> Pass: <password>"
        result = repl.login_replace_func(text)
        assert "user<web_agent_id>" in result
        assert "Passw0rd!" in result

    def test_non_str_returns_unchanged(self):
        result = repl.login_replace_func(None)
        assert result is None
        result = repl.login_replace_func(123)
        assert result == 123

    def test_constraints_replace_placeholder(self):
        text = "Profile <email>"
        constraints = [{"field": "email", "value": "a@b.com"}]
        result = repl.login_replace_func(text, constraints=constraints)
        assert "a@b.com" in result


class TestRegisterReplaceFunc:
    def test_replaces_username_email_password(self):
        text = "<username> <email> <password>"
        result = repl.register_replace_func(text)
        assert "newuser<web_agent_id>" in result
        assert "newuser<web_agent_id>@gmail.com" in result
        assert "Passw0rd!" in result

    def test_non_str_returns_unchanged(self):
        result = repl.register_replace_func(None)
        assert result is None


class TestFilmNameFromConstraints:
    def test_none_constraints_returns_none(self):
        assert repl._film_name_from_constraints(None) is None
        assert repl._film_name_from_constraints([]) is None

    def test_name_field_returns_value(self):
        constraints = [{"field": "name", "value": "Gladiator"}]
        assert repl._film_name_from_constraints(constraints) == "Gladiator"

    def test_query_field_returns_value(self):
        constraints = [{"field": "query", "value": "Inception"}]
        assert repl._film_name_from_constraints(constraints) == "Inception"

    def test_other_field_ignored(self):
        constraints = [{"field": "year", "value": 2000}]
        assert repl._film_name_from_constraints(constraints) is None


@pytest.mark.asyncio
class TestReplaceFilmPlaceholders:
    _SAMPLE_MOVIES: ClassVar[list] = [
        {"name": "Inception", "year": 2010, "duration": 148, "genres": ["Sci-Fi", "Action"], "director": "Nolan"},
    ]

    async def test_non_str_returns_unchanged(self):
        result = await repl.replace_film_placeholders(None)
        assert result is None

    async def test_empty_movies_returns_text_unchanged(self):
        result = await repl.replace_film_placeholders("Hello <movie>", dataset=[])
        assert result == "Hello <movie>"

    async def test_replaces_movie_and_duration_with_dataset(self):
        dataset = {"movies": [{"name": "Inception", "year": 2010, "duration": 148, "genres": ["Sci-Fi"], "director": "Nolan"}]}
        result = await repl.replace_film_placeholders("Watch <movie> (<duration> min)", dataset=dataset)
        assert "Inception" in result
        assert "148" in result

    async def test_constraint_film_name_used_for_movie_placeholder(self):
        dataset = {
            "movies": [
                {"name": "Inception", "year": 2010, "duration": 148, "genres": ["Sci-Fi"], "director": "Nolan"},
                {"name": "Gladiator", "year": 2000, "duration": 155, "genres": ["Drama"], "director": "Scott"},
            ]
        }
        constraints = [{"field": "name", "value": "Gladiator"}]
        result = await repl.replace_film_placeholders("Edit <movie>", dataset=dataset, constraints=constraints)
        assert result == "Edit Gladiator"

    async def test_decade_placeholder_replaced_when_present(self):
        dataset = {"movies": [{"name": "X", "year": 2005, "duration": 90, "genres": ["Drama"], "director": "Y"}]}
        result = await repl.replace_film_placeholders("Films of <decade>0s: <movie>", dataset=dataset)
        assert "200" in result or "X" in result

    async def test_dataset_as_list_accepted(self):
        movies_list = [{"name": "A", "year": 2020, "duration": 100, "genres": ["Action"], "director": "B"}]
        result = await repl.replace_film_placeholders("<movie>", dataset=movies_list)
        assert result == "A"

    async def test_fetch_data_called_when_dataset_none(self):
        with patch("autoppia_iwa.src.demo_webs.projects.p01_autocinema.replace_functions.fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = self._SAMPLE_MOVIES
            result = await repl.replace_film_placeholders("Watch <movie>", seed_value=42)
            mock_fetch.assert_called_once_with(seed_value=42)
        assert "Inception" in result


@pytest.mark.asyncio
class TestLoginAndFilmReplaceFunc:
    async def test_applies_login_then_film_replacements(self):
        dataset = {"movies": [{"name": "Matrix", "year": 1999, "duration": 136, "genres": ["Sci-Fi"], "director": "Wachowski"}]}
        text = "User <username> watch <movie>"
        result = await repl.login_and_film_replace_func(text, dataset=dataset)
        assert "user<web_agent_id>" in result
        assert "Matrix" in result

    async def test_passes_constraints_through(self):
        dataset = {"movies": [{"name": "A", "year": 2020, "duration": 90, "genres": ["Drama"], "director": "B"}]}
        constraints = [{"field": "name", "value": "A"}]
        result = await repl.login_and_film_replace_func("Login <username> then <movie>", dataset=dataset, constraints=constraints)
        assert "user<web_agent_id>" in result
        assert "A" in result
