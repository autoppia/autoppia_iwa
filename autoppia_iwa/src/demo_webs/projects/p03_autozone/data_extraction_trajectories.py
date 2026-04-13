from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autozone"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "VIEW_DETAIL",
        "seed": SEED,
        "question": "What is the title of the product where price is '$89.99'?",
        "expected_answer": "Professional Blender",
    },
    {
        "use_case": "DETAILS_TOGGLE",
        "seed": SEED,
        "question": "What is the price of the product where title is 'Professional Blender'?",
        "expected_answer": "$89.99",
    },
    {
        "use_case": "SHARE_PRODUCT",
        "seed": SEED,
        "question": "What is the image of the product where price is '$89.99'?",
        "expected_answer": "/images/homepage_categories/blender.jpg",
    },
    {
        "use_case": "SEARCH_PRODUCT",
        "seed": SEED,
        "question": "What is the description of the product where price is '$89.99'?",
        "expected_answer": "High-speed professional blender with multiple speed settings and durable stainless steel blades.",
    },
    {
        "use_case": "CATEGORY_FILTER",
        "seed": SEED,
        "question": "What is the category of the product where price is '$89.99'?",
        "expected_answer": "Kitchen",
    },
    {
        "use_case": "ADD_TO_CART",
        "seed": SEED,
        "question": "What is the rating of the product where price is '$89.99'?",
        "expected_answer": "4.5",
    },
    {
        "use_case": "ADD_TO_WISHLIST",
        "seed": SEED,
        "question": "What is the brand of the product where price is '$89.99'?",
        "expected_answer": "BlendPro",
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

def load_autozone_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
