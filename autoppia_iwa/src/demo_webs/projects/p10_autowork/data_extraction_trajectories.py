from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autowork"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "BOOK_A_CONSULTATION",
        "seed": SEED,
        "question": "What is the status of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "In progress",
    },
    {
        "use_case": "HIRE_BTN_CLICKED",
        "seed": SEED,
        "question": "What is the start of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "Nov 25",
    },
    {
        "use_case": "HIRE_LATER",
        "seed": SEED,
        "question": "What is the activity of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "last active today on Time logged this week: 42:00 hrs ($3,150)",
    },
    {
        "use_case": "QUICK_HIRE",
        "seed": SEED,
        "question": "What is the time of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "42:00 hrs ($3,150)",
    },
    {
        "use_case": "HIRE_CONSULTANT",
        "seed": SEED,
        "question": "What is the timestr of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "Time logged this week:",
    },
    {
        "use_case": "POST_A_JOB",
        "seed": SEED,
        "question": "What is the active of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "true",
    },
    {
        "use_case": "CONTACT_EXPERT_OPENED",
        "seed": SEED,
        "question": "What is the status of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "In progress",
    },
    {
        "use_case": "EDIT_PROFILE_NAME",
        "seed": SEED,
        "question": "What is the start of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "Nov 25",
    },
    {
        "use_case": "EDIT_PROFILE_EMAIL",
        "seed": SEED,
        "question": "What is the activity of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "last active today on Time logged this week: 42:00 hrs ($3,150)",
    },
    {
        "use_case": "EDIT_PROFILE_TITLE",
        "seed": SEED,
        "question": "What is the time of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "42:00 hrs ($3,150)",
    },
    {
        "use_case": "EDIT_PROFILE_LOCATION",
        "seed": SEED,
        "question": "What is the timestr of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "Time logged this week:",
    },
    {
        "use_case": "FAVORITE_EXPERT_SELECTED",
        "seed": SEED,
        "question": "What is the active of the job where title is 'Build e-commerce website with React and Node.js'?",
        "expected_answer": "true",
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

def load_autowork_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
