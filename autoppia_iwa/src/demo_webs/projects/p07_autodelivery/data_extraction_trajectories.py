from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autodelivery"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "SEARCH_DELIVERY_RESTAURANT",
        "seed": SEED,
        "question": "What is the name of the restaurant where description is 'Authentic Italian cuisine with fresh ingredients and traditional recipes.'?",
        "expected_answer": "Bella Vista",
    },
    {
        "use_case": "VIEW_DELIVERY_RESTAURANT",
        "seed": SEED,
        "question": "What is the description of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "Authentic Italian cuisine with fresh ingredients and traditional recipes.",
    },
    {
        "use_case": "RESTAURANT_FILTER",
        "seed": SEED,
        "question": "What is the image of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "/images/restaurant1.jpg",
    },
    {
        "use_case": "DELETE_REVIEW",
        "seed": SEED,
        "question": "What is the cuisine of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "Italian",
    },
    {
        "use_case": "ADD_TO_CART_MODAL_OPEN",
        "seed": SEED,
        "question": "What is the rating of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "4.8",
    },
    {
        "use_case": "ADD_TO_CART_MENU_ITEM",
        "seed": SEED,
        "question": "What is the delivery time of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "25-35 min",
    },
    {
        "use_case": "QUICK_REORDER",
        "seed": SEED,
        "question": "What is the pickup time of the restaurant where name is 'Bella Vista'?",
        "expected_answer": "10 min",
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


def load_autodelivery_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
