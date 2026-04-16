from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autobooks"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "FIND_BOOK",
        "seed": SEED,
        "question": "What is the name of the book where year is '-800'?",
        "expected_answer": "The Odyssey",
    },
    {
        "use_case": "FIND_AUTHOR",
        "seed": SEED,
        "question": "What is the year of the book where name is 'The Odyssey'?",
        "expected_answer": "-800",
    },
    {
        "use_case": "FIND_PAGES",
        "seed": SEED,
        "question": "What is the img of the book where name is 'The Odyssey'?",
        "expected_answer": "/media/gallery/9780140268867.webp",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "Who is the director for the book where name is 'The Odyssey'?",
        "expected_answer": "Homer",
    },
    {
        "use_case": "FIND_BOOK",
        "seed": SEED,
        "question": "What is the duration of the book where name is 'The Odyssey'?",
        "expected_answer": "541",
    },
    {
        "use_case": "FIND_AUTHOR",
        "seed": SEED,
        "question": "What is the trailer url of the book where name is 'The Odyssey'?",
        "expected_answer": "https://www.bookstores.com/books/edition/_/9780140268867?hl=en&gbpv=1",
    },
    {
        "use_case": "FIND_PAGES",
        "seed": SEED,
        "question": "What is the rating of the book where name is 'The Odyssey'?",
        "expected_answer": "4.7",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "What is the price of the book where name is 'The Odyssey'?",
        "expected_answer": "12.99",
    },
]


def _build_trajectory(spec: dict[str, str | int]) -> DataExtractionTrajectory:
    return DataExtractionTrajectory(
        web_project_id=PROJECT_ID,
        seed=int(spec["seed"]),
        use_case=spec["use_case"],
        question=spec["question"],
        expected_answer=spec["expected_answer"],
        actions=None,
    )


def load_autobooks_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
