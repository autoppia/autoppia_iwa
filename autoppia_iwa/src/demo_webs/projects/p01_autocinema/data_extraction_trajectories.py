from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1

_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "FIND_DIRECTOR",
        "seed": SEED,
        "question": "Who is the director of the movie Up that was released in 2009 and has a rating of 8.3?",
        "expected_answer": "Pete Docter",
    },
    {
        "use_case": "FIND_MOVIE",
        "seed": SEED,
        "question": "Who directed the film released in 2010 in the Action, Sci-Fi, and Thriller genres?",
        "expected_answer": "Christopher Nolan",
    },
    {
        "use_case": "FIND_ACTOR",
        "seed": SEED,
        "question": "Who directed the film that belongs to the genres of Crime and Drama and was released in 1972?",
        "expected_answer": "Francis Ford Coppola",
    },
    {
        "use_case": "FIND_YEAR",
        "seed": SEED,
        "question": "What is the duration of the film 'Toy Story' directed by John Lasseter and released in 1995?",
        "expected_answer": "81",
    },
    {
        "use_case": "FIND_DIRECTOR",
        "seed": SEED,
        "question": "Who directed the movie 'The Prestige' released in 2006 with a rating of 8.5?",
        "expected_answer": "Christopher Nolan",
    },
    {
        "use_case": "FIND_MOVIE",
        "seed": SEED,
        "question": "Who directed the movie with a duration of 142 minutes?",
        "expected_answer": "Robert Zemeckis",
    },
    {
        "use_case": "FIND_ACTOR",
        "seed": SEED,
        "question": "Who directed the film featuring Jamie Foxx, Christoph Waltz, Leonardo DiCaprio, and Kerry Washington in Drama and Western genres?",
        "expected_answer": "Quentin Tarantino",
    },
]


def _build(spec: dict[str, str | int]) -> DataExtractionTrajectory:
    return DataExtractionTrajectory(
        web_project_id="autocinema",
        seed=int(spec["seed"]),
        use_case=spec["use_case"],
        question=spec["question"],
        expected_answer=spec["expected_answer"],
        actions=None,
    )


def load_autocinema_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build(spec) for spec in _SPECS]
