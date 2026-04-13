from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autolodge"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "SEARCH_HOTEL",
        "seed": SEED,
        "question": "What is the image of the hotel where title is 'Garden Riad'?",
        "expected_answer": "/images/hotel16.png",
    },
    {
        "use_case": "VIEW_HOTEL",
        "seed": SEED,
        "question": "What is the title of the hotel where price is '240'?",
        "expected_answer": "Garden Riad",
    },
    {
        "use_case": "EDIT_NUMBER_OF_GUESTS",
        "seed": SEED,
        "question": "What is the location of the hotel where title is 'Garden Riad'?",
        "expected_answer": "Marrakech, Morocco",
    },
    {
        "use_case": "RESERVE_HOTEL",
        "seed": SEED,
        "question": "What is the rating of the hotel where title is 'Garden Riad'?",
        "expected_answer": "4.5",
    },
    {
        "use_case": "EDIT_CHECK_IN_OUT_DATES",
        "seed": SEED,
        "question": "What is the reviews of the hotel where title is 'Garden Riad'?",
        "expected_answer": "155",
    },
    {
        "use_case": "MESSAGE_HOST",
        "seed": SEED,
        "question": "What is the guests of the hotel where title is 'Garden Riad'?",
        "expected_answer": "4",
    },
    {
        "use_case": "SHARE_HOTEL",
        "seed": SEED,
        "question": "What is the guests of the hotel where title is 'Garden Riad'?",
        "expected_answer": "4",
    },
    {
        "use_case": "ADD_TO_WISHLIST",
        "seed": SEED,
        "question": "What is the bedrooms of the hotel where title is 'Garden Riad'?",
        "expected_answer": "2",
    },
    {
        "use_case": "APPLY_FILTERS",
        "seed": SEED,
        "question": "What is the beds of the hotel where title is 'Garden Riad'?",
        "expected_answer": "3",
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

def load_autolodge_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
