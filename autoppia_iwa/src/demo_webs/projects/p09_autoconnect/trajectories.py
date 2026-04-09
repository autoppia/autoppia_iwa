"""
Golden trajectories for Autoppia AutoConnect (``autoconnect``, web_9).

Per-use-case ``prompt`` and ``tests`` are static literals below (no JSON load).
Seeds match ``autoconnect_tasks.json`` in this package (``?seed=`` on ``http://localhost:8008``).

Base URL: ``http://localhost:8008``.
"""

from __future__ import annotations

PROJECT_NUMBER = 9
WEB_PROJECT_ID = "autoconnect"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions import (
    ClickAction,
    NavigateAction,
    SelectDropDownOptionAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

BASE = "http://localhost:8008"
DEFAULT_SEED = 1

# Seeds from autoconnect_tasks.json
SEED_VIEW_USER_PROFILE = 134
SEED_CONNECT_WITH_USER = 868
SEED_POST_STATUS = 654
SEED_LIKE_POST = 423
SEED_COMMENT_ON_POST = 18
SEED_SAVE_POST = 13
SEED_HIDE_POST = 361
SEED_VIEW_SAVED_POSTS = 148
SEED_VIEW_APPLIED_JOBS = 880
SEED_CANCEL_APPLICATION = 428
SEED_EDIT_PROFILE = 824
SEED_EDIT_EXPERIENCE = 326
SEED_ADD_EXPERIENCE = 667
SEED_REMOVE_POST = 282
SEED_VIEW_HIDDEN_POSTS = 547
SEED_UNHIDE_POST = 13
SEED_SEARCH_USERS = 551
SEED_FOLLOW_PAGE = 557
SEED_UNFOLLOW_PAGE = 406
SEED_VIEW_JOB = 409
SEED_FILTER_JOBS = 209
SEED_BACK_TO_ALL_JOBS = 665
SEED_APPLY_FOR_JOB = 806
SEED_SEARCH_JOBS = 61
SEED_HOME_NAVBAR = 809
SEED_JOBS_NAVBAR = 523

# Copy-paste strings aligned with prompts / static dataset
_ABOUT_TARGET = (
    "Hello! I'm Andrew, a senior ux designer with expertise in user-centered design. "
    "I'm passionate about accessibility and inclusive design. I'm always learning and "
    "exploring new trends and technologies in my field."
)
_POST_WEEKEND = "Weekend getaway was exactly what I needed. Sometimes a change of scenery makes all the difference."
_POST_PERSONAL_BEST = "Personal best today! Progress feels good."
_POST_FRIDAY = "Friday vibes! Another productive week in the books."
_BIRTHDAY_POST = "Birthday wishes are making my day! Thank you to everyone who reached out."
_POST_STATUS_SAFE = "IWA trajectory: status update (not the React Summit line)."


def _home(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/?seed={seed}"


def _path(seed: int, path: str) -> str:
    p = path.strip().lstrip("/")
    return f"{BASE}/{p}?seed={seed}" if p else _home(seed)


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


def _task_entry(seed: int) -> list[BaseAction]:
    return [NavigateAction(url=_home(seed)), WaitAction(time_seconds=1.0)]


def _user_search_input() -> Selector:
    return _xp("(//*[@id='search-input' or @id='user-search' or @id='people-search'])[1]")


def _post_article_contains_text(fragment: str) -> str:
    """Scope to a feed ``article`` whose body contains ``fragment`` (substring match)."""
    if "'" in fragment:
        escaped = fragment.replace("'", "',\"'\",'")
        pred = f"contains(normalize-space(.),concat({escaped}))"
    else:
        pred = f"contains(normalize-space(.), '{fragment}')"
    return f"(//article[.//p[{pred}]])[1]"


def _like_in_article(article_xpath: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_xp(f"{article_xpath}//button[.//path[contains(@d,'M12 21.35')]][1]")),
        WaitAction(time_seconds=0.45),
    ]


def _save_in_article(article_xpath: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_xp(f"{article_xpath}//button[.//path[contains(@d,'M6 3h12a1')]][1]")),
        WaitAction(time_seconds=0.45),
    ]


def _hide_in_article(article_xpath: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_xp(f"{article_xpath}//button[.//path[contains(@d,'M3 12s3.5-6')]][1]")),
        WaitAction(time_seconds=0.45),
    ]


def _comment_first_visible_post(text: str) -> list[BaseAction]:
    ta = _xp("(//article//textarea[contains(@placeholder,'comment') or contains(@placeholder,'Comment') or contains(@placeholder,'reply') or contains(@placeholder,'Reply')])[1]")
    return [
        ClickAction(selector=ta),
        WaitAction(time_seconds=0.25),
        TypeAction(selector=ta, text=text),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp("(//article//button[@type='submit' and .//path[contains(@d,'M3 20l18')]])[1]")),
        WaitAction(time_seconds=0.5),
    ]


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


# --- Flows: entry URL uses task seed; steps match UI in web_9_autoconnect. ---

_x_weekend = _post_article_contains_text("Weekend getaway was exactly what I needed")
_x_personal = _post_article_contains_text("Personal best today! Progress feels good.")
_x_friday = _post_article_contains_text("Friday vibes! Another productive week")
_x_hide_candidate = f"(//article[not(contains(translate(normalize-space((.//div[contains(@class,'font-semibold')])[1]),'HJM','hjm'),'hjm')) and .//p[normalize-space(.)!='{_BIRTHDAY_POST}'])[1]"

_JOBS_APPLIED_LINK = _xp("(//a[contains(@href,'/jobs/applied')])[1]")
_APPLY_JOB_J5_BTN = _xp("(//*[contains(@href,'/jobs/j5') or contains(@id,'job_card_j5')])[1]//button[contains(normalize-space(.),'Apply') and not(contains(normalize-space(.),'Applied'))]")
_APPLY_NOW_ON_DETAIL = _xp(
    "(//section//button[contains(normalize-space(.),'Apply Now') "
    "or (contains(normalize-space(.),'Apply') or (contains(normalize-space(.),'Submit Application') and not(contains(normalize-space(.),'Applied')))])[1]"
)
_CANCEL_APP_ON_DETAIL = _xp("//button[contains(normalize-space(.),'Cancel application')]")
_BACK_TO_ALL_JOBS_LINK = _xp("//a[contains(@href,'/jobs')][contains(normalize-space(.),'Back')]")

VIEW_USER_PROFILE = _uc(
    "VIEW_USER_PROFILE",
    [
        *_task_entry(SEED_VIEW_USER_PROFILE),
        ClickAction(selector=_id("nav_profile")),
        WaitAction(time_seconds=0.9),
    ],
)

CONNECT_WITH_USER = _uc(
    "CONNECT_WITH_USER",
    [
        *_task_entry(SEED_CONNECT_WITH_USER),
        NavigateAction(url=_path(SEED_CONNECT_WITH_USER, "profile/bella.hernandez")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("html/body/div[2]/main/span/section/div[1]/div/div[1]/button")),
        WaitAction(time_seconds=0.6),
    ],
)

POST_STATUS = _uc(
    "POST_STATUS",
    [
        *_task_entry(SEED_POST_STATUS),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/main/section/div[1]/div/button[1]")),
        WaitAction(time_seconds=0.45),
        TypeAction(
            selector=_xp("//html/body/div[2]/main/div/div/form/div[2]/textarea"),
            text=_POST_STATUS_SAFE,
        ),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/div/form/div[3]/button")),
        WaitAction(time_seconds=0.6),
    ],
)

LIKE_POST = _uc(
    "LIKE_POST",
    [
        *_task_entry(SEED_LIKE_POST),
        # *_like_in_article(_x_personal),
        ClickAction(selector=_xp("//html/body/div[3]/main/div/main/section/div[2]/article[45]/div[3]/button")),
        WaitAction(time_seconds=0.3),
    ],
)

COMMENT_ON_POST = _uc(
    "COMMENT_ON_POST",
    [
        *_task_entry(SEED_COMMENT_ON_POST),
        # *_comment_first_visible_post("Great job, keep it up!"),
        TypeAction(selector=_xp("//html/body/div[2]/main/div/main/section/div[2]/article[1]/form/textarea"), text="Great job, keep it up!"),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/main/section/div[2]/article[1]/form/button")),
        WaitAction(time_seconds=0.2),
    ],
)

SAVE_POST = _uc(
    "SAVE_POST",
    [
        NavigateAction(url="http://localhost:8008/profile/michelle.romero?seed=13"),
        ClickAction(selector=_xp('//*[@id="feed-card"]/div[1]/div[2]/button[1]')),
        WaitAction(time_seconds=0.3),
    ],
)

HIDE_POST = _uc(
    "HIDE_POST",
    [
        *_task_entry(SEED_HIDE_POST),
        # *_hide_in_article(_x_hide_candidate),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/main/section/div[2]/article[1]/div[1]/div[2]/button[2]")),
        WaitAction(time_seconds=0.3),
    ],
)

VIEW_SAVED_POSTS = _uc(
    "VIEW_SAVED_POSTS",
    [
        NavigateAction(url=_path(SEED_VIEW_SAVED_POSTS, "/")),
        ClickAction(selector=_xp("//*[@id='left_sidebar']/a[1]")),
        WaitAction(time_seconds=1.0),
    ],
)

VIEW_APPLIED_JOBS = _uc(
    "VIEW_APPLIED_JOBS",
    [
        NavigateAction(url=_path(SEED_VIEW_APPLIED_JOBS, "jobs/")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp('//*[@id="all-jobs-link"]')),
        WaitAction(time_seconds=0.4),
    ],
)

CANCEL_APPLICATION = _uc(
    "CANCEL_APPLICATION",
    [
        NavigateAction(url=_path(SEED_CANCEL_APPLICATION, "jobs/j62")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//html/body/div[2]/main/section/div[1]/div/div[2]/div[4]/div[2]/button")),
        WaitAction(time_seconds=0.55),
        # NavigateAction(url=_path(SEED_CANCEL_APPLICATION, "jobs/applied")),
        ClickAction(selector=_CANCEL_APP_ON_DETAIL),
        WaitAction(time_seconds=0.6),
    ],
)

_EDIT_PROFILE_HEADER_BTN = _xp("//div[contains(@class,'rounded-xl shadow-lg')]//button[contains(normalize-space(.),'Modify profile') or contains(normalize-space(.),'Save profile')][1]")
_ABOUT_EDIT_BTN = _xp("//h3[contains(normalize-space(.),'About')]/following::button[contains(.,'Edit') or contains(.,'Save')][1]")
_ABOUT_TEXTAREA = _xp("//html/body/div[2]/main/span[2]/section/div[2]/textarea")

EDIT_PROFILE = _uc(
    "EDIT_PROFILE",
    [
        NavigateAction(url=_path(SEED_EDIT_PROFILE, "profile/me")),
        WaitAction(time_seconds=1.2),
        ClickAction(selector=_EDIT_PROFILE_HEADER_BTN),
        WaitAction(time_seconds=0.35),
        TypeAction(
            selector=_xp("//html/body/div[2]/main/span[2]/section/div[1]/div/div[1]/div[1]/input"),
            text="Andrew Kim",
        ),
        TypeAction(
            selector=_xp("(//div[contains(@class,'text-blue-600')]//input[@class])[1]"),
            text="Senior UX Designer",
        ),
        TypeAction(
            selector=_xp("(//div[contains(@class,'text-gray-600 text-base')]//input[@class])[1]"),
            text="Product design and systems thinking.",
        ),
        ClickAction(selector=_EDIT_PROFILE_HEADER_BTN),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_ABOUT_EDIT_BTN),
        WaitAction(time_seconds=0.35),
        TypeAction(selector=_ABOUT_TEXTAREA, text=_ABOUT_TARGET),
        ClickAction(selector=_ABOUT_EDIT_BTN),
        WaitAction(time_seconds=0.5),
    ],
)

_EXP_EDIT_BTN = _xp("//h3[contains(normalize-space(.),'Career')]/following::button[contains(.,'Edit') or contains(.,'Save')][1]")
_SAVE_EXP_BTN = _xp("//button[contains(normalize-space(.),'Save changes')]")

EDIT_EXPERIENCE = _uc(
    "EDIT_EXPERIENCE",
    [
        NavigateAction(url=_path(SEED_EDIT_EXPERIENCE, "profile/me")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_EXP_EDIT_BTN),
        WaitAction(time_seconds=0.4),
        TypeAction(
            selector=_xp("(//div[contains(@class,'border-b')][.//input[@placeholder='Title']])[1]//input[@placeholder='Title']"),
            text="Product Designer",
        ),
        TypeAction(
            selector=_xp("(//div[contains(@class,'border-b')][.//input[@placeholder='Duration']])[1]//input[@placeholder='Duration']"),
            text="Jan 2020 - Present",
        ),
        TypeAction(
            selector=_xp("(//div[contains(@class,'border-b')][.//input[@placeholder='Location']])[1]//input[@placeholder='Location']"),
            text="San Francisco, CA",
        ),
        TypeAction(
            selector=_xp("(//div[contains(@class,'border-b')][.//textarea[@placeholder='Description']])[1]//textarea[@placeholder='Description']"),
            text="Leading design sprints and signal quality for releases.",
        ),
        ClickAction(selector=_SAVE_EXP_BTN),
        WaitAction(time_seconds=0.6),
    ],
)

ADD_EXPERIENCE = _uc(
    "ADD_EXPERIENCE",
    [
        NavigateAction(url=_path(SEED_ADD_EXPERIENCE, "profile/me")),
        WaitAction(time_seconds=1.2),
        ClickAction(selector=_xp("//button[contains(normalize-space(.),'Add experience')]")),
        WaitAction(time_seconds=0.45),
        TypeAction(
            selector=_xp("(//input[@placeholder='Title'])[last()]"),
            text="DevOps Engineer",
        ),
        TypeAction(
            selector=_xp("(//input[@placeholder='Company'])[last()]"),
            text="Apple",
        ),
        TypeAction(
            selector=_xp("(//input[@placeholder='Duration'])[last()]"),
            text="Sep 2022 - Present • 3 yrs 4 mos",
        ),
        TypeAction(
            selector=_xp("(//input[@placeholder='Location'])[last()]"),
            text="Raleigh, NC",
        ),
        TypeAction(
            selector=_xp("(//textarea[@placeholder='Description'])[last()]"),
            text="iOS features and performance work.",
        ),
        ClickAction(selector=_xp("//button[contains(normalize-space(.),'Save experience')]")),
        WaitAction(time_seconds=0.7),
    ],
)

REMOVE_POST = _uc(
    "REMOVE_POST",
    [
        NavigateAction(url=_path(SEED_REMOVE_POST, "/profile/jack.rogers")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//html/body/div[2]/main/span[1]/section/div[4]/div[2]/article/div[1]/div[2]/button[1]")),
        NavigateAction(url=_path(SEED_REMOVE_POST, "saved")),
        ClickAction(selector=_xp("//html/body/div[2]/main/section/div/div/span[2]/div/button")),
        WaitAction(time_seconds=0.5),
    ],
)

VIEW_HIDDEN_POSTS = _uc(
    "VIEW_HIDDEN_POSTS",
    [
        NavigateAction(url=_path(SEED_VIEW_HIDDEN_POSTS, "hidden")),
        WaitAction(time_seconds=1.0),
    ],
)

_x_personal_proj = _post_article_contains_text("personal projec")

UNHIDE_POST = _uc(
    "UNHIDE_POST",
    [
        NavigateAction(url=_path(SEED_UNHIDE_POST, "/profile/stephanie.hansen")),
        WaitAction(time_seconds=0.9),
        ClickAction(selector=_xp("//html/body/div[2]/main/span/section/div[4]/div[2]/article/div[1]/div[2]/button[2]")),
        NavigateAction(url=_path(SEED_UNHIDE_POST, "hidden")),
        ClickAction(selector=_xp("//html/body/div[2]/main/section/div[2]/div/div[1]/button")),
        WaitAction(time_seconds=0.5),
    ],
)

SEARCH_USERS = _uc(
    "SEARCH_USERS",
    [
        *_task_entry(SEED_SEARCH_USERS),
        ClickAction(selector=_user_search_input()),
        TypeAction(selector=_user_search_input(), text="Mobile Developer (iOS/Android)"),
        WaitAction(time_seconds=0.45),
    ],
)

FOLLOW_PAGE = _uc(
    "FOLLOW_PAGE",
    [
        NavigateAction(url=_path(SEED_FOLLOW_PAGE, "recommendations")),
        WaitAction(time_seconds=1.0),
        ClickAction(
            selector=_xp(
                "(//li[contains(@class,'shadow')]"
                "[not(contains(translate(.//div[contains(@class,'font-semibold')][1],"
                "'JOQ','joq'),'joq'))]"
                "//button[contains(normalize-space(.),'Follow') and not(contains(.,'Following'))])[1]"
            )
        ),
        WaitAction(time_seconds=0.5),
    ],
)

UNFOLLOW_PAGE = _uc(
    "UNFOLLOW_PAGE",
    [
        NavigateAction(url=_path(SEED_UNFOLLOW_PAGE, "recommendations")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/main/section/ul/div[2]/li/button")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp("//html/body/div[2]/main/div/main/section/ul/div[2]/li/button")),
        WaitAction(time_seconds=0.5),
    ],
)

VIEW_JOB = _uc(
    "VIEW_JOB",
    [
        NavigateAction(url=_path(SEED_VIEW_JOB, "jobs/j34")),
        WaitAction(time_seconds=1.0),
    ],
)

_JOBS_LOC_SELECT = _xp("//label[contains(normalize-space(.),'Location')]/following::select[1]")
_JOBS_SALARY_SELECT = _xp("//label[contains(normalize-space(.),'Salary')]/following::select[1]")

FILTER_JOBS = _uc(
    "FILTER_JOBS",
    [
        NavigateAction(url=_path(SEED_FILTER_JOBS, "jobs")),
        WaitAction(time_seconds=1.0),
        SelectDropDownOptionAction(selector=_JOBS_LOC_SELECT, text="San Francisco, CA"),
        WaitAction(time_seconds=0.4),
        SelectDropDownOptionAction(selector=_JOBS_SALARY_SELECT, text="Under $50,000"),
        WaitAction(time_seconds=0.6),
    ],
)

BACK_TO_ALL_JOBS = _uc(
    "BACK_TO_ALL_JOBS",
    [
        NavigateAction(url=_path(SEED_BACK_TO_ALL_JOBS, "jobs/j9")),
        WaitAction(time_seconds=1.0),
        ClickAction(selector=_xp("//a[contains(@href,'/jobs')][contains(normalize-space(.),'Back')]")),
        WaitAction(time_seconds=0.6),
    ],
)

APPLY_FOR_JOB = _uc(
    "APPLY_FOR_JOB",
    [
        NavigateAction(url=_path(SEED_APPLY_FOR_JOB, "jobs")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//html/body/div[2]/main/section/div[6]/a[12]/span[3]/button")),
        WaitAction(time_seconds=0.55),
    ],
)

_JOBS_SEARCH = _xp("(//*[@id='jobs_search_input' or contains(@id,'jobs-search') or contains(@id,'job_search')])[1]")

SEARCH_JOBS = _uc(
    "SEARCH_JOBS",
    [
        NavigateAction(url=_path(SEED_SEARCH_JOBS, "jobs")),
        WaitAction(time_seconds=1.0),
        ClickAction(selector=_JOBS_SEARCH),
        TypeAction(selector=_JOBS_SEARCH, text="Innovation Studio"),
        WaitAction(time_seconds=0.45),
    ],
)

HOME_NAVBAR = _uc(
    "HOME_NAVBAR",
    [
        NavigateAction(url=_path(SEED_HOME_NAVBAR, "jobs")),
        WaitAction(time_seconds=0.7),
        ClickAction(selector=_id("nav-feed")),
        WaitAction(time_seconds=0.4),
    ],
)

JOBS_NAVBAR = _uc(
    "JOBS_NAVBAR",
    [
        *_task_entry(SEED_JOBS_NAVBAR),
        ClickAction(selector=_id("nav-careers")),
        WaitAction(time_seconds=0.4),
    ],
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
