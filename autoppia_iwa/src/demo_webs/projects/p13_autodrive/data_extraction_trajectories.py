from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autodrive"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "SELECT_DATE",
        "seed": SEED,
        "question": "What is the label of the place where main is '1 Hotel San Francisco'?",
        "expected_answer": "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA",
    },
    {
        "use_case": "SELECT_TIME",
        "seed": SEED,
        "question": "What is the main of the place where label is '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'?",
        "expected_answer": "1 Hotel San Francisco",
    },
    {
        "use_case": "SEARCH",
        "seed": SEED,
        "question": "What is the sub of the place where label is '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'?",
        "expected_answer": "8 Mission St, San Francisco, CA 94105, USA",
    },
    {
        "use_case": "SELECT_CAR",
        "seed": SEED,
        "question": "What is the category of the place where label is '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'?",
        "expected_answer": "hotel",
    },
    {
        "use_case": "RESERVE_RIDE",
        "seed": SEED,
        "question": "What is the latitude of the place where label is '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'?",
        "expected_answer": "37.7937",
    },
    {
        "use_case": "TRIP_DETAILS",
        "seed": SEED,
        "question": "What is the longitude of the place where label is '1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA'?",
        "expected_answer": "-122.3929",
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

def load_autodrive_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
