from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory
from autoppia_iwa.src.execution.actions.actions import ExtractAction, NavigateAction
from autoppia_iwa.src.execution.actions.base import Selector, SelectorType

BASE = "http://localhost:8015"
SEED = 1
PROJECT_ID = "autodiscord"
HOME_URL = f"{BASE}/?seed={SEED}"

_PAGE_SELECTOR = Selector(type=SelectorType.XPATH_SELECTOR, value="//body")

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "VIEW_DMS",
        "seed": SEED,
        "question": "What is the platform name shown on the AutoDiscord page?",
        "expected_answer": "Discord",
    },
    {
        "use_case": "SELECT_SERVER",
        "seed": SEED,
        "question": "What is the platform name shown on the AutoDiscord page?",
        "expected_answer": "Discord",
    },
    {
        "use_case": "SELECT_CHANNEL",
        "seed": SEED,
        "question": "What is the platform name shown on the AutoDiscord page?",
        "expected_answer": "Discord",
    },
    {
        "use_case": "ADD_REACTION",
        "seed": SEED,
        "question": "What is the platform name shown on the AutoDiscord page?",
        "expected_answer": "Discord",
    },
    {
        "use_case": "JOIN_VOICE_CHANNEL",
        "seed": SEED,
        "question": "What is the platform name shown on the AutoDiscord page?",
        "expected_answer": "Discord",
    },
]

def _build_trajectory(spec: dict[str, str | int]) -> DataExtractionTrajectory:
    return DataExtractionTrajectory(
        web_project_id=PROJECT_ID,
        seed=int(spec["seed"]),
        use_case=spec["use_case"],
        question=spec["question"],
        expected_answer=spec["expected_answer"],
        actions=[
            NavigateAction(url=HOME_URL),
            ExtractAction(selector=_PAGE_SELECTOR, max_chars=50000),
        ],
    )

def load_autodiscord_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
