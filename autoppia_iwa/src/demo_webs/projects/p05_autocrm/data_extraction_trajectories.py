from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "autocrm"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "VIEW_MATTER_DETAILS",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "DELETE_MATTER",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "ARCHIVE_MATTER",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "VIEW_CLIENT_DETAILS",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "SEARCH_CLIENT",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "DOCUMENT_DELETED",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "LOG_DELETE",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "SEARCH_MATTER",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "DELETE_CLIENT",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "FILTER_CLIENTS",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "FILTER_MATTER_STATUS",
        "seed": SEED,
        "question": "What is the client of the matter where name is 'Corporate Merger'?",
        "expected_answer": "TechCorp Industries",
    },
    {
        "use_case": "UPDATE_MATTER",
        "seed": SEED,
        "question": "What is the updated of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Today",
    },
    {
        "use_case": "DOCUMENT_RENAMED",
        "seed": SEED,
        "question": "What is the name of the matter where client is 'TechCorp Industries' and updated is 'Today'?",
        "expected_answer": "Corporate Merger",
    },
    {
        "use_case": "LOG_EDITED",
        "seed": SEED,
        "question": "What is the status of the matter where name is 'Corporate Merger'?",
        "expected_answer": "Active",
    },
    {
        "use_case": "BILLING_SEARCH",
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
