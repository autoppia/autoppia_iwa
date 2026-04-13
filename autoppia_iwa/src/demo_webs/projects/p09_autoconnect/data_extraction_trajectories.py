from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autoconnect"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "VIEW_USER_PROFILE",
        "seed": SEED,
        "question": "What is the username of the user where name is 'Sarah Chen'?",
        "expected_answer": "sarah.chen",
    },
    {
        "use_case": "CONNECT_WITH_USER",
        "seed": SEED,
        "question": "What is the name of the user where username is 'sarah.chen'?",
        "expected_answer": "Sarah Chen",
    },
    {
        "use_case": "LIKE_POST",
        "seed": SEED,
        "question": "What is the avatar of the user where name is 'Sarah Chen'?",
        "expected_answer": "/media/avatars/person1.jpg",
    },
    {
        "use_case": "COMMENT_ON_POST",
        "seed": SEED,
        "question": "What is the bio of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer at Google with 8+ years of experience in mobile and web design.",
    },
    {
        "use_case": "SAVE_POST",
        "seed": SEED,
        "question": "What is the title of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer",
    },
    {
        "use_case": "HIDE_POST",
        "seed": SEED,
        "question": "What is the username of the user where name is 'Sarah Chen'?",
        "expected_answer": "sarah.chen",
    },
    {
        "use_case": "EDIT_PROFILE",
        "seed": SEED,
        "question": "What is the name of the user where username is 'sarah.chen'?",
        "expected_answer": "Sarah Chen",
    },
    {
        "use_case": "EDIT_EXPERIENCE",
        "seed": SEED,
        "question": "What is the avatar of the user where name is 'Sarah Chen'?",
        "expected_answer": "/media/avatars/person1.jpg",
    },
    {
        "use_case": "ADD_EXPERIENCE",
        "seed": SEED,
        "question": "What is the bio of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer at Google with 8+ years of experience in mobile and web design.",
    },
    {
        "use_case": "REMOVE_POST",
        "seed": SEED,
        "question": "What is the title of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer",
    },
    {
        "use_case": "SEARCH_USERS",
        "seed": SEED,
        "question": "What is the username of the user where name is 'Sarah Chen'?",
        "expected_answer": "sarah.chen",
    },
    {
        "use_case": "FOLLOW_PAGE",
        "seed": SEED,
        "question": "What is the name of the user where username is 'sarah.chen'?",
        "expected_answer": "Sarah Chen",
    },
    {
        "use_case": "VIEW_JOB",
        "seed": SEED,
        "question": "What is the avatar of the user where name is 'Sarah Chen'?",
        "expected_answer": "/media/avatars/person1.jpg",
    },
    {
        "use_case": "FILTER_JOBS",
        "seed": SEED,
        "question": "What is the bio of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer at Google with 8+ years of experience in mobile and web design.",
    },
    {
        "use_case": "APPLY_FOR_JOB",
        "seed": SEED,
        "question": "What is the title of the user where name is 'Sarah Chen'?",
        "expected_answer": "Senior UX Designer",
    },
    {
        "use_case": "SEARCH_JOBS",
        "seed": SEED,
        "question": "What is the username of the user where name is 'Sarah Chen'?",
        "expected_answer": "sarah.chen",
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


def load_autoconnect_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
