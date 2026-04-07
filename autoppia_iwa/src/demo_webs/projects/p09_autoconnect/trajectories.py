"""
Golden trajectories for Autoppia AutoConnect (``autoconnect``, web_9).

Per-use-case ``prompt`` and ``tests`` are static literals below (no JSON load).
``actions`` are empty until concrete flows are scripted.

Base URL: ``http://localhost:8008``.
"""

from __future__ import annotations

PROJECT_NUMBER = 9
WEB_PROJECT_ID = "autoconnect"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.base import BaseAction

BASE = "http://localhost:8008"

_PROMPTS: dict[str, str] = {
    "VIEW_USER_PROFILE": "View the profile of user where name equals 'Brian Griffith'.",
    "CONNECT_WITH_USER": "Connect with a user whose target_name does NOT contain 'zxz'",
    "POST_STATUS": "Post a status update where the content is NOT 'Attending React Summit next month—who else is going?'",
    "LIKE_POST": "Like the post where the poster_content equals 'Personal best today! Progress feels good.'",
    "COMMENT_ON_POST": "Comment on the post where the comment_text contains 'job, keep it up!'",
    "SAVE_POST": "Save the post where the content equals 'Weekend getaway was exactly what I needed. Sometimes a change of scenery makes all the difference.'",
    "HIDE_POST": "Hide this post where the author does NOT contain 'hjm' and the content does NOT equal 'Birthday wishes are making my day! Thank you to everyone who reached out.'",
    "VIEW_SAVED_POSTS": "Show me my saved posts list.",
    "VIEW_APPLIED_JOBS": "Show me the jobs I have applied to.",
    "CANCEL_APPLICATION": "Cancel application for a position where the job_title is NOT 'UI Designer'",
    "EDIT_PROFILE": "Edit profile to ensure the name is NOT 'Charles Cruz', the about section equals "
    "'Hello! I'm Andrew, a senior ux designer with expertise in user-centered design. "
    "I'm passionate about accessibility and inclusive design. I'm always learning and "
    "exploring new trends and technologies in my field.', the bio does NOT contain "
    "'ksf', and the title does NOT contain 'qox'.",
    "EDIT_EXPERIENCE": "Edit experience to ensure the duration does NOT contain 'yor', the title is "
    "NOT equal to 'Design Lead', the description contains 'sig', and the location "
    "does NOT contain 'pih'.",
    "ADD_EXPERIENCE": "Add experience at a company that equals 'Apple' with a duration of 'Sep 2022 - "
    "Present • 3 yrs 4 mos', a title that contains 's En', a location that contains "
    "'gh, N', and a description that does NOT contain 'ums'.",
    "REMOVE_POST": "Remove post where the author does NOT contain 'nlv' and the content equals 'Friday vibes! Another productive week in the books.'",
    "VIEW_HIDDEN_POSTS": "View the hidden posts that I have previously hidden.",
    "UNHIDE_POST": "Unhide the post where the content CONTAINS 'personal projec'.",
    "SEARCH_USERS": "Search for users with the query equals 'Mobile Developer (iOS/Android)'",
    "FOLLOW_PAGE": "Follow a company page where the recommendation does NOT contain 'joq'.",
    "UNFOLLOW_PAGE": "Unfollow the company page where the recommendation contains 'Manag'",
    "VIEW_JOB": "View the job details for a position where the job_title CONTAINS 't', the company is 'Digital Innovations', and the location does NOT CONTAIN 'kys'.",
    "FILTER_JOBS": "Filter jobs where the location does NOT contain 'qdx', the salary does NOT contain 'cco', and the remote status is NOT equal to 'True'.",
    "BACK_TO_ALL_JOBS": "Go back to all jobs where the company equals 'Tech Innovations'.",
    "APPLY_FOR_JOB": "Apply for a job in 'Salt Lake City, UT'.",
    "SEARCH_JOBS": "Search for jobs with the query equals 'Innovation Studio'",
    "HOME_NAVBAR": "Go to the Home tab from the navbar.",
    "JOBS_NAVBAR": "Open the Jobs tab from the navbar.",
}

_RAW_TESTS: dict[str, list[dict]] = {
    "VIEW_USER_PROFILE": [{"type": "CheckEventTest", "event_name": "VIEW_USER_PROFILE", "event_criteria": {"name": "Brian Griffith"}, "description": "Check if specific event was triggered"}],
    "CONNECT_WITH_USER": [
        {
            "type": "CheckEventTest",
            "event_name": "CONNECT_WITH_USER",
            "event_criteria": {"target_name": {"operator": "not_contains", "value": "zxz"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "POST_STATUS": [
        {
            "type": "CheckEventTest",
            "event_name": "POST_STATUS",
            "event_criteria": {"content": {"operator": "not_equals", "value": "Attending React Summit next month—who else is going?"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "LIKE_POST": [
        {"type": "CheckEventTest", "event_name": "LIKE_POST", "event_criteria": {"poster_content": "Personal best today! Progress feels good."}, "description": "Check if specific event was triggered"}
    ],
    "COMMENT_ON_POST": [
        {
            "type": "CheckEventTest",
            "event_name": "COMMENT_ON_POST",
            "event_criteria": {"comment_text": {"operator": "contains", "value": "job, keep it up!"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SAVE_POST": [
        {
            "type": "CheckEventTest",
            "event_name": "SAVE_POST",
            "event_criteria": {"content": "Weekend getaway was exactly what I needed. Sometimes a change of scenery makes all the difference."},
            "description": "Check if specific event was triggered",
        }
    ],
    "HIDE_POST": [
        {
            "type": "CheckEventTest",
            "event_name": "HIDE_POST",
            "event_criteria": {
                "author": {"operator": "not_contains", "value": "hjm"},
                "content": {"operator": "not_equals", "value": "Birthday wishes are making my day! Thank you to everyone who reached out."},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_SAVED_POSTS": [{"type": "CheckEventTest", "event_name": "VIEW_SAVED_POSTS", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "VIEW_APPLIED_JOBS": [{"type": "CheckEventTest", "event_name": "VIEW_APPLIED_JOBS", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CANCEL_APPLICATION": [
        {
            "type": "CheckEventTest",
            "event_name": "CANCEL_APPLICATION",
            "event_criteria": {"job_title": {"operator": "not_equals", "value": "UI Designer"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_PROFILE": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_PROFILE",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "Charles Cruz"},
                "about": "Hello! I'm Andrew, a senior ux designer with "
                "expertise in user-centered design. I'm passionate "
                "about accessibility and inclusive design. I'm "
                "always learning and exploring new trends and "
                "technologies in my field.",
                "bio": {"operator": "not_contains", "value": "ksf"},
                "title": {"operator": "not_contains", "value": "qox"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_EXPERIENCE": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_EXPERIENCE",
            "event_criteria": {
                "duration": {"operator": "not_contains", "value": "yor"},
                "title": {"operator": "not_equals", "value": "Design Lead"},
                "description": {"operator": "contains", "value": "sig"},
                "location": {"operator": "not_contains", "value": "pih"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_EXPERIENCE": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_EXPERIENCE",
            "event_criteria": {
                "company": "Apple",
                "duration": "Sep 2022 - Present • 3 yrs 4 mos",
                "title": {"operator": "contains", "value": "s En"},
                "location": {"operator": "contains", "value": "gh, N"},
                "description": {"operator": "not_contains", "value": "ums"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REMOVE_POST": [
        {
            "type": "CheckEventTest",
            "event_name": "REMOVE_POST",
            "event_criteria": {"author": {"operator": "not_contains", "value": "nlv"}, "content": "Friday vibes! Another productive week in the books."},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_HIDDEN_POSTS": [{"type": "CheckEventTest", "event_name": "VIEW_HIDDEN_POSTS", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "UNHIDE_POST": [
        {
            "type": "CheckEventTest",
            "event_name": "UNHIDE_POST",
            "event_criteria": {"content": {"operator": "contains", "value": "personal projec"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_USERS": [{"type": "CheckEventTest", "event_name": "SEARCH_USERS", "event_criteria": {"query": "Mobile Developer (iOS/Android)"}, "description": "Check if specific event was triggered"}],
    "FOLLOW_PAGE": [
        {
            "type": "CheckEventTest",
            "event_name": "FOLLOW_PAGE",
            "event_criteria": {"recommendation": {"operator": "not_contains", "value": "joq"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "UNFOLLOW_PAGE": [
        {
            "type": "CheckEventTest",
            "event_name": "UNFOLLOW_PAGE",
            "event_criteria": {"recommendation": {"operator": "contains", "value": "Manag"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_JOB": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_JOB",
            "event_criteria": {"job_title": {"operator": "contains", "value": "t"}, "company": "Digital Innovations", "location": {"operator": "not_contains", "value": "kys"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "FILTER_JOBS": [
        {
            "type": "CheckEventTest",
            "event_name": "FILTER_JOBS",
            "event_criteria": {"location": {"operator": "not_contains", "value": "qdx"}, "salary": {"operator": "not_contains", "value": "cco"}, "remote": {"operator": "not_equals", "value": True}},
            "description": "Check if specific event was triggered",
        }
    ],
    "BACK_TO_ALL_JOBS": [{"type": "CheckEventTest", "event_name": "BACK_TO_ALL_JOBS", "event_criteria": {"company": "Tech Innovations"}, "description": "Check if specific event was triggered"}],
    "APPLY_FOR_JOB": [{"type": "CheckEventTest", "event_name": "APPLY_FOR_JOB", "event_criteria": {"location": "Salt Lake City, UT"}, "description": "Check if specific event was triggered"}],
    "SEARCH_JOBS": [{"type": "CheckEventTest", "event_name": "SEARCH_JOBS", "event_criteria": {"query": "Innovation Studio"}, "description": "Check if specific event was triggered"}],
    "HOME_NAVBAR": [{"type": "CheckEventTest", "event_name": "HOME_NAVBAR", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "JOBS_NAVBAR": [{"type": "CheckEventTest", "event_name": "JOBS_NAVBAR", "event_criteria": {}, "description": "Check if specific event was triggered"}],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(
        name=use_case,
        prompt=_PROMPTS[use_case],
        actions=actions,
        tests=_TESTS[use_case],
    )


# --- One trajectory per use case (canonical JSON order); fill ``actions`` later. ---

VIEW_USER_PROFILE = _uc(
    "VIEW_USER_PROFILE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

CONNECT_WITH_USER = _uc(
    "CONNECT_WITH_USER",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

POST_STATUS = _uc(
    "POST_STATUS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

LIKE_POST = _uc(
    "LIKE_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

COMMENT_ON_POST = _uc(
    "COMMENT_ON_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

SAVE_POST = _uc(
    "SAVE_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

HIDE_POST = _uc(
    "HIDE_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

VIEW_SAVED_POSTS = _uc(
    "VIEW_SAVED_POSTS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

VIEW_APPLIED_JOBS = _uc(
    "VIEW_APPLIED_JOBS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

CANCEL_APPLICATION = _uc(
    "CANCEL_APPLICATION",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

EDIT_PROFILE = _uc(
    "EDIT_PROFILE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

EDIT_EXPERIENCE = _uc(
    "EDIT_EXPERIENCE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

ADD_EXPERIENCE = _uc(
    "ADD_EXPERIENCE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

REMOVE_POST = _uc(
    "REMOVE_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

VIEW_HIDDEN_POSTS = _uc(
    "VIEW_HIDDEN_POSTS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

UNHIDE_POST = _uc(
    "UNHIDE_POST",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

SEARCH_USERS = _uc(
    "SEARCH_USERS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

FOLLOW_PAGE = _uc(
    "FOLLOW_PAGE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

UNFOLLOW_PAGE = _uc(
    "UNFOLLOW_PAGE",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

VIEW_JOB = _uc(
    "VIEW_JOB",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

FILTER_JOBS = _uc(
    "FILTER_JOBS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

BACK_TO_ALL_JOBS = _uc(
    "BACK_TO_ALL_JOBS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

APPLY_FOR_JOB = _uc(
    "APPLY_FOR_JOB",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

SEARCH_JOBS = _uc(
    "SEARCH_JOBS",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

HOME_NAVBAR = _uc(
    "HOME_NAVBAR",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)

JOBS_NAVBAR = _uc(
    "JOBS_NAVBAR",
    [],  # TODO: scripted actions (use task URL / seed from when tasks were materialized)
)


def load_autoconnect_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "VIEW_USER_PROFILE": VIEW_USER_PROFILE,
        "CONNECT_WITH_USER": CONNECT_WITH_USER,
        "POST_STATUS": POST_STATUS,
        "LIKE_POST": LIKE_POST,
        "COMMENT_ON_POST": COMMENT_ON_POST,
        "SAVE_POST": SAVE_POST,
        "HIDE_POST": HIDE_POST,
        "VIEW_SAVED_POSTS": VIEW_SAVED_POSTS,
        "VIEW_APPLIED_JOBS": VIEW_APPLIED_JOBS,
        "CANCEL_APPLICATION": CANCEL_APPLICATION,
        "EDIT_PROFILE": EDIT_PROFILE,
        "EDIT_EXPERIENCE": EDIT_EXPERIENCE,
        "ADD_EXPERIENCE": ADD_EXPERIENCE,
        "REMOVE_POST": REMOVE_POST,
        "VIEW_HIDDEN_POSTS": VIEW_HIDDEN_POSTS,
        "UNHIDE_POST": UNHIDE_POST,
        "SEARCH_USERS": SEARCH_USERS,
        "FOLLOW_PAGE": FOLLOW_PAGE,
        "UNFOLLOW_PAGE": UNFOLLOW_PAGE,
        "VIEW_JOB": VIEW_JOB,
        "FILTER_JOBS": FILTER_JOBS,
        "BACK_TO_ALL_JOBS": BACK_TO_ALL_JOBS,
        "APPLY_FOR_JOB": APPLY_FOR_JOB,
        "SEARCH_JOBS": SEARCH_JOBS,
        "HOME_NAVBAR": HOME_NAVBAR,
        "JOBS_NAVBAR": JOBS_NAVBAR,
    }
