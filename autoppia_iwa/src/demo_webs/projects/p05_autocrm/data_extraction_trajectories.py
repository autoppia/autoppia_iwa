from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autocrm"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "FIND_CLIENT",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "FIND_BILLING",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "FIND_MATTER",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "FIND_CLIENT",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "FIND_BILLING",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "FIND_MATTER",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "FIND_CLIENT",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "FIND_BILLING",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "FIND_MATTER",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "FIND_CLIENT",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "FIND_BILLING",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "FIND_MATTER",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "FIND_CLIENT",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "FIND_BILLING",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "FIND_MATTER",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
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


def load_autocrm_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
