from __future__ import annotations

import pytest

from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest
from autoppia_iwa.src.demo_webs.projects.autocinema_1 import dataExtractionUseCases as de_uc


def _sample_movies() -> list[dict]:
    return [
        {
            "name": "Up",
            "director": "Pete Docter",
            "year": 2009,
            "rating": 8.3,
            "cast": "Ed Asner, Christopher Plummer",
        },
        {
            "name": "Inception",
            "director": "Christopher Nolan",
            "year": 2010,
            "rating": 8.8,
            "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt",
        },
        {
            "name": "The Matrix",
            "director": "Lana Wachowski",
            "year": 1999,
            "rating": 8.7,
            "cast": "Keanu Reeves, Laurence Fishburne",
        },
        {
            "name": "Toy Story",
            "director": "John Lasseter",
            "year": 1995,
            "rating": 8.3,
            "cast": "Tom Hanks, Tim Allen",
        },
        {
            "name": "Forrest Gump",
            "director": "Robert Zemeckis",
            "year": 1994,
            "rating": 8.8,
            "cast": "Tom Hanks, Robin Wright",
        },
    ]


@pytest.mark.asyncio
async def test_generate_de_tasks_autocinema_builds_four_detasks(monkeypatch):
    async def _fake_fetch_data(seed_value: int | None = None, count: int = 50):
        _ = seed_value, count
        return _sample_movies()

    monkeypatch.setattr(de_uc, "fetch_data", _fake_fetch_data)

    tasks = await de_uc.generate_de_tasks(
        seed=1,
        task_url="http://localhost:8000/?seed=1",
        selected_use_cases=None,
    )

    assert len(tasks) == 4
    assert {getattr(task, "de_use_case_name", "") for task in tasks} == {
        "FIND_DIRECTOR",
        "FIND_MOVIE",
        "FIND_ACTOR",
        "FIND_YEAR",
    }

    for task in tasks:
        assert task.web_project_id == "autocinema"
        assert "seed=1" in task.url
        assert task.prompt
        assert getattr(task, "task_type", "") == "DEtask"
        assert len(task.tests) == 1
        assert isinstance(task.tests[0], DataExtractionTest)
        assert task.tests[0].expected_answer is not None


@pytest.mark.asyncio
async def test_generate_de_tasks_autocinema_filters_selected_use_cases(monkeypatch):
    async def _fake_fetch_data(seed_value: int | None = None, count: int = 50):
        _ = seed_value, count
        return _sample_movies()

    monkeypatch.setattr(de_uc, "fetch_data", _fake_fetch_data)

    tasks = await de_uc.generate_de_tasks(
        seed=7,
        task_url="http://localhost:8000/?seed=7",
        selected_use_cases={"FIND_DIRECTOR", "FIND_YEAR"},
    )

    assert len(tasks) == 2
    assert {getattr(task, "de_use_case_name", "") for task in tasks} == {
        "FIND_DIRECTOR",
        "FIND_YEAR",
    }
