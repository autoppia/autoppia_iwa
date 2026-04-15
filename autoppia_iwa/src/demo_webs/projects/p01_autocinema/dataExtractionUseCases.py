from __future__ import annotations

from dataclasses import dataclass

from autoppia_iwa.src.data_generation.tasks.classes import Task
from autoppia_iwa.src.data_generation.tests.classes import DataExtractionTest

from .data_utils import fetch_data


@dataclass(frozen=True)
class DataExtractionUseCaseDefinition:
    name: str
    description: str


DATA_EXTRACTION_USE_CASES: list[DataExtractionUseCaseDefinition] = [
    DataExtractionUseCaseDefinition(
        name="FIND_DIRECTOR",
        description="Find the director of a movie using identifying fields.",
    ),
    DataExtractionUseCaseDefinition(
        name="FIND_MOVIE",
        description="Find the movie name using director/year/rating identifiers.",
    ),
    DataExtractionUseCaseDefinition(
        name="FIND_ACTOR",
        description="Find an actor from the cast of a selected movie.",
    ),
    DataExtractionUseCaseDefinition(
        name="FIND_YEAR",
        description="Find the release year of a selected movie.",
    ),
]


def _pick_movie(*, movies: list[dict], seed: int, offset: int) -> dict:
    idx = abs((int(seed) * 131) + (offset * 17)) % len(movies)
    return movies[idx]


def _extract_first_actor(movie: dict) -> str | None:
    cast_value = movie.get("cast")
    if isinstance(cast_value, list):
        for value in cast_value:
            actor = str(value or "").strip()
            if actor:
                return actor
        return None
    if isinstance(cast_value, str):
        actor = str(cast_value.split(",")[0]).strip()
        return actor or None
    return None


def _build_find_director_task(*, movie: dict) -> tuple[str, str] | None:
    name = str(movie.get("name", "")).strip()
    director = movie.get("director")
    year = movie.get("year")
    rating = movie.get("rating")
    if not name or director in (None, "") or year is None or rating is None:
        return None
    question = f"Who is the director of the movie {name} that was released in {year} and has a rating of {rating}?"
    return question, str(director).strip()


def _build_find_movie_task(*, movie: dict) -> tuple[str, str] | None:
    name = str(movie.get("name", "")).strip()
    director = movie.get("director")
    year = movie.get("year")
    rating = movie.get("rating")
    if not name or director in (None, "") or year is None or rating is None:
        return None
    question = f"What is the name of the movie directed by {director} that was released in {year} and has a rating of {rating}?"
    return question, name


def _build_find_actor_task(*, movie: dict) -> tuple[str, str] | None:
    name = str(movie.get("name", "")).strip()
    director = movie.get("director")
    year = movie.get("year")
    actor = _extract_first_actor(movie)
    if not name or director in (None, "") or year is None or not actor:
        return None
    question = f"Name one actor who appears in the movie {name} directed by {director} and released in {year}."
    return question, actor


def _build_find_year_task(*, movie: dict) -> tuple[str, str] | None:
    name = str(movie.get("name", "")).strip()
    director = movie.get("director")
    year = movie.get("year")
    rating = movie.get("rating")
    if not name or director in (None, "") or year is None or rating is None:
        return None
    question = f"In which year was the movie {name} directed by {director} released, if its rating is {rating}?"
    return question, str(year)


def _definition_names() -> list[str]:
    return [item.name for item in DATA_EXTRACTION_USE_CASES]


async def generate_de_tasks(
    *,
    seed: int,
    task_url: str,
    selected_use_cases: set[str] | None = None,
) -> list[Task]:
    movies = await fetch_data(seed_value=int(seed), count=50)
    if not movies:
        return []

    selected = {name.upper() for name in selected_use_cases} if selected_use_cases else set(_definition_names())

    builders = {
        "FIND_DIRECTOR": lambda movie: _build_find_director_task(movie=movie),
        "FIND_MOVIE": lambda movie: _build_find_movie_task(movie=movie),
        "FIND_ACTOR": lambda movie: _build_find_actor_task(movie=movie),
        "FIND_YEAR": lambda movie: _build_find_year_task(movie=movie),
    }

    tasks: list[Task] = []
    for offset, use_case_name in enumerate(_definition_names(), start=1):
        if use_case_name not in selected:
            continue
        movie = _pick_movie(movies=movies, seed=int(seed), offset=offset)
        built = builders[use_case_name](movie)
        if built is None:
            continue
        question, expected_answer = built
        task = Task(
            web_project_id="autocinema",
            url=task_url,
            prompt=question,
            tests=[DataExtractionTest(expected_answer=expected_answer)],
        )
        task.assign_seed_to_url(seed_value=int(seed))
        task.de_use_case_name = use_case_name
        task.task_type = "DEtask"
        task.de_expected_answer = expected_answer
        tasks.append(task)

    return tasks
