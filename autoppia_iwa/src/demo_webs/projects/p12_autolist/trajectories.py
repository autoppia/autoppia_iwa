"""
Concrete IWA flows for Autoppia AutoList (web_12).

Prompts and per-flow seeds follow `autolist_tasks.json` in autoppia_web_agents concrete_actions;
`CheckEventTest` payloads for each use case live in this file as Python literals (import-time init).

Base URL: http://localhost:8011 (FRONTEND_PORT_INDEX 11 → 8011).

The task date popover uses quick picks and a mini calendar (no month header). Flows use
visible calendar days or quick options when an exact ISO date is not reachable in the UI.
"""

from __future__ import annotations

PROJECT_NUMBER = 12
WEB_PROJECT_ID = "autolist"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    EvaluateAction,
    NavigateAction,
    SendKeysIWAAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

BASE = "http://localhost:8011"
DEFAULT_SEED = 1

# Seeds from autolist_tasks.json (?seed= on each task URL)
SEED_ADD_TASK_CLICKED = 682
SEED_SELECT_DATE_FOR_TASK = 715
SEED_SELECT_TASK_PRIORITY = 463
SEED_TASK_ADDED = 359
SEED_CANCEL_TASK_CREATION = 360
SEED_EDIT_TASK_MODAL_OPENED = 641
SEED_COMPLETE_TASK = 348
SEED_DELETE_TASK = 898
SEED_ADD_TEAM_CLICKED = 102
SEED_TEAM_MEMBERS_ADDED = 665
SEED_TEAM_ROLE_ASSIGNED = 216
SEED_TEAM_CREATED = 865

EDIT_TARGET_DESC = "Review pull requests and provide feedback to development team"


def _home(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/?seed={seed}"


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


# V3 id pools from web_12_autolist/src/dynamic/v3/data/id-variants.json
_TASK_NAME_IDS = (
    "task-name-input",
    "task-title-input",
    "todo-name",
    "task-summary-input",
    "task-headline-input",
)
_TASK_DESC_IDS = (
    "task-description-input",
    "task-notes-input",
    "task-body",
    "task-copy-input",
    "task-details-input",
)
_TEAM_NAME_IDS = (
    "team-name-input",
    "new-team-name-input",
    "create-team-name-input",
    "team-name-field",
    "team-input-name",
)
_TEAM_DESC_IDS = (
    "team-description-input",
    "new-team-description-input",
    "create-team-description-input",
    "team-description-field",
    "team-input-description",
)
# Task form footer: V3 ids + label text pool (cancel_action in text-variants.json)
_CANCEL_TASK_IDS = (
    "cancel-button",
    "dismiss-button",
    "abort-task-button",
    "close-task-button",
    "cancel-action",
    "cancel-edit-button",
    "dismiss-edit-button",
    "close-edit-button",
    "abort-edit-button",
    "cancel-edit-btn",
)


def _first_xpath_union(prefix: str, ids: tuple[str, ...]) -> Selector:
    union = " | ".join(f"{prefix}[@id='{i}']" for i in ids)
    return _xp(f"({union})[1]")


def _task_name_input() -> Selector:
    return _first_xpath_union("//input", _TASK_NAME_IDS)


def _task_description_input() -> Selector:
    return _first_xpath_union("//input", _TASK_DESC_IDS)


def _team_modal_name_input() -> Selector:
    return _first_xpath_union("//div[contains(@class,'ant-modal')]//input", _TEAM_NAME_IDS)


def _team_modal_description_input() -> Selector:
    # CreateTeamModal uses Input.TextArea → <textarea>, not <input>
    return _first_xpath_union("//div[contains(@class,'ant-modal')]//textarea", _TEAM_DESC_IDS)


def _date_picker_button() -> Selector:
    """Stable across V3 id variants (actual id may be due-date-trigger, date-picker-button-0, …)."""
    return _xp("//main//button[@data-dyn-key='date-picker-button']")


def _priority_picker_button() -> Selector:
    return _xp("//main//button[@data-dyn-key='priority-picker-button']")


def _sidebar_add_team_button() -> Selector:
    """Plus next to Teams (avoid ambiguous id overlap with modal submit)."""
    return _xp("//aside//div[contains(@class,'justify-between')][.//span[contains(@class,'anticon-team')]]//button[.//span[contains(@class,'anticon-plus')]]")


def _team_modal_member_select_trigger() -> Selector:
    """First Ant Select in team modal (members multiselect); label text varies (Team Members, People, …)."""
    return _xp("(//div[contains(@class,'ant-modal')]//div[contains(@class,'ant-select')][not(ancestor::div[contains(@class,'ant-select-dropdown')])]//div[contains(@class,'ant-select-selector')])[1]")


def _team_modal_role_select_for_member(name_fragment: str) -> Selector:
    return _xp(f"//div[contains(@class,'ant-modal')]//div[contains(@class,'ant-form-item')][.//label[contains(.,'{name_fragment}')]]//div[contains(@class,'ant-select-selector')]")


def _cancel_task_form_button_selector() -> Selector:
    id_or = " or ".join(f"@id='{i}'" for i in _CANCEL_TASK_IDS)
    text_or = " or ".join(f"normalize-space(.)='{t}'" for t in ("Cancel", "Dismiss", "Nevermind", "Close", "Back"))
    return _xp(f"//main//div[contains(@class,'border-t')]//button[{id_or} or {text_or}][1]")


_TASK_FORM_SUBMIT_IDS = (
    "submit-button",
    "save-task-button",
    "create-task-button",
    "confirm-task-button",
    "task-submit",
)


def _task_form_submit_button() -> Selector:
    union = " | ".join(f"//button[@id='{i}']" for i in _TASK_FORM_SUBMIT_IDS)
    return _xp(f"({union})[1]")


def _open_add_task_form() -> list[BaseAction]:
    return [
        WaitAction(time_seconds=2.5),
        EvaluateAction(
            script=r"""() => {
  const emptyCta = document.querySelector('button[data-dyn-key="cta-add-task"]');
  if (emptyCta) {
    emptyCta.click();
    return "empty-inbox-cta";
  }
  const aside = document.querySelector("aside");
  if (!aside) return "no-aside";
  const lis = aside.querySelectorAll("li");
  for (const li of lis) {
    const t = (li.textContent || "").replace(/\s+/g, " ").trim();
    if (/Getting Started|Start Here|Welcome|Begin|Quick Start/i.test(t)) {
      li.click();
      return "getting-started-nav";
    }
  }
  return "no-match";
}"""
        ),
        WaitAction(time_seconds=0.55),
        EvaluateAction(
            script=r"""() => {
  const visible = (el) => el && el.offsetParent !== null && el.getClientRects().length > 0;
  const nameIds = ["task-name-input","task-title-input","todo-name","task-summary-input","task-headline-input"];
  for (const id of nameIds) {
    const byId = document.getElementById(id);
    if (visible(byId)) return "form-already-visible";
  }
  const wrapBtn = document.querySelector('[data-dyn-key="add-first-task-button"] button');
  if (visible(wrapBtn)) {
    wrapBtn.click();
    return "getting-started-cta-wrap";
  }
  for (const b of document.querySelectorAll("main button")) {
    const t = (b.textContent || "").trim();
    if (!visible(b)) continue;
    if (/Add your first task|first task/i.test(t)) {
      b.click();
      return "getting-started-cta-text";
    }
  }
  return "could-not-open-form";
}"""
        ),
        WaitAction(time_seconds=0.45),
    ]


def _pick_date_tomorrow() -> list[BaseAction]:
    return [
        ClickAction(selector=_date_picker_button()),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_xp("//button[.//span[normalize-space()='Tomorrow']]")),
        WaitAction(time_seconds=0.25),
    ]


def _pick_date_after_apr_28() -> list[BaseAction]:
    """Mini calendar: pick a late in-month day (e.g. 29-30) so date > 2026-04-28 when April is in view."""
    return [
        ClickAction(selector=_date_picker_button()),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_xp("(//td[contains(@class,'ant-picker-cell-in-view') and not(contains(@class,'ant-picker-cell-disabled'))]//div[normalize-space()='30'])[1]")),
        WaitAction(time_seconds=0.3),
    ]


def _pick_priority(label: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_priority_picker_button()),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_xp(f"//div[contains(@class,'rounded-xl')][contains(@class,'shadow-lg')]//button[.//span[normalize-space()='{label}']]")),
        WaitAction(time_seconds=0.2),
    ]


def _cancel_task_form_button() -> list[BaseAction]:
    return [
        ClickAction(selector=_cancel_task_form_button_selector()),
        WaitAction(time_seconds=0.35),
    ]


def _select_ant_option_containing(text: str) -> list[BaseAction]:
    return [
        ClickAction(
            selector=_xp(
                f"(//div[contains(@class,'ant-select-dropdown')][.//div[contains(@class,'ant-select-item-option')]]//div[contains(@class,'ant-select-item-option') and contains(.,'{text}')])[last()]"
            )
        ),
        WaitAction(time_seconds=0.25),
    ]


# --- Flows: names match autolist_tasks.json use_case.name (AUTOLIST_*); tests below. ---


_RAW_TESTS: dict[str, list[dict]] = {
    "AUTOLIST_ADD_TASK_CLICKED": [{"type": "CheckEventTest", "event_name": "AUTOLIST_ADD_TASK_CLICKED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "AUTOLIST_SELECT_DATE_FOR_TASK": [{"type": "CheckEventTest", "event_name": "AUTOLIST_SELECT_DATE_FOR_TASK", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "AUTOLIST_SELECT_TASK_PRIORITY": [
        {"type": "CheckEventTest", "event_name": "AUTOLIST_SELECT_TASK_PRIORITY", "event_criteria": {"priority": "Low"}, "description": "Check if specific event was triggered"}
    ],
    "AUTOLIST_TASK_ADDED": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_TASK_ADDED",
            "event_criteria": {
                "name": {"operator": "not_contains", "value": "mvk"},
                "description": {"operator": "not_equals", "value": "Create user communication plan for important announcements"},
                "date": {"operator": "less_than", "value": "2026-04-24"},
                "priority": {"operator": "not_equals", "value": "Low"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_CANCEL_TASK_CREATION": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_CANCEL_TASK_CREATION",
            "event_criteria": {
                "name": {"operator": "not_contains", "value": "vqs"},
                "description": {"operator": "contains", "value": "ate"},
                "date": {"operator": "greater_than", "value": "2026-04-28"},
                "priority": 1,
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_EDIT_TASK_MODAL_OPENED": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_EDIT_TASK_MODAL_OPENED",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "Implement data anonymization"},
                "description": "Review pull requests and provide feedback to development team",
                "date": {"operator": "less_than", "value": "2026-04-25"},
                "priority": {"operator": "not_equals", "value": "Low"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_COMPLETE_TASK": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_COMPLETE_TASK",
            "event_criteria": {
                "name": {"operator": "contains", "value": "t"},
                "description": {"operator": "not_equals", "value": "Plan tasks and priorities for the next development sprint"},
                "date": {"operator": "less_than", "value": "2026-04-22"},
                "priority": {"operator": "not_equals", "value": "Low"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_DELETE_TASK": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_DELETE_TASK",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "Review vendor contracts"},
                "description": {"operator": "not_contains", "value": "uwv"},
                "date": {"operator": "less_equal", "value": "2026-04-27"},
                "priority": 3,
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_ADD_TEAM_CLICKED": [{"type": "CheckEventTest", "event_name": "AUTOLIST_ADD_TEAM_CLICKED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "AUTOLIST_TEAM_MEMBERS_ADDED": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_TEAM_MEMBERS_ADDED",
            "event_criteria": {"members": {"operator": "in_list", "value": ["John Doe", "Emily Davis"]}, "member_count": 2},
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_TEAM_ROLE_ASSIGNED": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_TEAM_ROLE_ASSIGNED",
            "event_criteria": {"member": {"operator": "not_contains", "value": "jmu"}, "role": "Product Manager"},
            "description": "Check if specific event was triggered",
        }
    ],
    "AUTOLIST_TEAM_CREATED": [
        {
            "type": "CheckEventTest",
            "event_name": "AUTOLIST_TEAM_CREATED",
            "event_criteria": {
                "name": {"operator": "not_contains", "value": "wiu"},
                "description": {"operator": "not_equals", "value": "Creates and manages training and professional development programs."},
                "member": {"operator": "not_contains", "value": "oex"},
                "role": {"operator": "not_equals", "value": "Admin"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


AUTOLIST_ADD_TASK_CLICKED = _uc(
    "AUTOLIST_ADD_TASK_CLICKED",
    prompt="Please add a task by clicking the button to create a new task.",
    actions=[
        NavigateAction(url=_home(SEED_ADD_TASK_CLICKED)),
        *_open_add_task_form(),
    ],
)

AUTOLIST_ADD_TEAM_CLICKED = _uc(
    "AUTOLIST_ADD_TEAM_CLICKED",
    prompt="Please click the button to add a new team.",
    actions=[
        NavigateAction(url=_home(SEED_ADD_TEAM_CLICKED)),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_sidebar_add_team_button()),
        WaitAction(time_seconds=0.45),
    ],
)

AUTOLIST_SELECT_DATE_FOR_TASK = _uc(
    "AUTOLIST_SELECT_DATE_FOR_TASK",
    prompt="Please set the date for the task to '2025-07-21'.",
    actions=[
        NavigateAction(url=_home(SEED_SELECT_DATE_FOR_TASK)),
        *_open_add_task_form(),
        # Task JSON tests use empty event_criteria; quick "Tomorrow" reliably fires SELECT_DATE.
        *_pick_date_tomorrow(),
    ],
)

AUTOLIST_SELECT_TASK_PRIORITY = _uc(
    "AUTOLIST_SELECT_TASK_PRIORITY",
    prompt="Set the task priority to 'Low'.",
    actions=[
        NavigateAction(url=_home(SEED_SELECT_TASK_PRIORITY)),
        *_open_add_task_form(),
        *_pick_priority("Low"),
    ],
)

AUTOLIST_TASK_ADDED = _uc(
    "AUTOLIST_TASK_ADDED",
    prompt=(
        "Add a task whose name NOT contains 'mvk' and description NOT equals "
        "'Create user communication plan for important announcements' and date less than '2026-04-24' "
        "and priority NOT equals 'Low'."
    ),
    actions=[
        NavigateAction(url=_home(SEED_TASK_ADDED)),
        *_open_add_task_form(),
        TypeAction(selector=_task_name_input(), text="Quarterly roadmap sync"),
        TypeAction(
            selector=_task_description_input(),
            text="Align stakeholders on milestones and owners.",
        ),
        *_pick_date_tomorrow(),
        *_pick_priority("Medium"),
        ClickAction(selector=_task_form_submit_button()),
        WaitAction(time_seconds=0.55),
    ],
)

AUTOLIST_CANCEL_TASK_CREATION = _uc(
    "AUTOLIST_CANCEL_TASK_CREATION",
    prompt=("Please cancel the task creation where the name does NOT contain 'vqs', the description contains 'ate', the date is AFTER '2026-04-28', and the priority equals '1'."),
    actions=[
        NavigateAction(url=_home(SEED_CANCEL_TASK_CREATION)),
        *_open_add_task_form(),
        TypeAction(selector=_task_name_input(), text="Corporate strategy update"),
        TypeAction(selector=_task_description_input(), text="Consolidate quarterly metrics."),
        *_pick_date_after_apr_28(),
        *_pick_priority("Highest"),
        *_cancel_task_form_button(),
    ],
)

AUTOLIST_EDIT_TASK_MODAL_OPENED = _uc(
    "AUTOLIST_EDIT_TASK_MODAL_OPENED",
    prompt=(
        "Edit task modal open where name is NOT 'Implement data anonymization' and description equals "
        "'Review pull requests and provide feedback to development team' and date is LESS THAN '2026-04-25' "
        "and priority is NOT 'Low'."
    ),
    actions=[
        NavigateAction(url=_home(SEED_EDIT_TASK_MODAL_OPENED)),
        WaitAction(time_seconds=3.0),
        ClickAction(selector=_xp("//div[@data-dyn-key='task-card'][.//div[contains(.,'" + EDIT_TARGET_DESC.replace("'", "\\'") + "')]]//button[@title='Edit'][1]")),
        WaitAction(time_seconds=0.5),
    ],
)

AUTOLIST_COMPLETE_TASK = _uc(
    "AUTOLIST_COMPLETE_TASK",
    prompt=(
        "Complete task whose name contains 't' and description not equals 'Plan tasks and priorities for the next development sprint' and date less than '2026-04-22' and priority not equals 'Low'."
    ),
    actions=[
        NavigateAction(url=_home(SEED_COMPLETE_TASK)),
        WaitAction(time_seconds=3.0),
        ClickAction(
            selector=_xp(
                "(//div[@data-dyn-key='task-card']"
                "[.//div[contains(@class,'font-semibold')][contains(normalize-space(.),'t')]]"
                "[.//div[contains(@class,'text-gray-600')]"
                "[not(normalize-space()='Plan tasks and priorities for the next development sprint')]]"
                "//button[@aria-label='Mark complete'])[1]"
            )
        ),
        WaitAction(time_seconds=0.5),
    ],
)

AUTOLIST_DELETE_TASK = _uc(
    "AUTOLIST_DELETE_TASK",
    prompt=("Delete task whose name not equals 'Review vendor contracts' and description not contains 'uwv' and date less equal '2026-04-27' and priority equals '3'."),
    actions=[
        NavigateAction(url=_home(SEED_DELETE_TASK)),
        WaitAction(time_seconds=3.0),
        ClickAction(
            selector=_xp(
                "(//div[@data-dyn-key='task-card']"
                "[not(.//div[contains(@class,'font-semibold')][normalize-space()='Review vendor contracts'])]"
                "[.//div[contains(@class,'flex')][contains(@class,'gap-3')]"
                "//span[last()][contains(normalize-space(.),'3')]]"
                "//button[@title='Delete'])[1]"
            )
        ),
        WaitAction(time_seconds=0.5),
    ],
)

AUTOLIST_TEAM_MEMBERS_ADDED = _uc(
    "AUTOLIST_TEAM_MEMBERS_ADDED",
    prompt="Please add members 'John Doe' and 'Emily Davis' to the team with a member_count of 2",
    actions=[
        NavigateAction(url=_home(SEED_TEAM_MEMBERS_ADDED)),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_sidebar_add_team_button()),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_team_modal_member_select_trigger()),
        WaitAction(time_seconds=0.35),
        *_select_ant_option_containing("John Doe"),
        *_select_ant_option_containing("Emily Davis"),
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.3),
    ],
)

AUTOLIST_TEAM_ROLE_ASSIGNED = _uc(
    "AUTOLIST_TEAM_ROLE_ASSIGNED",
    prompt="Assign the role of 'Product Manager' to a team member whose name does NOT contain 'jmu'.",
    actions=[
        NavigateAction(url=_home(SEED_TEAM_ROLE_ASSIGNED)),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_sidebar_add_team_button()),
        WaitAction(time_seconds=0.45),
        ClickAction(selector=_team_modal_member_select_trigger()),
        WaitAction(time_seconds=0.35),
        *_select_ant_option_containing("Jane Smith"),
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_team_modal_role_select_for_member("Jane Smith")),
        WaitAction(time_seconds=0.3),
        *_select_ant_option_containing("Product Manager"),
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.25),
    ],
)

AUTOLIST_TEAM_CREATED = _uc(
    "AUTOLIST_TEAM_CREATED",
    prompt=(
        "Create a team whose name NOT CONTAINS 'wiu' and description NOT EQUALS 'Creates and manages training and professional development programs.' "
        "and member NOT CONTAINS 'oex' and role NOT EQUALS 'Admin'."
    ),
    actions=[
        NavigateAction(url=_home(SEED_TEAM_CREATED)),
        WaitAction(time_seconds=2.0),
        ClickAction(selector=_sidebar_add_team_button()),
        WaitAction(time_seconds=0.45),
        TypeAction(selector=_team_modal_name_input(), text="Platform Engineering"),
        TypeAction(
            selector=_team_modal_description_input(),
            text="Owns core APIs and reliability.",
        ),
        ClickAction(selector=_team_modal_member_select_trigger()),
        WaitAction(time_seconds=0.35),
        *_select_ant_option_containing("John Doe"),
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.35),
        ClickAction(selector=_team_modal_role_select_for_member("John Doe")),
        WaitAction(time_seconds=0.3),
        *_select_ant_option_containing("Developer"),
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.5),
        EvaluateAction(
            script=r"""() => {
  const btn = document.querySelector(".ant-modal-footer .ant-btn-primary");
  if (!btn) return "no-primary-btn";
  btn.scrollIntoView({ block: "center", inline: "nearest" });
  (btn).click();
  return "clicked-save";
}"""
        ),
        WaitAction(time_seconds=0.55),
    ],
)


def load_autolist_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "AUTOLIST_ADD_TASK_CLICKED": AUTOLIST_ADD_TASK_CLICKED,
        "AUTOLIST_ADD_TEAM_CLICKED": AUTOLIST_ADD_TEAM_CLICKED,
        "AUTOLIST_SELECT_DATE_FOR_TASK": AUTOLIST_SELECT_DATE_FOR_TASK,
        "AUTOLIST_SELECT_TASK_PRIORITY": AUTOLIST_SELECT_TASK_PRIORITY,
        "AUTOLIST_TASK_ADDED": AUTOLIST_TASK_ADDED,
        "AUTOLIST_CANCEL_TASK_CREATION": AUTOLIST_CANCEL_TASK_CREATION,
        "AUTOLIST_EDIT_TASK_MODAL_OPENED": AUTOLIST_EDIT_TASK_MODAL_OPENED,
        "AUTOLIST_COMPLETE_TASK": AUTOLIST_COMPLETE_TASK,
        "AUTOLIST_DELETE_TASK": AUTOLIST_DELETE_TASK,
        "AUTOLIST_TEAM_MEMBERS_ADDED": AUTOLIST_TEAM_MEMBERS_ADDED,
        "AUTOLIST_TEAM_ROLE_ASSIGNED": AUTOLIST_TEAM_ROLE_ASSIGNED,
        "AUTOLIST_TEAM_CREATED": AUTOLIST_TEAM_CREATED,
    }


if __name__ == "__main__":
    for name, uc in sorted(load_autolist_use_case_completion_flows().items()):
        if name.startswith("AUTOLIST_"):
            print(name, "->", (uc.prompt or "")[:72], "...")
