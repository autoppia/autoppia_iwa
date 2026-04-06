"""
Concrete IWA flows for Autoppia Calendar (web_11).

- Prompts align with ``use_cases.py`` example text where possible.
- Base URL and seed match ``autocalendar_tasks.json`` (``build_tasks_json.DEFAULT_SEED``).
- Selectors favor stable ``aria-label``s and V3 id-variant unions (see ``id-variants.json``).
"""

from __future__ import annotations

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions import (
    ClickAction,
    NavigateAction,
    SelectDropDownOptionAction,
    SendKeysIWAAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

PROJECT_NUMBER = 11
WEB_PROJECT_ID = "autocalendar"

BASE = "http://localhost:8010"
DEFAULT_SEED = 201


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _nav_home() -> list[BaseAction]:
    return [
        NavigateAction(url=f"{BASE}/?seed={DEFAULT_SEED}"),
        WaitAction(time_seconds=0.75),
    ]


def _open_view_menu() -> list[BaseAction]:
    return [
        ClickAction(selector=_xp("//button[@aria-label='Select calendar view']")),
        WaitAction(time_seconds=0.4),
    ]


def _pick_view_aria(label: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_xp(f"//button[@aria-label='Select {label} view']")),
        WaitAction(time_seconds=0.45),
    ]


def _ct(name: str, raw: list[dict]) -> list[BaseTaskTest]:
    return [BaseTaskTest.deserialize(d) for d in raw]


_RAW_TESTS: dict[str, list[dict]] = {
    "SELECT_MONTH": [{"type": "CheckEventTest", "event_name": "SELECT_MONTH", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "SELECT_WEEK": [{"type": "CheckEventTest", "event_name": "SELECT_WEEK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "SELECT_FIVE_DAYS": [{"type": "CheckEventTest", "event_name": "SELECT_FIVE_DAYS", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "SELECT_DAY": [{"type": "CheckEventTest", "event_name": "SELECT_DAY", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "SELECT_TODAY": [{"type": "CheckEventTest", "event_name": "SELECT_TODAY", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "ADD_NEW_CALENDAR": [{"type": "CheckEventTest", "event_name": "ADD_NEW_CALENDAR", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CREATE_CALENDAR": [
        {
            "type": "CheckEventTest",
            "event_name": "CREATE_CALENDAR",
            "event_criteria": {"name": "IWA Trajectory Calendar", "description": "Trajectory seed calendar"},
            "description": "Check if specific event was triggered",
        }
    ],
    "UNSELECT_CALENDAR": [
        {
            "type": "CheckEventTest",
            "event_name": "UNSELECT_CALENDAR",
            "event_criteria": {"calendar_name": "Personal"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SELECT_CALENDAR": [
        {
            "type": "CheckEventTest",
            "event_name": "SELECT_CALENDAR",
            "event_criteria": {"calendar_name": "Personal"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_SUBMIT": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_SUBMIT",
            "event_criteria": {"query": "work"},
            "description": "Check if specific event was triggered",
        }
    ],
    "EVENT_WIZARD_OPEN": [{"type": "CheckEventTest", "event_name": "EVENT_WIZARD_OPEN", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CELL_CLICKED": [{"type": "CheckEventTest", "event_name": "CELL_CLICKED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "ADD_EVENT": [{"type": "CheckEventTest", "event_name": "ADD_EVENT", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "CANCEL_ADD_EVENT": [{"type": "CheckEventTest", "event_name": "CANCEL_ADD_EVENT", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "DELETE_ADDED_EVENT": [{"type": "CheckEventTest", "event_name": "DELETE_ADDED_EVENT", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "EVENT_ADD_REMINDER": [
        {
            "type": "CheckEventTest",
            "event_name": "EVENT_ADD_REMINDER",
            "event_criteria": {"minutes": 30},
            "description": "Check if specific event was triggered",
        }
    ],
    "EVENT_REMOVE_REMINDER": [
        {
            "type": "CheckEventTest",
            "event_name": "EVENT_REMOVE_REMINDER",
            "event_criteria": {"minutes": 30},
            "description": "Check if specific event was triggered",
        }
    ],
    "EVENT_ADD_ATTENDEE": [
        {
            "type": "CheckEventTest",
            "event_name": "EVENT_ADD_ATTENDEE",
            "event_criteria": {"email": "traj.user@example.com"},
            "description": "Check if specific event was triggered",
        }
    ],
    "EVENT_REMOVE_ATTENDEE": [
        {
            "type": "CheckEventTest",
            "event_name": "EVENT_REMOVE_ATTENDEE",
            "event_criteria": {"email": "traj.user@example.com"},
            "description": "Check if specific event was triggered",
        }
    ],
}

# --- View switches (dropdown) ---
_SELECT_MONTH = Trajectory(
    name="SELECT_MONTH",
    prompt="Switch to month view.",
    actions=_nav_home() + _open_view_menu() + _pick_view_aria("Month"),
    tests=_ct("SELECT_MONTH", _RAW_TESTS["SELECT_MONTH"]),
)

_SELECT_WEEK = Trajectory(
    name="SELECT_WEEK",
    prompt="Switch to week view.",
    actions=_nav_home() + _open_view_menu() + _pick_view_aria("Week"),
    tests=_ct("SELECT_WEEK", _RAW_TESTS["SELECT_WEEK"]),
)

_SELECT_FIVE_DAYS = Trajectory(
    name="SELECT_FIVE_DAYS",
    prompt="Switch to 5-day view.",
    actions=_nav_home() + _open_view_menu() + _pick_view_aria("5 days"),
    tests=_ct("SELECT_FIVE_DAYS", _RAW_TESTS["SELECT_FIVE_DAYS"]),
)

_SELECT_DAY = Trajectory(
    name="SELECT_DAY",
    prompt="Switch to day view please.",
    actions=_nav_home() + _open_view_menu() + _pick_view_aria("Day"),
    tests=_ct("SELECT_DAY", _RAW_TESTS["SELECT_DAY"]),
)

_SELECT_TODAY = Trajectory(
    name="SELECT_TODAY",
    prompt="Go to today's date.",
    actions=[*_nav_home(), ClickAction(selector=_xp("//button[@aria-label='Go to today']")), WaitAction(time_seconds=0.45)],
    tests=_ct("SELECT_TODAY", _RAW_TESTS["SELECT_TODAY"]),
)

_SEARCH_SUBMIT = Trajectory(
    name="SEARCH_SUBMIT",
    prompt="Search for 'work'",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//input[@aria-label='Search events']")),
        TypeAction(selector=_xp("//input[@aria-label='Search events']"), text="work"),
        SendKeysIWAAction(keys="Enter"),
        WaitAction(time_seconds=0.35),
    ],
    tests=_ct("SEARCH_SUBMIT", _RAW_TESTS["SEARCH_SUBMIT"]),
)

_ADD_CAL_MODAL_NAME = "//input[@id='add-calendar-modal-name' or @id='new-calendar-modal-name' or @id='calendar-dialog-name' or @id='calendar-wizard-name']"
_ADD_CAL_MODAL_DESC = "//textarea[@id='add-calendar-modal-description' or @id='new-calendar-modal-description' or @id='calendar-dialog-description' or @id='calendar-wizard-description']"
_ADD_CAL_SUBMIT = "//button[@id='add-calendar-modal-submit' or @id='new-calendar-modal-submit' or @id='calendar-dialog-submit' or @id='calendar-wizard-submit']"

_ADD_NEW_CALENDAR = Trajectory(
    name="ADD_NEW_CALENDAR",
    prompt="Click add calendar.",
    actions=[*_nav_home(), ClickAction(selector=_xp("(//button[contains(normalize-space(.),'Add calendar')])[1]")), WaitAction(time_seconds=0.5)],
    tests=_ct("ADD_NEW_CALENDAR", _RAW_TESTS["ADD_NEW_CALENDAR"]),
)

_CREATE_CALENDAR = Trajectory(
    name="CREATE_CALENDAR",
    prompt="Create calendar named 'IWA Trajectory Calendar' with a description for trajectory seed calendar.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("(//button[contains(normalize-space(.),'Add calendar')])[1]")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_ADD_CAL_MODAL_NAME)),
        TypeAction(selector=_xp(_ADD_CAL_MODAL_NAME), text="IWA Trajectory Calendar"),
        ClickAction(selector=_xp(_ADD_CAL_MODAL_DESC)),
        TypeAction(selector=_xp(_ADD_CAL_MODAL_DESC), text="Trajectory seed calendar"),
        ClickAction(selector=_xp(_ADD_CAL_SUBMIT)),
        WaitAction(time_seconds=0.55),
    ],
    tests=_ct("CREATE_CALENDAR", _RAW_TESTS["CREATE_CALENDAR"]),
)

_UNSELECT_CALENDAR = Trajectory(
    name="UNSELECT_CALENDAR",
    prompt="Unselect the Personal calendar.",
    actions=[*_nav_home(), ClickAction(selector=_xp("//label[contains(.,'Personal')]//input[@type='checkbox']")), WaitAction(time_seconds=0.35)],
    tests=_ct("UNSELECT_CALENDAR", _RAW_TESTS["UNSELECT_CALENDAR"]),
)

_SELECT_CALENDAR = Trajectory(
    name="SELECT_CALENDAR",
    prompt="Select the Personal calendar.",
    actions=[
        *_nav_home(),
        # Toggle off then on so the final event is SELECT_CALENDAR (default state is checked).
        ClickAction(selector=_xp("//label[contains(.,'Personal')]//input[@type='checkbox']")),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp("//label[contains(.,'Personal')]//input[@type='checkbox']")),
        WaitAction(time_seconds=0.35),
    ],
    tests=_ct("SELECT_CALENDAR", _RAW_TESTS["SELECT_CALENDAR"]),
)

_EVENT_WIZARD_OPEN = Trajectory(
    name="EVENT_WIZARD_OPEN",
    prompt="Open the new event wizard.",
    actions=[*_nav_home(), ClickAction(selector=_xp("//button[@aria-label='Create new event']")), WaitAction(time_seconds=0.55)],
    tests=_ct("EVENT_WIZARD_OPEN", _RAW_TESTS["EVENT_WIZARD_OPEN"]),
)

_EVENT_NAME_INPUT = "//input[@id='event-name-input' or @id='event-title-input' or @id='event-label-input' or @id='event-name-field' or @id='event-headline-input']"
_EVENT_MODAL_NEXT = "//button[@id='event-modal-next' or @id='event-dialog-next' or @id='planner-modal-next' or @id='edit-event-modal-next']"
_EVENT_MODAL_SAVE = "//button[@id='event-modal-save' or @id='event-dialog-save' or @id='planner-save' or @id='editor-save']"

_CELL_CLICKED = Trajectory(
    name="CELL_CLICKED",
    prompt="Click on cell when view equals 'Week' and date equals '2025-09-30' and hour equals '3'.",
    actions=[
        *_nav_home(),
        *_open_view_menu(),
        *_pick_view_aria("Week"),
        ClickAction(selector=_xp("(//button[contains(@aria-label,'Add event on')])[1]")),
        WaitAction(time_seconds=0.45),
    ],
    tests=_ct("CELL_CLICKED", _RAW_TESTS["CELL_CLICKED"]),
)

_ADD_EVENT = Trajectory(
    name="ADD_EVENT",
    prompt="Add an event titled IWA Traj Save via wizard.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_NAME_INPUT)),
        TypeAction(selector=_xp(_EVENT_NAME_INPUT), text="IWA Traj Save"),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_EVENT_MODAL_SAVE)),
        WaitAction(time_seconds=0.55),
    ],
    tests=_ct("ADD_EVENT", _RAW_TESTS["ADD_EVENT"]),
)

_CANCEL_ADD_EVENT = Trajectory(
    name="CANCEL_ADD_EVENT",
    prompt="Cancel an event after opening the wizard.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_NAME_INPUT)),
        TypeAction(selector=_xp(_EVENT_NAME_INPUT), text="Cancel Me"),
        ClickAction(selector=_xp("//div[contains(@class,'DialogFooter')]//button[contains(normalize-space(.),'Cancel')][not(contains(normalize-space(.),'Delete'))][1]")),
        WaitAction(time_seconds=0.45),
    ],
    tests=_ct("CANCEL_ADD_EVENT", _RAW_TESTS["CANCEL_ADD_EVENT"]),
)

_DELETE_ADDED_EVENT = Trajectory(
    name="DELETE_ADDED_EVENT",
    prompt="Delete an added event from the month grid.",
    actions=[
        *_nav_home(),
        *_open_view_menu(),
        *_pick_view_aria("Month"),
        ClickAction(selector=_xp("(//button[starts-with(@aria-label,'Edit event:')])[1]")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//button[contains(normalize-space(.),'Delete')]")),
        WaitAction(time_seconds=0.55),
    ],
    tests=_ct("DELETE_ADDED_EVENT", _RAW_TESTS["DELETE_ADDED_EVENT"]),
)

_ATT_INPUT = "//input[@id='attendee-input' or @id='guest-input' or @id='invitee-input' or @id='people-input']"
_ATT_ADD_BTN = "//button[contains(@id,'attendee-input') and contains(@id,'add')]"
_REM_ADD_BTN = "//button[contains(@id,'reminder-pill') and contains(@id,'add')]"

_SEL_MINUTES = Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="select-minutes")

_EVENT_ADD_REMINDER = Trajectory(
    name="EVENT_ADD_REMINDER",
    prompt="Add a 30-minute reminder to the event.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        SelectDropDownOptionAction(selector=_SEL_MINUTES, text="30m before"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp(_REM_ADD_BTN)),
        WaitAction(time_seconds=0.4),
    ],
    tests=_ct("EVENT_ADD_REMINDER", _RAW_TESTS["EVENT_ADD_REMINDER"]),
)

_EVENT_REMOVE_REMINDER = Trajectory(
    name="EVENT_REMOVE_REMINDER",
    prompt="Remove the 30-minute reminder from the event.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        SelectDropDownOptionAction(selector=_SEL_MINUTES, text="30m before"),
        WaitAction(time_seconds=0.25),
        ClickAction(selector=_xp(_REM_ADD_BTN)),
        WaitAction(time_seconds=0.3),
        ClickAction(selector=_xp("//button[normalize-space(.)='Remove']")),
        WaitAction(time_seconds=0.4),
    ],
    tests=_ct("EVENT_REMOVE_REMINDER", _RAW_TESTS["EVENT_REMOVE_REMINDER"]),
)

_EVENT_ADD_ATTENDEE = Trajectory(
    name="EVENT_ADD_ATTENDEE",
    prompt="Add traj.user@example.com as an attendee.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_ATT_INPUT)),
        TypeAction(selector=_xp(_ATT_INPUT), text="traj.user@example.com"),
        ClickAction(selector=_xp(_ATT_ADD_BTN)),
        WaitAction(time_seconds=0.45),
    ],
    tests=_ct("EVENT_ADD_ATTENDEE", _RAW_TESTS["EVENT_ADD_ATTENDEE"]),
)

_EVENT_REMOVE_ATTENDEE = Trajectory(
    name="EVENT_REMOVE_ATTENDEE",
    prompt="Remove traj.user@example.com from attendees.",
    actions=[
        *_nav_home(),
        ClickAction(selector=_xp("//button[@aria-label='Create new event']")),
        WaitAction(time_seconds=0.55),
        ClickAction(selector=_xp(_EVENT_MODAL_NEXT)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(_ATT_INPUT)),
        TypeAction(selector=_xp(_ATT_INPUT), text="traj.user@example.com"),
        ClickAction(selector=_xp(_ATT_ADD_BTN)),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp("//button[starts-with(@aria-label,'Remove traj.user@example.com')]")),
        WaitAction(time_seconds=0.4),
    ],
    tests=_ct("EVENT_REMOVE_ATTENDEE", _RAW_TESTS["EVENT_REMOVE_ATTENDEE"]),
)


def load_autocalendar_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "SELECT_MONTH": _SELECT_MONTH,
        "SELECT_WEEK": _SELECT_WEEK,
        "SELECT_FIVE_DAYS": _SELECT_FIVE_DAYS,
        "SELECT_DAY": _SELECT_DAY,
        "SELECT_TODAY": _SELECT_TODAY,
        "ADD_NEW_CALENDAR": _ADD_NEW_CALENDAR,
        "CREATE_CALENDAR": _CREATE_CALENDAR,
        "UNSELECT_CALENDAR": _UNSELECT_CALENDAR,
        "SELECT_CALENDAR": _SELECT_CALENDAR,
        "SEARCH_SUBMIT": _SEARCH_SUBMIT,
        "EVENT_WIZARD_OPEN": _EVENT_WIZARD_OPEN,
        "CELL_CLICKED": _CELL_CLICKED,
        "ADD_EVENT": _ADD_EVENT,
        "CANCEL_ADD_EVENT": _CANCEL_ADD_EVENT,
        "DELETE_ADDED_EVENT": _DELETE_ADDED_EVENT,
        "EVENT_ADD_REMINDER": _EVENT_ADD_REMINDER,
        "EVENT_REMOVE_REMINDER": _EVENT_REMOVE_REMINDER,
        "EVENT_ADD_ATTENDEE": _EVENT_ADD_ATTENDEE,
        "EVENT_REMOVE_ATTENDEE": _EVENT_REMOVE_ATTENDEE,
    }
