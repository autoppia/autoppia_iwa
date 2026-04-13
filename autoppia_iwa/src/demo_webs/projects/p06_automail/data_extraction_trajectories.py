from __future__ import annotations

from autoppia_iwa.src.demo_webs.classes import DataExtractionTrajectory

SEED = 1
PROJECT_ID = "automail"

_TRAJECTORY_SPECS: list[dict[str, str | int]] = [
    {
        "use_case": "SEARCH_EMAIL",
        "seed": SEED,
        "question": "In the dataset, who sent the email with subject 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "Michael Chen",
    },
    {
        "use_case": "TEMPLATE_SELECTED",
        "seed": SEED,
        "question": "In the dataset, what recipient email is listed for 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "me@gmail.com",
    },
    {
        "use_case": "TEMPLATE_BODY_EDITED",
        "seed": SEED,
        "question": "In the dataset, what is the subject of the email whose snippet says 'The design mockups for the new website are ready...'?",
        "expected_answer": "Re: Design Mockups Ready for Review",
    },
    {
        "use_case": "TEMPLATE_SENT",
        "seed": SEED,
        "question": "In the dataset, what snippet is shown for the email titled 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "The design mockups for the new website are ready...",
    },
    {
        "use_case": "TEMPLATE_SAVED_DRAFT",
        "seed": SEED,
        "question": "In the dataset, what timestamp is recorded for 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "2025-12-01T10:30:00Z",
    },
    {
        "use_case": "TEMPLATE_CANCELED",
        "seed": SEED,
        "question": "In the dataset, is the email 'Re: Design Mockups Ready for Review' marked as read?",
        "expected_answer": "true",
    },
    {
        "use_case": "VIEW_EMAIL",
        "seed": SEED,
        "question": "In the dataset, is the email 'Re: Design Mockups Ready for Review' marked as starred?",
        "expected_answer": "false",
    },
    {
        "use_case": "ARCHIVE_EMAIL",
        "seed": SEED,
        "question": "In the dataset, is the email 'Re: Design Mockups Ready for Review' marked as starred?",
        "expected_answer": "false",
    },
    {
        "use_case": "STAR_AN_EMAIL",
        "seed": SEED,
        "question": "In the dataset, is the email 'Re: Design Mockups Ready for Review' marked as starred?",
        "expected_answer": "false",
    },
    {
        "use_case": "MARK_EMAIL_AS_IMPORTANT",
        "seed": SEED,
        "question": "In the dataset, is the email 'Re: Design Mockups Ready for Review' marked as starred?",
        "expected_answer": "false",
    },
    {
        "use_case": "MARK_AS_UNREAD",
        "seed": SEED,
        "question": "In the dataset, what is the first label name on 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "Work",
    },
    {
        "use_case": "DELETE_EMAIL",
        "seed": SEED,
        "question": "In the dataset, what category is assigned to 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "primary",
    },
    {
        "use_case": "MARK_AS_SPAM",
        "seed": SEED,
        "question": "In the dataset, what thread ID does 'Re: Design Mockups Ready for Review' belong to?",
        "expected_answer": "thread2",
    },
    {
        "use_case": "EMAIL_SAVE_AS_DRAFT",
        "seed": SEED,
        "question": "In the dataset, what is the filename of the attachment in 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "mockups-v2.pdf",
    },
    {
        "use_case": "EDIT_DRAFT_EMAIL",
        "seed": SEED,
        "question": "In the dataset, who is the sender of 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "Michael Chen",
    },
    {
        "use_case": "REPLY_EMAIL",
        "seed": SEED,
        "question": "In the dataset, what recipient email is listed on 'Re: Design Mockups Ready for Review'?",
        "expected_answer": "me@gmail.com",
    },
    {
        "use_case": "FORWARD_EMAIL",
        "seed": SEED,
        "question": "In the dataset, what is the subject of the email whose snippet says 'The design mockups for the new website are ready...'?",
        "expected_answer": "Re: Design Mockups Ready for Review",
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


def load_automail_data_extraction_trajectories() -> list[DataExtractionTrajectory]:
    return [_build_trajectory(spec) for spec in _TRAJECTORY_SPECS]
