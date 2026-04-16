from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autohealth"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "FIND_DOCTOR",
        "seed": SEED,
        "question": "What is the doctor id of the appointment where date is '2025-09-01'?",
        "expected_answer": "d47",
    },
    {
        "use_case": "FIND_APPOITNMENT",
        "seed": SEED,
        "question": "Who is the doctor name for the appointment where date is '2025-09-01'?",
        "expected_answer": "Dr. Lisa Green",
    },
    {
        "use_case": "FIND_PRESCRIPTION",
        "seed": SEED,
        "question": "What is the specialty of the appointment where date is '2025-09-01'?",
        "expected_answer": "Cardiology",
    },
    {
        "use_case": "FIND_ANALYSIS",
        "seed": SEED,
        "question": "What is the date of the appointment where doctor name is 'Dr. Lisa Green'?",
        "expected_answer": "2025-09-01",
    },
    {
        "use_case": "FIND_ESPECIALITY",
        "seed": SEED,
        "question": "What is the time of the appointment where date is '2025-09-01'?",
        "expected_answer": "11:00 AM",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "What is the doctor id of the appointment where date is '2025-09-01'?",
        "expected_answer": "d47",
    },
    {
        "use_case": "FIND_DOCTOR",
        "seed": SEED,
        "question": "Who is the doctor name for the appointment where date is '2025-09-01'?",
        "expected_answer": "Dr. Lisa Green",
    },
    {
        "use_case": "FIND_APPOITNMENT",
        "seed": SEED,
        "question": "What is the specialty of the appointment where date is '2025-09-01'?",
        "expected_answer": "Cardiology",
    },
    {
        "use_case": "FIND_PRESCRIPTION",
        "seed": SEED,
        "question": "What is the date of the appointment where doctor name is 'Dr. Lisa Green'?",
        "expected_answer": "2025-09-01",
    },
    {
        "use_case": "FIND_ANALYSIS",
        "seed": SEED,
        "question": "What is the time of the appointment where date is '2025-09-01'?",
        "expected_answer": "11:00 AM",
    },
    {
        "use_case": "FIND_ESPECIALITY",
        "seed": SEED,
        "question": "What is the doctor id of the appointment where date is '2025-09-01'?",
        "expected_answer": "d47",
    },
    {
        "use_case": "FIND_RATING",
        "seed": SEED,
        "question": "Who is the doctor name for the appointment where date is '2025-09-01'?",
        "expected_answer": "Dr. Lisa Green",
    },
    {
        "use_case": "FIND_DOCTOR",
        "seed": SEED,
        "question": "What is the specialty of the appointment where date is '2025-09-01'?",
        "expected_answer": "Cardiology",
    },
    {
        "use_case": "FIND_APPOITNMENT",
        "seed": SEED,
        "question": "What is the date of the appointment where doctor name is 'Dr. Lisa Green'?",
        "expected_answer": "2025-09-01",
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


def load_autohealth_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
