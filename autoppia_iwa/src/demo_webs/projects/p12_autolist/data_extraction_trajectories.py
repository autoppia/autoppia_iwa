from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autolist"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "AUTOLIST_ADD_TASK_CLICKED",
        "seed": SEED,
        "question": "What is the name of the task where created at is '2025-01-15'?",
        "expected_answer": "Complete project proposal",
    },
    {
        "use_case": "AUTOLIST_SELECT_DATE_FOR_TASK",
        "seed": SEED,
        "question": "What is the description of the task where name is 'Complete project proposal'?",
        "expected_answer": "Write and submit the quarterly project proposal with all required documentation",
    },
    {
        "use_case": "AUTOLIST_SELECT_TASK_PRIORITY",
        "seed": SEED,
        "question": "What is the priority of the task where name is 'Complete project proposal'?",
        "expected_answer": "1",
    },
    {
        "use_case": "AUTOLIST_EDIT_TASK_MODAL_OPENED",
        "seed": SEED,
        "question": "What is the status of the task where name is 'Complete project proposal'?",
        "expected_answer": "pending",
    },
    {
        "use_case": "AUTOLIST_COMPLETE_TASK",
        "seed": SEED,
        "question": "What is the created at of the task where name is 'Complete project proposal'?",
        "expected_answer": "2025-01-15",
    },
    {
        "use_case": "AUTOLIST_DELETE_TASK",
        "seed": SEED,
        "question": "What is the due date of the task where name is 'Complete project proposal'?",
        "expected_answer": "2025-01-20",
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


def load_autolist_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
