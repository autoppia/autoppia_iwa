from __future__ import annotations

import re
from typing import Any

PROJECT_NUMBER = 5
WEB_PROJECT_ID = "autocrm"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import (
    ClickAction,
    NavigateAction,
    SelectAction,
    TypeAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

ACTIONS = [
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Filter matters to only show those with status 'Active'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8004/?seed=1",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "matters-nav-link",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "matters-nav-link",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "SelectAction",
                "value": "Active",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "matter-status-filter",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "value": "Active",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "matter-status-filter",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "FILTER_MATTER_STATUS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Sort matters by latest first.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8004/?seed=1",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='matters-nav-link' or @id='cases-link' or @id='projects-nav' or @id='legal-matters-link' or @id='matter-registry' or @id='tracking-link' or @id='active-cases-link' or @id='orders-link' or @id='engagements-nav' or @id='initiative-tracker']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='matters-nav-link' or @id='cases-link' or @id='projects-nav' or @id='legal-matters-link' or @id='matter-registry' or @id='tracking-link' or @id='active-cases-link' or @id='orders-link' or @id='engagements-nav' or @id='initiative-tracker']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "SelectAction",
                "value": "__CRM_MATTER_SORT_PREP__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "value": "__CRM_MATTER_SORT_PREP__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SelectAction",
                "value": "__CRM_MATTER_SORT_TARGET__",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "value": "__CRM_MATTER_SORT_TARGET__",
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']",
                        "case_sensitive": False,
                    },
                },
            },
        ],
        "use_case": "SORT_MATTER_BY_CREATED_AT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Edit the matter 'Estate Planning' to change status to 'On Hold'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8004/?seed=1",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "matters-nav-link",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "matters-nav-link",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "matter-search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "matter-search-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "Estate Planning",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "matter-search-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Estate Planning",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "matter-search-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "(//button[@aria-label='Edit matter' or @aria-label='Edit Matter' or normalize-space()='Edit'])[1]",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "(//button[@aria-label='Edit matter' or @aria-label='Edit Matter' or normalize-space()='Edit'])[1]",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "SelectAction",
                "value": "On Hold",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "edit-matter-status-select",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "value": "On Hold",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "edit-matter-status-select",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-matter-btn",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "save-matter-btn",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "UPDATE_MATTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Open the pending events list on the calendar page.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8004/?seed=1",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "calendar-nav-link",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "calendar-nav-link",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "toggle-pending-events",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "toggle-pending-events",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "VIEW_PENDING_EVENTS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Add a new calendar event on 2025-05-13 at 9:00am called 'Team Sync' with a Filing type.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
                "go_back": False,
                "attributes": {
                    "url": "http://localhost:8004/?seed=1",
                    "go_back": False,
                    "go_forward": False,
                },
                "go_forward": False,
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "calendar-nav-link",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "calendar-nav-link",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "xpathSelector",
                    "value": "//*[@id='day-number-2025-05-13']",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "xpathSelector",
                        "value": "//*[@id='day-number-2025-05-13']",
                        "case_sensitive": False,
                    }
                },
            },
            {
                "type": "TypeAction",
                "text": "Team Sync",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "event-label-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "Team Sync",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "event-label-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "TypeAction",
                "text": "09:00",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "event-time-input",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "text": "09:00",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "event-time-input",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "SelectAction",
                "value": "Filing",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "event-color-select",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "value": "Filing",
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "event-color-select",
                        "attribute": "id",
                        "case_sensitive": False,
                    },
                },
            },
            {
                "type": "ClickAction",
                "selector": {
                    "type": "attributeValueSelector",
                    "value": "save-btn",
                    "attribute": "id",
                    "case_sensitive": False,
                },
                "attributes": {
                    "selector": {
                        "type": "attributeValueSelector",
                        "value": "save-btn",
                        "attribute": "id",
                        "case_sensitive": False,
                    }
                },
            },
        ],
        "use_case": "NEW_CALENDAR_EVENT_ADDED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Search for matters that include 'Estate' in the title.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "SEARCH_MATTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "ADD_NEW_MATTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "VIEW_MATTER_DETAILS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Archive the matter whose status is set to 'Active'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "ARCHIVE_MATTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Delete the matter where status is set to 'Active'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "DELETE_MATTER",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "View details of client, whose client name is 'Jessica Taylor' and email is 'jtaylor@samplemail.com'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "VIEW_CLIENT_DETAILS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Search for clients named 'Smith'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "SEARCH_CLIENT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Add a new client named 'Nova Labs' with status Active.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "ADD_CLIENT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Delete the client named not equals 'Orion Tech Solutions'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "DELETE_CLIENT",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Filter clients to status Active with 3-4 matters.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "FILTER_CLIENTS",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Rename the document 'Retainer-Agreement-6908.pdf' to 'Retainer-Agreement-final.pdf'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "DOCUMENT_RENAMED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Delete the document named 'Retainer-Agreement-6908.pdf'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "DOCUMENT_DELETED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Add log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "NEW_LOG_ADDED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Edit the time log for 'Estate Planning' to change hours to 2.5.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "LOG_EDITED",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Delete the time log for 'Estate Planning' that recorded 2 hours.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "LOG_DELETE",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Search billing entries for 'contract' from this week.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "BILLING_SEARCH",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Change user name to 'Muhammad Ali'.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "CHANGE_USER_NAME",
        "has_success": False,
    },
    {
        "url": "http://localhost:8004/?seed=1",
        "prompt": "Open the help center.",
        "actions": [
            {
                "url": "http://localhost:8004/?seed=1",
                "type": "NavigateAction",
            }
        ],
        "use_case": "HELP_VIEWED",
        "has_success": False,
    },
]


def _normalize_field_name(raw_field: str) -> str:
    field = raw_field.strip().lower().replace(" ", "_")
    aliases = {
        "movie_name": "name",
        "film_name": "name",
    }
    return aliases.get(field, field)


def _parse_value_token(raw_value: str) -> Any:
    value = raw_value.strip().strip(".")
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _maybe_add_operator_criterion(criteria: dict[str, Any], field: str, operator: str, raw_value: str) -> None:
    criteria[_normalize_field_name(field)] = {
        "operator": operator,
        "value": _parse_value_token(raw_value),
    }


def _extract_event_criteria_from_prompt(prompt: str) -> dict[str, Any]:
    # Conservative parser: if prompt looks complex/ambiguous, return empty criteria.
    lowered = prompt.lower()
    tricky_markers = (" one of ", " or ", " either ", " directly ", " then ")
    if any(marker in lowered for marker in tricky_markers):
        return {}

    criteria: dict[str, Any] = {}

    not_equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+is\s+not\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+'([^']+)'",
    ]
    contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+contains\s+'([^']+)'",
    ]
    not_contains_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+does\s+not\s+contain\s+'([^']+)'",
        r"\b([a-zA-Z_ ]+?)\s+not\s+contain\s+'([^']+)'",
    ]
    equals_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+equals\s+'([^']+)'",
    ]
    less_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_equal_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+equal\s+'?([0-9]+(?:\.[0-9]+)?)'?",
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+or\s+equal\s+to\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    less_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+less\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]
    greater_than_patterns = [
        r"\b([a-zA-Z_ ]+?)\s+greater\s+than\s+'?([0-9]+(?:\.[0-9]+)?)'?",
    ]

    for pattern in not_contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_contains", value)

    for pattern in contains_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "contains", value)

    for pattern in not_equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "not_equals", value)

    for pattern in equals_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            criteria[_normalize_field_name(field)] = _parse_value_token(value)

    for pattern in less_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_equal", value)

    for pattern in greater_equal_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_equal", value)

    for pattern in less_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "less_than", value)

    for pattern in greater_than_patterns:
        for field, value in re.findall(pattern, prompt, flags=re.IGNORECASE):
            _maybe_add_operator_criterion(criteria, field, "greater_than", value)

    return criteria


def _build_raw_tests_from_actions(actions_data: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    raw_tests: dict[str, list[dict[str, Any]]] = {}
    for item in actions_data:
        use_case = str(item.get("use_case", "")).strip()
        if not use_case:
            continue
        prompt = str(item.get("prompt", ""))
        criteria = _extract_event_criteria_from_prompt(prompt)
        raw_tests[use_case] = [
            {
                "type": "CheckEventTest",
                "event_name": use_case,
                "event_criteria": criteria,
                "description": "Check if specific event was triggered",
            }
        ]
    return raw_tests


_RAW_TESTS: dict[str, list[dict[str, Any]]] = _build_raw_tests_from_actions(ACTIONS)
_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS.get(use_case, []))


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


FILTER_MATTER_STATUS = _uc(
    "FILTER_MATTER_STATUS",
    prompt="Filter matters to only show those with status 'Active'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("matters-nav-link")),
        SelectAction(selector=_id("matter-status-filter"), value="Active"),
    ],
)

SORT_MATTER_BY_CREATED_AT = _uc(
    "SORT_MATTER_BY_CREATED_AT",
    prompt="Sort matters by latest first.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(
            selector=_xp(
                "//*[@id='matters-nav-link' or @id='cases-link' or @id='projects-nav' or @id='legal-matters-link' or @id='matter-registry' or @id='tracking-link' or @id='active-cases-link' or @id='orders-link' or @id='engagements-nav' or @id='initiative-tracker']"
            )
        ),
        SelectAction(
            selector=_xp(
                "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']"
            ),
            value="__CRM_MATTER_SORT_PREP__",
        ),
        SelectAction(
            selector=_xp(
                "//*[@id='matter-sort-select' or @id='case-sort-select' or @id='project-sort-select' or @id='matter-order-select' or @id='case-order-select' or @id='project-order-select' or @id='sort-dropdown' or @id='order-dropdown' or @id='sort-selector' or @id='order-selector']"
            ),
            value="__CRM_MATTER_SORT_TARGET__",
        ),
    ],
)

UPDATE_MATTER = _uc(
    "UPDATE_MATTER",
    prompt="Edit the matter 'Estate Planning' to change status to 'On Hold'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("matters-nav-link")),
        ClickAction(selector=_id("matter-search-input")),
        TypeAction(selector=_id("matter-search-input"), text="Estate Planning"),
        ClickAction(selector=_xp("(//button[@aria-label='Edit matter' or @aria-label='Edit Matter' or normalize-space()='Edit'])[1]")),
        SelectAction(selector=_id("edit-matter-status-select"), value="On Hold"),
        ClickAction(selector=_id("save-matter-btn")),
    ],
)

VIEW_PENDING_EVENTS = _uc(
    "VIEW_PENDING_EVENTS",
    prompt="Open the pending events list on the calendar page.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("calendar-nav-link")),
        ClickAction(selector=_id("toggle-pending-events")),
    ],
)

NEW_CALENDAR_EVENT_ADDED = _uc(
    "NEW_CALENDAR_EVENT_ADDED",
    prompt="Add a new calendar event on 2025-05-13 at 9:00am called 'Team Sync' with a Filing type.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("calendar-nav-link")),
        ClickAction(selector=_xp("//*[@id='day-number-2025-05-13']")),
        TypeAction(selector=_id("event-label-input"), text="Team Sync"),
        TypeAction(selector=_id("event-time-input"), text="09:00"),
        SelectAction(selector=_id("event-color-select"), value="Filing"),
        ClickAction(selector=_id("save-btn")),
    ],
)

SEARCH_MATTER = _uc(
    "SEARCH_MATTER",
    prompt="Search for matters that include 'Estate' in the title.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ADD_NEW_MATTER = _uc(
    "ADD_NEW_MATTER",
    prompt="Create a matter named 'New Matter', with client 'Acme Co.' and status 'Active'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

VIEW_MATTER_DETAILS = _uc(
    "VIEW_MATTER_DETAILS",
    prompt="Go to the Matters page and click on 'Estate Planning' to view the details of that particular matter.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ARCHIVE_MATTER = _uc(
    "ARCHIVE_MATTER",
    prompt="Archive the matter whose status is set to 'Active'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DELETE_MATTER = _uc(
    "DELETE_MATTER",
    prompt="Delete the matter where status is set to 'Active'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

VIEW_CLIENT_DETAILS = _uc(
    "VIEW_CLIENT_DETAILS",
    prompt="View details of client, whose client name is 'Jessica Taylor' and email is 'jtaylor@samplemail.com'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

SEARCH_CLIENT = _uc(
    "SEARCH_CLIENT",
    prompt="Search for clients named 'Smith'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ADD_CLIENT = _uc(
    "ADD_CLIENT",
    prompt="Add a new client named 'Nova Labs' with status Active.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DELETE_CLIENT = _uc(
    "DELETE_CLIENT",
    prompt="Delete the client named not equals 'Orion Tech Solutions'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

FILTER_CLIENTS = _uc(
    "FILTER_CLIENTS",
    prompt="Filter clients to status Active with 3-4 matters.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DOCUMENT_RENAMED = _uc(
    "DOCUMENT_RENAMED",
    prompt="Rename the document 'Retainer-Agreement-6908.pdf' to 'Retainer-Agreement-final.pdf'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DOCUMENT_DELETED = _uc(
    "DOCUMENT_DELETED",
    prompt="Delete the document named 'Retainer-Agreement-6908.pdf'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

NEW_LOG_ADDED = _uc(
    "NEW_LOG_ADDED",
    prompt="Add log with matter 'Trademark Filing', description 'Prepare documents', and hours '2.5'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

LOG_EDITED = _uc(
    "LOG_EDITED",
    prompt="Edit the time log for 'Estate Planning' to change hours to 2.5.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

LOG_DELETE = _uc(
    "LOG_DELETE",
    prompt="Delete the time log for 'Estate Planning' that recorded 2 hours.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

BILLING_SEARCH = _uc(
    "BILLING_SEARCH",
    prompt="Search billing entries for 'contract' from this week.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

CHANGE_USER_NAME = _uc(
    "CHANGE_USER_NAME",
    prompt="Change user name to 'Muhammad Ali'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

HELP_VIEWED = _uc(
    "HELP_VIEWED",
    prompt="Open the help center.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)


def load_autocrm_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "FILTER_MATTER_STATUS": FILTER_MATTER_STATUS,
        "SORT_MATTER_BY_CREATED_AT": SORT_MATTER_BY_CREATED_AT,
        "UPDATE_MATTER": UPDATE_MATTER,
        "VIEW_PENDING_EVENTS": VIEW_PENDING_EVENTS,
        "NEW_CALENDAR_EVENT_ADDED": NEW_CALENDAR_EVENT_ADDED,
        "SEARCH_MATTER": SEARCH_MATTER,
        "ADD_NEW_MATTER": ADD_NEW_MATTER,
        "VIEW_MATTER_DETAILS": VIEW_MATTER_DETAILS,
        "ARCHIVE_MATTER": ARCHIVE_MATTER,
        "DELETE_MATTER": DELETE_MATTER,
        "VIEW_CLIENT_DETAILS": VIEW_CLIENT_DETAILS,
        "SEARCH_CLIENT": SEARCH_CLIENT,
        "ADD_CLIENT": ADD_CLIENT,
        "DELETE_CLIENT": DELETE_CLIENT,
        "FILTER_CLIENTS": FILTER_CLIENTS,
        "DOCUMENT_RENAMED": DOCUMENT_RENAMED,
        "DOCUMENT_DELETED": DOCUMENT_DELETED,
        "NEW_LOG_ADDED": NEW_LOG_ADDED,
        "LOG_EDITED": LOG_EDITED,
        "LOG_DELETE": LOG_DELETE,
        "BILLING_SEARCH": BILLING_SEARCH,
        "CHANGE_USER_NAME": CHANGE_USER_NAME,
        "HELP_VIEWED": HELP_VIEWED,
    }
