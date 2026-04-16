from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autodining"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "FIND_RESTAURANT",
        "seed": SEED,
        "question": "In the dataset, what country code is listed for Le Jardin?",
        "expected_answer": "US",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "In the dataset, what is the restaurant name for the entry with image '/images/restaurant1.jpg'?",
        "expected_answer": "Le Jardin",
    },
    {
        "use_case": "FIND_LOCATION",
        "seed": SEED,
        "question": "In the dataset, what cuisine is listed for Le Jardin?",
        "expected_answer": "French",
    },
    {
        "use_case": "FIND_PLATE",
        "seed": SEED,
        "question": "In the dataset, in which area is Le Jardin located?",
        "expected_answer": "Castro",
    },
    {
        "use_case": "FIND_CUISINE",
        "seed": SEED,
        "question": "In the dataset, how many reviews does Le Jardin have?",
        "expected_answer": "305",
    },
    {
        "use_case": "FIND_RESTAURANT",
        "seed": SEED,
        "question": "In the dataset, how many bookings does Le Jardin have?",
        "expected_answer": "204",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "In the dataset, what rating is shown for Le Jardin?",
        "expected_answer": "4.6",
    },
    {
        "use_case": "FIND_LOCATION",
        "seed": SEED,
        "question": "In the dataset, how many stars are shown for Le Jardin?",
        "expected_answer": "5",
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


def load_autodining_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
