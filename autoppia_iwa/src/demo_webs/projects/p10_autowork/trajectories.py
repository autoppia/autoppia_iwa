"""
Concrete IWA flows for Autoppia AutoWork (web_10).

Prompts and per-flow seeds follow:
  concrete_actions/10_autowork/autowork_tasks.json

Base URL: http://localhost:8009 (each task's url in autowork_tasks.json includes ?seed=).
"""

from __future__ import annotations

PROJECT_NUMBER = 10
WEB_PROJECT_ID = "autowork"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    SelectAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

# BASE = "https://autowork.webs.autoppia.com"
BASE = "http://localhost:8009"
# From autowork_tasks.json (?seed= on BOOK_A_CONSULTATION task URL)
SEED_BOOK_A_CONSULTATION = 641
SEED_HIRE_BTN_CLICKED = 412
SEED_HIRE_LATER_ADDED = 481
SEED_HIRE_LATER_REMOVED = 657
SEED_HIRE_LATER_START = 225
SEED_QUICK_HIRE = 642
SEED_SELECT_HIRING_TEAM = 778
SEED_HIRE_CONSULTANT = 391
SEED_CANCEL_HIRE = 636
SEED_POST_A_JOB = 783
SEED_WRITE_JOB_TITLE = 159
SEED_SEARCH_SKILL = 558
SEED_ADD_SKILL = 106
SEED_CHOOSE_BUDGET_TYPE = 445
SEED_CHOOSE_PROJECT_SIZE = 504
SEED_CHOOSE_PROJECT_TIMELINE = 115
SEED_SET_RATE_RANGE = 359
SEED_WRITE_JOB_DESCRIPTION = 838
SEED_SUBMIT_JOB = 858
SEED_CLOSE_POST_A_JOB_WINDOW = 12
SEED_NAVBAR_PROFILE_CLICK = 959
SEED_NAVBAR_JOBS_CLICK = 188
SEED_NAVBAR_EXPERTS_CLICK = 391
SEED_NAVBAR_FAVORITES_CLICK = 401
SEED_NAVBAR_HIRE_LATER_CLICK = 757
SEED_NAVBAR_HIRES_CLICK = 670
SEED_CONTACT_EXPERT_OPENED = 555
SEED_CONTACT_EXPERT_MESSAGE_SENT = 19
SEED_EDIT_PROFILE_NAME = 580
SEED_EDIT_ABOUT = 482
SEED_EDIT_PROFILE_EMAIL = 729
SEED_EDIT_PROFILE_TITLE = 389
SEED_EDIT_PROFILE_LOCATION = 164
SEED_BROWSE_FAVORITE_EXPERT = 932
SEED_FAVORITE_EXPERT_SELECTED = 134
SEED_FAVORITE_EXPERT_REMOVED = 380

_RAW_TESTS: dict[str, list[dict]] = {
    "BOOK_A_CONSULTATION": [
        {
            "type": "CheckEventTest",
            "event_name": "BOOK_A_CONSULTATION",
            "event_criteria": {
                "rating": {"operator": "not_equals", "value": 4.5},
                "jobs": {"operator": "less_equal", "value": 330},
                "rate": {"operator": "not_equals", "value": "$65.00/hr"},
                "role": {"operator": "contains", "value": "ngine"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "HIRE_BTN_CLICKED": [
        {
            "type": "CheckEventTest",
            "event_name": "HIRE_BTN_CLICKED",
            "event_criteria": {"country": "Denmark", "role": "UX Researcher", "name": "Rachel Foster"},
            "description": "Check if specific event was triggered",
        }
    ],
    "HIRE_LATER_ADDED": [
        {
            "type": "CheckEventTest",
            "event_name": "HIRE_LATER_ADDED",
            "event_criteria": {
                "name": {"operator": "not_contains", "value": "xue"},
                "role": {"operator": "not_equals", "value": "Data Scientist"},
                "country": {"operator": "not_equals", "value": "New Zealand"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "HIRE_LATER_REMOVED": [
        {
            "type": "CheckEventTest",
            "event_name": "HIRE_LATER_REMOVED",
            "event_criteria": {
                "country": {"operator": "not_equals", "value": "South Korea"},
                "name": {"operator": "contains", "value": "l"},
                "role": {"operator": "not_equals", "value": "QA Engineer"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "HIRE_LATER_START": [
        {
            "type": "CheckEventTest",
            "event_name": "HIRE_LATER_START",
            "event_criteria": {"country": {"operator": "contains", "value": "krai"}, "name": {"operator": "not_equals", "value": "Raymond Gonzalez"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "QUICK_HIRE": [
        {
            "type": "CheckEventTest",
            "event_name": "QUICK_HIRE",
            "event_criteria": {"rate": {"operator": "not_equals", "value": "$63.00/hr"}, "role": {"operator": "contains", "value": "Dev"}, "country": {"operator": "not_equals", "value": "Ireland"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SELECT_HIRING_TEAM": [
        {
            "type": "CheckEventTest",
            "event_name": "SELECT_HIRING_TEAM",
            "event_criteria": {"name": "Joshua Turner", "team": {"operator": "contains", "value": "gle"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "HIRE_CONSULTANT": [
        {
            "type": "CheckEventTest",
            "event_name": "HIRE_CONSULTANT",
            "event_criteria": {
                "increaseWhen": {"operator": "contains", "value": "ever"},
                "paymentType": "hourly",
                "rate": {"operator": "not_contains", "value": "rnd"},
                "country": "Canada",
                "increaseHowMuch": {"operator": "contains", "value": "5"},
                "name": {"operator": "not_equals", "value": "Joseph Alexander"},
                "role": {"operator": "contains", "value": "k D"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CANCEL_HIRE": [
        {
            "type": "CheckEventTest",
            "event_name": "CANCEL_HIRE",
            "event_criteria": {
                "name": {"operator": "contains", "value": "is"},
                "rate": {"operator": "contains", "value": ".00/"},
                "country": {"operator": "contains", "value": "South Afri"},
                "role": {"operator": "not_contains", "value": "mzu"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "POST_A_JOB": [{"type": "CheckEventTest", "event_name": "POST_A_JOB", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "WRITE_JOB_TITLE": [
        {"type": "CheckEventTest", "event_name": "WRITE_JOB_TITLE", "event_criteria": {"query": {"operator": "not_contains", "value": "lki"}}, "description": "Check if specific event was triggered"}
    ],
    "SEARCH_SKILL": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_SKILL",
            "event_criteria": {"skill": {"operator": "not_equals", "value": "API Monitoring"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_SKILL": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_SKILL",
            "event_criteria": {"skill": {"operator": "not_equals", "value": "Web Performance Optimization"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CHOOSE_BUDGET_TYPE": [
        {
            "type": "CheckEventTest",
            "event_name": "CHOOSE_BUDGET_TYPE",
            "event_criteria": {"budget_type": {"operator": "not_contains", "value": "ker"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CHOOSE_PROJECT_SIZE": [
        {
            "type": "CheckEventTest",
            "event_name": "CHOOSE_PROJECT_SIZE",
            "event_criteria": {"scope": {"operator": "not_equals", "value": "Small"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CHOOSE_PROJECT_TIMELINE": [
        {"type": "CheckEventTest", "event_name": "CHOOSE_PROJECT_TIMELINE", "event_criteria": {"duration": "More than 6 months"}, "description": "Check if specific event was triggered"}
    ],
    "SET_RATE_RANGE": [
        {
            "type": "CheckEventTest",
            "event_name": "SET_RATE_RANGE",
            "event_criteria": {"rate_from": {"operator": "greater_equal", "value": 39}, "rate_to": {"operator": "greater_than", "value": 77}},
            "description": "Check if specific event was triggered",
        }
    ],
    "WRITE_JOB_DESCRIPTION": [
        {
            "type": "CheckEventTest",
            "event_name": "WRITE_JOB_DESCRIPTION",
            "event_criteria": {"description": "Build and deploy machine learning models for real-world production environments."},
            "description": "Check if specific event was triggered",
        }
    ],
    "SUBMIT_JOB": [
        {
            "type": "CheckEventTest",
            "event_name": "SUBMIT_JOB",
            "event_criteria": {
                "rate_from": {"operator": "less_than", "value": 12},
                "rate_to": {"operator": "not_equals", "value": 61},
                "duration": {"operator": "not_contains", "value": "wdr"},
                "scope": {"operator": "contains", "value": "i"},
                "description": {"operator": "contains", "value": "rove user experience through"},
                "title": "Database Administrators Jobs",
                "skills": {"operator": "contains", "value": "Analysis"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CLOSE_POST_A_JOB_WINDOW": [
        {
            "type": "CheckEventTest",
            "event_name": "CLOSE_POST_A_JOB_WINDOW",
            "event_criteria": {
                "scope": {"operator": "contains", "value": "ediu"},
                "budgetType": {"operator": "not_contains", "value": "hpz"},
                "skills": {"operator": "not_contains", "value": "fcu"},
                "rate_from": {"operator": "not_equals", "value": 47},
                "rate_to": {"operator": "less_than", "value": 67},
                "duration": "More than 6 months",
                "description": {"operator": "contains", "value": "functi"},
                "title": {"operator": "not_equals", "value": "Embedded Systems Engineers Jobs"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "NAVBAR_PROFILE_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_PROFILE_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "NAVBAR_JOBS_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_JOBS_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "NAVBAR_EXPERTS_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_EXPERTS_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "NAVBAR_FAVORITES_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_FAVORITES_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "NAVBAR_HIRE_LATER_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_HIRE_LATER_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "NAVBAR_HIRES_CLICK": [{"type": "CheckEventTest", "event_name": "NAVBAR_HIRES_CLICK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CONTACT_EXPERT_OPENED": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_EXPERT_OPENED",
            "event_criteria": {"role": {"operator": "not_contains", "value": "lqb"}, "name": {"operator": "not_equals", "value": "James Wright"}, "country": {"operator": "contains", "value": "ab"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "CONTACT_EXPERT_MESSAGE_SENT": [
        {
            "type": "CheckEventTest",
            "event_name": "CONTACT_EXPERT_MESSAGE_SENT",
            "event_criteria": {"role": "QA Engineer", "name": "Zachary Russell", "message": {"operator": "contains", "value": "can I c"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_PROFILE_NAME": [
        {"type": "CheckEventTest", "event_name": "EDIT_PROFILE_NAME", "event_criteria": {"value": {"operator": "contains", "value": "Thomp"}}, "description": "Check if specific event was triggered"}
    ],
    "EDIT_ABOUT": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_ABOUT",
            "event_criteria": {"value": {"operator": "contains", "value": "strations, and visu"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_PROFILE_EMAIL": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_PROFILE_EMAIL",
            "event_criteria": {"value": {"operator": "not_equals", "value": "sarah.williams@example.com"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_PROFILE_TITLE": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_PROFILE_TITLE",
            "event_criteria": {"value": {"operator": "not_equals", "value": "Project Managers Jobs"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_PROFILE_LOCATION": [
        {"type": "CheckEventTest", "event_name": "EDIT_PROFILE_LOCATION", "event_criteria": {"value": "Boston, MA, USA"}, "description": "Check if specific event was triggered"}
    ],
    "BROWSE_FAVORITE_EXPERT": [{"type": "CheckEventTest", "event_name": "BROWSE_FAVORITE_EXPERT", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "FAVORITE_EXPERT_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "FAVORITE_EXPERT_SELECTED",
            "event_criteria": {"country": {"operator": "contains", "value": "rain"}, "role": "Software Architect", "name": {"operator": "not_contains", "value": "msm"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "FAVORITE_EXPERT_REMOVED": [
        {
            "type": "CheckEventTest",
            "event_name": "FAVORITE_EXPERT_REMOVED",
            "event_criteria": {"name": {"operator": "not_contains", "value": "kfm"}, "country": "Egypt", "role": "DevOps Engineer"},
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


def _placeholder(element_placeholder: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="placeholder", value=element_placeholder)


# --- Use cases: names match autowork_tasks.json use_case.name (registry keys are unique per task) ---

BOOK_A_CONSULTATION = _uc(
    "BOOK_A_CONSULTATION",
    prompt="Book a consultation whose rating is NOT '4.5' AND whose jobs are LESS THAN OR EQUAL TO '330' AND whose rate is NOT '$65.00/hr' AND whose role CONTAINS 'ngine'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_BOOK_A_CONSULTATION}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-nav-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("book-consultation-button-8")),
        WaitAction(time_seconds=2.0),
    ],
)

HIRE_BTN_CLICKED = _uc(
    "HIRE_BTN_CLICKED",
    prompt="Hire a consultant whose country equals 'Denmark' and whose role equals 'UX Researcher' and whose name equals 'Rachel Foster'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HIRE_BTN_CLICKED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-nav-link')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-0")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("hire-begin-button")),
    ],
)

HIRE_LATER_ADDED = _uc(
    "HIRE_LATER_ADDED",
    prompt="Decide to hire later for an expert whose name does NOT contain 'xue', whose role is NOT 'Data Scientist', and whose country is NOT 'New Zealand'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HIRE_LATER_ADDED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-menu-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("book-consultation-button-0")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='expert-name-header-0']/div[2]/button[3]")),
    ],
)

HIRE_LATER_REMOVED = _uc(
    "HIRE_LATER_REMOVED",
    prompt="Decide to remove expert that name contains 'l' from hire later page.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HIRE_LATER_REMOVED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-experts-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("book-consultation-button-3")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='expert-name-header-0']/div[2]/button[4]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-hire-later-element')]")),
        WaitAction(time_seconds=0.45),
        # Chrome recorder: html/.../main/div/span/main/div[2]/div[2]/div[3]/button[2]
        ClickAction(selector=_xp("//button[contains(@class, 'delete-btn')]")),
    ],
)

HIRE_LATER_START = _uc(
    "HIRE_LATER_START",
    prompt="Decide to start hiring of expert that country contains 'krai' and name is not equals 'Raymond Gonzalez' and is in hire later page.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HIRE_LATER_START}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-menu-link')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-5")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='expert-name-header-0']/div[2]/button[3]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//aside//a[contains(@class,'hire-later-nav-item')]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//button[contains(normalize-space(),'Start now')]")),
    ],
)

QUICK_HIRE = _uc(
    "QUICK_HIRE",
    prompt="Quick hire the expert whose role contains 'Dev' and rate is NOT '$63.00/hr' and country is NOT 'Ireland'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_QUICK_HIRE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-experts-element')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-7")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='expert-name-header-0']/div[2]/button[2]")),
    ],
)

SELECT_HIRING_TEAM = _uc(
    "SELECT_HIRING_TEAM",
    prompt="Show details for the hiring team where the name equals 'Joshua Turner' and the team contains 'sof'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SELECT_HIRING_TEAM}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-experts-element')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-3")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("begin-hiring-button")),
        WaitAction(time_seconds=0.45),
        SelectAction(selector=_id("select-hiring-team"), value="Google"),
    ],
)

HIRE_CONSULTANT = _uc(
    "HIRE_CONSULTANT",
    prompt="Confirm hiring of a consultation whose increaseWhen contains 'ever', paymentType equals 'hourly', rate not contains 'rnd', country equals 'Canada', increaseHowMuch contains '5', name not equals 'Joseph Alexander', and role contains 'k D'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_HIRE_CONSULTANT}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-menu-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-2")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("hire-start-btn")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("submit-hire-action")),
    ],
)

CANCEL_HIRE = _uc(
    "CANCEL_HIRE",
    prompt="Cancel hiring of a consultation whose name CONTAINS 'is' AND whose rate CONTAINS '.00/' AND whose country CONTAINS 'South Afri' AND whose role does NOT CONTAIN 'mzu'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CANCEL_HIRE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//nav//a[3]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("//*[@id='experts']/nav/button[2]")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-2")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("begin-hire-btn")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("cancel-hire-action")),
    ],
)

POST_A_JOB = _uc(
    "POST_A_JOB",
    prompt="User clicks 'Post a job' button to initiate the posting process for a job when the page is 'home'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_POST_A_JOB}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("create-job-btn")),
    ],
)

WRITE_JOB_TITLE = _uc(
    "WRITE_JOB_TITLE",
    prompt="User initiates a process of job posting by writing a strong title of the job that does NOT contain 'lki'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_WRITE_JOB_TITLE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-jobs-control')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("new-posting-btn")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("job-title-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("job-title-input-0"), text="Machine Learning"),
    ],
)

SEARCH_SKILL = _uc(
    "SEARCH_SKILL",
    prompt="Search for a skill that is NOT 'API Monitoring'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SEARCH_SKILL}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("create-job-btn")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("skill-search-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("skill-search-input-0"), text="PyTorch"),
        WaitAction(time_seconds=0.2),
    ],
)

ADD_SKILL = _uc(
    "ADD_SKILL",
    prompt="Add a skill where skill is NOT 'Web Performance Optimization'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_ADD_SKILL}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("post-job-action")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("skill-search-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("skill-search-input-0"), text="CSS"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_id("add-skill-button-0")),
    ],
)

CHOOSE_BUDGET_TYPE = _uc(
    "CHOOSE_BUDGET_TYPE",
    prompt="Choose a budget type that does NOT contain 'ker'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CHOOSE_BUDGET_TYPE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("post-job-btn")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-3")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("budget-type-button-1")),
    ],
)

CHOOSE_PROJECT_SIZE = _uc(
    "CHOOSE_PROJECT_SIZE",
    prompt="Select a project size that is NOT 'Small'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CHOOSE_PROJECT_SIZE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//a[contains(@class,'nav-jobs-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("new-job-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//div[contains(@class,'space-y-4')]/label[1]/input")),
    ],
)

CHOOSE_PROJECT_TIMELINE = _uc(
    "CHOOSE_PROJECT_TIMELINE",
    prompt="Choose a project timeline that is 'More than 6 months'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CHOOSE_PROJECT_TIMELINE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("post-job-action")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//div[contains(@class,'mt-8')]//label[1]/input")),
    ],
)

SET_RATE_RANGE = _uc(
    "SET_RATE_RANGE",
    prompt="Set the hourly rate range where rate_from is greater equal to '39' and rate_to is greater than '77'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SET_RATE_RANGE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("post-job-action")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-3")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//main//form//section[1]/div[1]/div[1]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[1]/div[1]/div[1]/input"), text="40"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp("//main//form//section[1]/div[1]/div[2]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[1]/div[1]/div[2]/input"), text="78"),
        WaitAction(time_seconds=0.2),
    ],
)

_WRITE_JOB_DESCRIPTION_TEXT = "Build and deploy machine learning models for real-world production environments."

WRITE_JOB_DESCRIPTION = _uc(
    "WRITE_JOB_DESCRIPTION",
    prompt="Write a job description that equals 'Build and deploy machine learning models for real-world production environments.'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_WRITE_JOB_DESCRIPTION}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("new-job-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-3")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-4")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("job-description-textarea-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("job-description-textarea-0"), text=_WRITE_JOB_DESCRIPTION_TEXT),
        WaitAction(time_seconds=0.4),
    ],
)

_SUBMIT_JOB_DESCRIPTION_TEXT = "Prove user experience through', a title that equals 'Database Administrators Jobs"

SUBMIT_JOB = _uc(
    "SUBMIT_JOB",
    prompt="Submit a job with a rate from less than '12', a rate to that is NOT '61', a duration that does NOT contain 'wdr', a scope that CONTAINS 'i', a description that CONTAINS 'rove user experience through', a title that equals 'Database Administrators Jobs', and skills that CONTAINS 'Analysis'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_SUBMIT_JOB}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("job-create-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("skill-search-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("skill-search-input-0"), text="Time Complexity Analysis"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_id("add-skill-button-0")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//div[contains(@class,'space-y-4')]/label[2]/input")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-3")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//main//form//section[3]/div[1]/div[1]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[3]/div[1]/div[1]/input"), text="10"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp("//main//form//section[3]/div[1]/div[2]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[3]/div[1]/div[2]/input"), text="50"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_id("next-button-4")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("job-description-textarea-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("job-description-textarea-0"), text=_SUBMIT_JOB_DESCRIPTION_TEXT),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_id("submit-job-button-0")),
    ],
)

CLOSE_POST_A_JOB_WINDOW = _uc(
    "CLOSE_POST_A_JOB_WINDOW",
    prompt="Close the job posting window where the scope contains 'ediu', the budgetType does not contain 'hpz', the skills do not contain 'fcu', the rate_from does not equal '47', the rate_to is less than '67', the duration equals 'More than 6 months', the description contains 'functi', and the title does not equal 'Embedded Systems Engineers Jobs'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CLOSE_POST_A_JOB_WINDOW}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("job-create-button")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("skill-search-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("skill-search-input-0"), text="MongoDB"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_id("add-skill-button-0")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("next-button-1")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//div[contains(@class,'space-y-4')]/label[2]/input")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//div[contains(@class,'mt-8')]//label[1]/input")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_id("next-button-2")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("job-title-input-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("job-title-input-0"), text="AI Engineer Job"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_id("next-button-3")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//main//form//section[2]/div[1]/div[1]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[2]/div[1]/div[1]/input"), text="40"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp("//main//form//section[2]/div[1]/div[2]/input")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_xp("//main//form//section[2]/div[1]/div[2]/input"), text="60"),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_id("next-button-4")),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("job-description-textarea-0")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_id("job-description-textarea-0"),
            text="Functional projects will get bonus points.",
        ),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//main/div/span[1]/main/span[4]/div/div/header/button")),
    ],
)

NAVBAR_PROFILE_CLICK = _uc(
    "NAVBAR_PROFILE_CLICK",
    prompt="User clicks on the profile option from the navbar to view the user profile.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_PROFILE_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'profile-nav-link')]")),
        WaitAction(time_seconds=2.0),
    ],
)

NAVBAR_JOBS_CLICK = _uc(
    "NAVBAR_JOBS_CLICK",
    prompt="User clicks on the 'jobs' option from the navbar to view all available jobs.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_JOBS_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-jobs-link')]")),
        WaitAction(time_seconds=2.0),
    ],
)

NAVBAR_EXPERTS_CLICK = _uc(
    "NAVBAR_EXPERTS_CLICK",
    prompt="User clicks on the experts section from the navbar to view all experts.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_EXPERTS_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'experts-menu-item')]")),
        WaitAction(time_seconds=2.0),
    ],
)

NAVBAR_FAVORITES_CLICK = _uc(
    "NAVBAR_FAVORITES_CLICK",
    prompt="User clicks favorites to view all favorite experts.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_FAVORITES_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside/nav/a[4]")),
        WaitAction(time_seconds=2.0),
    ],
)

NAVBAR_HIRE_LATER_CLICK = _uc(
    "NAVBAR_HIRE_LATER_CLICK",
    prompt="User clicks 'hire later' from the navbar option to view hire later experts.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_HIRE_LATER_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'hire-later-nav-item')]")),
        WaitAction(time_seconds=2.0),
    ],
)

NAVBAR_HIRES_CLICK = _uc(
    "NAVBAR_HIRES_CLICK",
    prompt="User clicks on the 'hires' option from the navbar to view all hires.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_NAVBAR_HIRES_CLICK}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'hires-menu-item')]")),
        WaitAction(time_seconds=2.0),
    ],
)

CONTACT_EXPERT_OPENED = _uc(
    "CONTACT_EXPERT_OPENED",
    prompt="Contact an expert where role does NOT contain 'lqb', name is NOT 'James Wright', and country contains 'ab'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_EXPERT_OPENED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside/nav/a[3]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("book-consultation-button-4")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("message-expert-button")),
    ],
)

CONTACT_EXPERT_MESSAGE_SENT = _uc(
    "CONTACT_EXPERT_MESSAGE_SENT",
    prompt="Send a message to an expert where role equals 'QA Engineer' and name equals 'Zachary Russell' and message contains 'can I c'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_CONTACT_EXPERT_MESSAGE_SENT}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-experts-element')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_id("book-consultation-button-7")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("contact-btn")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//main/div/div/div/textarea")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_xp("//main/div/div/div/textarea"),
            text="Hi, can I consult you on this?",
        ),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp("//main/div/div/div/div[2]/button[2]")),
    ],
)

EDIT_PROFILE_NAME = _uc(
    "EDIT_PROFILE_NAME",
    prompt="Edit profile name where value contains 'Thomp'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_PROFILE_NAME}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'profile-nav-link')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//main/div/main/div[1]/div/div[2]/div/div[2]/button[contains(normalize-space(),'Change profile')]")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//main/div/main/div[1]/div/div[2]/div/div[1]/input[1]")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_xp("//main/div/main/div[1]/div/div[2]/div/div[1]/input[1]"),
            text="Thompson Alex",
        ),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp("//main/div/main/div[1]/div/div[2]/div/div[2]/button[2]")),
    ],
)

_EDIT_ABOUT_TEXT = "Graphic designer specializing in branding, illustrations, and visual storytelling."

EDIT_ABOUT = _uc(
    "EDIT_ABOUT",
    prompt="Edit profile about where value contains 'strations' and 'visu'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_ABOUT}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-profile-link')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//main/div/span[2]/main/div[1]/div/div[2]/div/div[2]/button[contains(normalize-space(),'Modify profile')]")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//main/div/span[2]/main/div[3]/div/button[normalize-space()='Change']")),
        WaitAction(time_seconds=0.3),
        ClickAction(selector=_xp("//main/div/span[2]/main/div[3]/div[2]/textarea")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_xp("//main/div/span[2]/main/div[3]/div[2]/textarea"),
            text=_EDIT_ABOUT_TEXT,
        ),
        ClickAction(selector=_xp("//button[normalize-space()='Save']")),
        WaitAction(time_seconds=2.0),
    ],
)

_EDIT_PROFILE_EMAIL_TEXT = "emily.johnson@example.com"

EDIT_PROFILE_EMAIL = _uc(
    "EDIT_PROFILE_EMAIL",
    prompt="Edit profile email where email NOT equals 'sarah.williams@example.com'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_PROFILE_EMAIL}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-profile-element')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//main/div/span[1]/main/div[1]/div/div[2]/div/div[2]/button[normalize-space()='Edit']")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_placeholder("Add an email")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_placeholder("Add an email"),
            text=_EDIT_PROFILE_EMAIL_TEXT,
        ),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp("//button[normalize-space()='Save']")),
    ],
)

_EDIT_PROFILE_TITLE_TEXT = "AI/ML Engineer"

EDIT_PROFILE_TITLE = _uc(
    "EDIT_PROFILE_TITLE",
    prompt="Edit profile title where title is NOT 'Project Managers Jobs'",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_PROFILE_TITLE}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-profile-action')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//button[normalize-space()='Modify']")),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_placeholder("Add a title")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_placeholder("Add a title"),
            text=_EDIT_PROFILE_TITLE_TEXT,
        ),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp("//button[normalize-space()='Save']")),
    ],
)

_EDIT_PROFILE_LOCATION_TEXT = "Boston, MA, USA"

EDIT_PROFILE_LOCATION = _uc(
    "EDIT_PROFILE_LOCATION",
    prompt="Edit profile location where value equals 'Boston, MA, USA'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_EDIT_PROFILE_LOCATION}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'profile-menu-link')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(
            selector=_xp(
                # "//main/div/main/div[1]/div/div[2]/div/div[2]/button[normalize-space()='Update']"
                "//button[normalize-space()='Update']"
            )
        ),
        WaitAction(time_seconds=0.35),
        ClickAction(
            # selector=_xp(
            #     "//main/div/main/div[1]/div/div[2]/div/div[1]/div/label[1]/input"
            # )
            selector=_placeholder("Add a location")
        ),
        WaitAction(time_seconds=0.2),
        TypeAction(
            # selector=_xp(
            #     "//main/div/main/div[1]/div/div[2]/div/div[1]/div/label[1]/input"
            # ),
            selector=_placeholder("Add a location"),
            text=_EDIT_PROFILE_LOCATION_TEXT,
        ),
        WaitAction(time_seconds=0.25),
        ClickAction(
            selector=_xp(
                # "//main/div/main/div[1]/div/div[2]/div/div[2]/button[2]"
                "//button[normalize-space()='Save']"
            )
        ),
    ],
)

BROWSE_FAVORITE_EXPERT = _uc(
    "BROWSE_FAVORITE_EXPERT",
    prompt="The user browse an expert to mark them as favorite.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_BROWSE_FAVORITE_EXPERT}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-favorites-control')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(
            selector=_xp(
                # "//main/div/span/main/div[2]/span/button[normalize-space()='View Experts']"
                "//button[normalize-space()='View Experts']"
            )
        ),
        WaitAction(time_seconds=0.5),
    ],
)

FAVORITE_EXPERT_SELECTED = _uc(
    "FAVORITE_EXPERT_SELECTED",
    prompt="Select favorite expert where country contains 'rain' and role equals 'Software Architect' and name not contains 'msm'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FAVORITE_EXPERT_SELECTED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'nav-experts-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp('//*[@id="experts"]/nav/button[2]')),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_id("book-consultation-button-4")),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_id("add-favorite-button")),
    ],
)

FAVORITE_EXPERT_REMOVED = _uc(
    "FAVORITE_EXPERT_REMOVED",
    prompt="Remove favorite expert where name NOT contains 'kfm' and country equals 'Egypt' and role equals 'DevOps Engineer'.",
    actions=[
        NavigateAction(url=f"{BASE}/?seed={SEED_FAVORITE_EXPERT_REMOVED}"),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_xp("//aside//a[contains(@class,'favorites-nav-item')]")),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//main/div/main/div[2]/button[normalize-space()='Browse Experts']")),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp('//*[@id="experts"]/nav/button[2]')),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp('//*[@id="experts"]/nav/button[2]')),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp('//*[@id="experts"]/nav/button[2]')),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp('//*[@id="experts"]/div[2]/div[5]/button[1]')),
        WaitAction(time_seconds=0.2),
        ClickAction(selector=_xp('//*[@id="experts"]/div[2]/div[5]/button[1]')),
    ],
)


def load_autowork_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "BOOK_A_CONSULTATION": BOOK_A_CONSULTATION,
        "HIRE_BTN_CLICKED": HIRE_BTN_CLICKED,
        "HIRE_LATER_ADDED": HIRE_LATER_ADDED,
        "HIRE_LATER_REMOVED": HIRE_LATER_REMOVED,
        "HIRE_LATER_START": HIRE_LATER_START,
        "QUICK_HIRE": QUICK_HIRE,
        "SELECT_HIRING_TEAM": SELECT_HIRING_TEAM,
        "HIRE_CONSULTANT": HIRE_CONSULTANT,
        "CANCEL_HIRE": CANCEL_HIRE,
        "POST_A_JOB": POST_A_JOB,
        "WRITE_JOB_TITLE": WRITE_JOB_TITLE,
        "SEARCH_SKILL": SEARCH_SKILL,
        "ADD_SKILL": ADD_SKILL,
        "CHOOSE_BUDGET_TYPE": CHOOSE_BUDGET_TYPE,
        "CHOOSE_PROJECT_SIZE": CHOOSE_PROJECT_SIZE,
        "CHOOSE_PROJECT_TIMELINE": CHOOSE_PROJECT_TIMELINE,
        "SET_RATE_RANGE": SET_RATE_RANGE,
        "WRITE_JOB_DESCRIPTION": WRITE_JOB_DESCRIPTION,
        "SUBMIT_JOB": SUBMIT_JOB,
        "CLOSE_POST_A_JOB_WINDOW": CLOSE_POST_A_JOB_WINDOW,
        "NAVBAR_PROFILE_CLICK": NAVBAR_PROFILE_CLICK,
        "NAVBAR_JOBS_CLICK": NAVBAR_JOBS_CLICK,
        "NAVBAR_EXPERTS_CLICK": NAVBAR_EXPERTS_CLICK,
        "NAVBAR_FAVORITES_CLICK": NAVBAR_FAVORITES_CLICK,
        "NAVBAR_HIRE_LATER_CLICK": NAVBAR_HIRE_LATER_CLICK,
        "NAVBAR_HIRES_CLICK": NAVBAR_HIRES_CLICK,
        "CONTACT_EXPERT_OPENED": CONTACT_EXPERT_OPENED,
        "CONTACT_EXPERT_MESSAGE_SENT": CONTACT_EXPERT_MESSAGE_SENT,
        "EDIT_PROFILE_NAME": EDIT_PROFILE_NAME,
        "EDIT_ABOUT": EDIT_ABOUT,
        "EDIT_PROFILE_EMAIL": EDIT_PROFILE_EMAIL,
        "EDIT_PROFILE_TITLE": EDIT_PROFILE_TITLE,
        "EDIT_PROFILE_LOCATION": EDIT_PROFILE_LOCATION,
        "BROWSE_FAVORITE_EXPERT": BROWSE_FAVORITE_EXPERT,
        "FAVORITE_EXPERT_SELECTED": FAVORITE_EXPERT_SELECTED,
        "FAVORITE_EXPERT_REMOVED": FAVORITE_EXPERT_REMOVED,
    }


if __name__ == "__main__":
    for name, uc in sorted(load_autowork_use_case_completion_flows().items()):
        print(name, "->", (uc.prompt or "")[:72], "...")
