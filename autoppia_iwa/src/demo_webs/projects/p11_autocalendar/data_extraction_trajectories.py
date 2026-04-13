from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autocalendar"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "ADD_NEW_CALENDAR",
        "seed": SEED,
        "question": "What is the date of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "2025-12-15",
    },
    {
        "use_case": "CREATE_CALENDAR",
        "seed": SEED,
        "question": "What is the start of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "9",
    },
    {
        "use_case": "UNSELECT_CALENDAR",
        "seed": SEED,
        "question": "What is the end of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "10",
    },
    {
        "use_case": "SELECT_CALENDAR",
        "seed": SEED,
        "question": "What is the label of the event where description is 'Daily standup with the development team to discuss progress and blockers.'?",
        "expected_answer": "Team Standup Meeting",
    },
    {
        "use_case": "SEARCH_SUBMIT",
        "seed": SEED,
        "question": "What is the calendar of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "Work",
    },
    {
        "use_case": "EVENT_WIZARD_OPEN",
        "seed": SEED,
        "question": "What is the color of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "#2196F3",
    },
    {
        "use_case": "DELETE_ADDED_EVENT",
        "seed": SEED,
        "question": "What is the start of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "9",
    },
    {
        "use_case": "EVENT_ADD_REMINDER",
        "seed": SEED,
        "question": "What is the end of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "10",
    },
    {
        "use_case": "EVENT_REMOVE_REMINDER",
        "seed": SEED,
        "question": "What is the description of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "Daily standup with the development team to discuss progress and blockers.",
    },
    {
        "use_case": "EVENT_ADD_ATTENDEE",
        "seed": SEED,
        "question": "What is the location of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "Conference Room A",
    },
    {
        "use_case": "EVENT_REMOVE_ATTENDEE",
        "seed": SEED,
        "question": "What is the all day of the event where label is 'Team Standup Meeting'?",
        "expected_answer": "false",
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


def load_autocalendar_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
