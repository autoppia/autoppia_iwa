from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autostats"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "VIEW_SUBNET",
        "seed": SEED,
        "question": "What is the coldkey of the validator where hotkey is '5A799Cx2RgwURj2B2oqXLafnVfXYTZuJnENHr9HxcAYBBiuo'?",
        "expected_answer": "5A7zaSNCify9TyX82wmwvAyYWeJtykzfojvL7U3g72cDMKcC",
    },
    {
        "use_case": "VIEW_VALIDATOR",
        "seed": SEED,
        "question": "What is the stake of the validator where hotkey is '5A799Cx2RgwURj2B2oqXLafnVfXYTZuJnENHr9HxcAYBBiuo'?",
        "expected_answer": "962431",
    },
    {
        "use_case": "VIEW_BLOCK",
        "seed": SEED,
        "question": "What is the return percentage of the validator where hotkey is '5A799Cx2RgwURj2B2oqXLafnVfXYTZuJnENHr9HxcAYBBiuo'?",
        "expected_answer": "10.53",
    },
    {
        "use_case": "VIEW_ACCOUNT",
        "seed": SEED,
        "question": "What is the nominator count of the validator where hotkey is '5A799Cx2RgwURj2B2oqXLafnVfXYTZuJnENHr9HxcAYBBiuo'?",
        "expected_answer": "35",
    },
    {
        "use_case": "TRANSFER_COMPLETE",
        "seed": SEED,
        "question": "What is the nominator change24h of the validator where hotkey is '5A799Cx2RgwURj2B2oqXLafnVfXYTZuJnENHr9HxcAYBBiuo'?",
        "expected_answer": "1",
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


def load_autostats_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
