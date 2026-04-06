from __future__ import annotations

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


# CheckEventTest payloads aligned with autocrm_tasks.json (per use_case.name).
_RAW_TESTS: dict[str, list[dict]] = {
    "ADD_NEW_MATTER": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_NEW_MATTER",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "Litigation 2025"},
                "client": {"operator": "contains", "value": "Emma"},
                "status": {"operator": "contains", "value": "On hold"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_MATTER_DETAILS": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_MATTER_DETAILS",
            "event_criteria": {"status": {"operator": "not_contains", "value": "Archived"}, "name": "Contract Review"},
            "description": "Check if specific event was triggered",
        }
    ],
    "DELETE_MATTER": [
        {
            "type": "CheckEventTest",
            "event_name": "DELETE_MATTER",
            "event_criteria": {"name": {"operator": "not_contains", "value": "Contract Review"}, "status": {"operator": "not_equals", "value": "Archived"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "ARCHIVE_MATTER": [
        {
            "type": "CheckEventTest",
            "event_name": "ARCHIVE_MATTER",
            "event_criteria": {"name": {"operator": "not_contains", "value": "Litigation Support"}, "status": {"operator": "contains", "value": "Pe"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "VIEW_CLIENT_DETAILS": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_CLIENT_DETAILS",
            "event_criteria": {"matters": {"operator": "greater_than", "value": 4.64}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_CLIENT": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_CLIENT",
            "event_criteria": {"query": {"operator": "not_equals", "value": "Commercial Legal"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "DOCUMENT_DELETED": [
        {
            "type": "CheckEventTest",
            "event_name": "DOCUMENT_DELETED",
            "event_criteria": {"version": {"operator": "not_equals", "value": "v5"}, "size": {"operator": "less_equal", "value": "1351 KB"}, "name": "Complaint-5725.xlsx"},
            "description": "Check if specific event was triggered",
        }
    ],
    "NEW_CALENDAR_EVENT_ADDED": [
        {
            "type": "CheckEventTest",
            "event_name": "NEW_CALENDAR_EVENT_ADDED",
            "event_criteria": {
                "label": {"operator": "not_contains", "value": "Monthly Sales Review"},
                "time": {"operator": "greater_than", "value": "9:30am"},
                "date": {"operator": "less_than", "value": "2026-05-18"},
                "event_type": "Matter/Event",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "NEW_LOG_ADDED": [{"type": "CheckEventTest", "event_name": "NEW_LOG_ADDED", "event_criteria": {"hours": 3.6}, "description": "Check if specific event was triggered"}],
    "LOG_DELETE": [
        {
            "type": "CheckEventTest",
            "event_name": "LOG_DELETE",
            "event_criteria": {
                "hours": {"operator": "not_equals", "value": 6.0},
                "matter": {"operator": "not_contains", "value": "Franchise Agreement"},
                "status": {"operator": "contains", "value": "Bill"},
                "client": {"operator": "not_equals", "value": "Strategic Partners"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CHANGE_USER_NAME": [
        {
            "type": "CheckEventTest",
            "event_name": "CHANGE_USER_NAME",
            "event_criteria": {"name": {"operator": "not_contains", "value": "Builder"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_MATTER": [
        {"type": "CheckEventTest", "event_name": "SEARCH_MATTER", "event_criteria": {"query": {"operator": "contains", "value": "Data"}}, "description": "Check if specific event was triggered"}
    ],
    "ADD_CLIENT": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_CLIENT",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "United Legal"},
                "email": {"operator": "not_equals", "value": "unitedlegal@enterprises.com"},
                "matters": {"operator": "less_than", "value": 3},
                "status": "Active",
                "last": {"operator": "not_equals", "value": "1mo ago"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "DELETE_CLIENT": [
        {
            "type": "CheckEventTest",
            "event_name": "DELETE_CLIENT",
            "event_criteria": {
                "name": {"operator": "not_equals", "value": "Nicole Miller"},
                "email": {"operator": "not_contains", "value": "nicolemiller@services.com"},
                "matters": {"operator": "not_equals", "value": 8},
                "status": "Inactive",
                "last": {"operator": "contains", "value": "Today"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "FILTER_CLIENTS": [{"type": "CheckEventTest", "event_name": "FILTER_CLIENTS", "event_criteria": {"status": "Active", "matters": "5+"}, "description": "Check if specific event was triggered"}],
    "FILTER_MATTER_STATUS": [
        {
            "type": "CheckEventTest",
            "event_name": "FILTER_MATTER_STATUS",
            "event_criteria": {"status": {"operator": "not_equals", "value": "Archived"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SORT_MATTER_BY_CREATED_AT": [
        {"type": "CheckEventTest", "event_name": "SORT_MATTER_BY_CREATED_AT", "event_criteria": {"direction": "asc"}, "description": "Check if specific event was triggered"}
    ],
    "UPDATE_MATTER": [{"type": "CheckEventTest", "event_name": "UPDATE_MATTER", "event_criteria": {"updated": "1mo ago"}, "description": "Check if specific event was triggered"}],
    "VIEW_PENDING_EVENTS": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_PENDING_EVENTS",
            "event_criteria": {"earliest": {"operator": "not_equals", "value": "2025-12-12"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "DOCUMENT_RENAMED": [
        {
            "type": "CheckEventTest",
            "event_name": "DOCUMENT_RENAMED",
            "event_criteria": {"new_name": {"operator": "not_equals", "value": "Agreement-337.docx"}, "previous_name": {"operator": "not_equals", "value": "Complaint-2574.xlsx"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "LOG_EDITED": [
        {
            "type": "CheckEventTest",
            "event_name": "LOG_EDITED",
            "event_criteria": {
                "client": {"operator": "contains", "value": "itta"},
                "status": {"operator": "contains", "value": "B"},
                "matter": {"operator": "not_contains", "value": "Corporate Formation"},
                "hours": {"operator": "greater_equal", "value": 1.2},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "BILLING_SEARCH": [
        {
            "type": "CheckEventTest",
            "event_name": "BILLING_SEARCH",
            "event_criteria": {"query": "Regulatory Approval", "date_filter": {"operator": "contains", "value": "Previous 2 weeks"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "HELP_VIEWED": [{"type": "CheckEventTest", "event_name": "HELP_VIEWED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


FILTER_MATTER_STATUS = _uc(
    "FILTER_MATTER_STATUS",
    prompt="Filter matters to exclude those with status 'Archived'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("matters-nav-link")),
        SelectAction(selector=_id("matter-status-filter"), value="Active"),
    ],
)

SORT_MATTER_BY_CREATED_AT = _uc(
    "SORT_MATTER_BY_CREATED_AT",
    prompt="Sort matters by created date in 'asc' order.",
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
    prompt="Update any matter where the updated date equals '1mo ago'.",
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
    prompt="Show me the pending events on the calendar where the earliest date is NOT '2025-12-12'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
        ClickAction(selector=_id("calendar-nav-link")),
        ClickAction(selector=_id("toggle-pending-events")),
    ],
)

NEW_CALENDAR_EVENT_ADDED = _uc(
    "NEW_CALENDAR_EVENT_ADDED",
    prompt="Add a new calendar event where the label does NOT contain 'Monthly Sales Review', the time is GREATER than '9:30am', the date is LESS than '2026-05-18', and the event_type equals 'Matter/Event'.",
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
    prompt="Search for matters where the query contains 'Data'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ADD_NEW_MATTER = _uc(
    "ADD_NEW_MATTER",
    prompt="Create a matter with the name that is NOT 'Litigation 2025', with client that contains 'Emma', and status that contains 'On hold'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

VIEW_MATTER_DETAILS = _uc(
    "VIEW_MATTER_DETAILS",
    prompt="Retrieve details of the matter where the status does NOT contain 'Archived' and the name equals 'Contract Review'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ARCHIVE_MATTER = _uc(
    "ARCHIVE_MATTER",
    prompt="Archive the matter where the name does NOT contain 'Litigation Support' and the status contains 'Pe'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DELETE_MATTER = _uc(
    "DELETE_MATTER",
    prompt="Delete the matter where the name does NOT contain 'Contract Review' and the status is NOT 'Archived'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

VIEW_CLIENT_DETAILS = _uc(
    "VIEW_CLIENT_DETAILS",
    prompt="View details of clients where the matters are greater than '4.64'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

SEARCH_CLIENT = _uc(
    "SEARCH_CLIENT",
    prompt="Search for clients where the query is NOT 'Commercial Legal'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

ADD_CLIENT = _uc(
    "ADD_CLIENT",
    prompt="Add a new client named 'Nova Labs' with email not equals 'unitedlegal@enterprises.com', matters less than 3, status equals 'Active', and last not equals '1mo ago'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DELETE_CLIENT = _uc(
    "DELETE_CLIENT",
    prompt="Delete the client whose name is NOT 'Nicole Miller', email does NOT contain 'nicolemiller@services.com', matters is NOT '8', status equals 'Inactive', and last contains 'Today'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

FILTER_CLIENTS = _uc(
    "FILTER_CLIENTS",
    prompt="Retrieve details of clients where the status equals 'Active' and the matters equals '5+'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DOCUMENT_RENAMED = _uc(
    "DOCUMENT_RENAMED",
    prompt="Rename the document 'Retainer-Agreement.pdf' to 'Retainer-Agreement-final.pdf' where the new_name is NOT 'Agreement-337.docx' and the previous_name is NOT 'Complaint-2574.xlsx'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

DOCUMENT_DELETED = _uc(
    "DOCUMENT_DELETED",
    prompt="Please delete the document with name equals 'Complaint-5725.xlsx' that has a version NOT equal to 'v5' and a size less than or equal to '1351 KB'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

NEW_LOG_ADDED = _uc(
    "NEW_LOG_ADDED",
    prompt="Add log entry with hours equals '3.6'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

LOG_EDITED = _uc(
    "LOG_EDITED",
    prompt="Edit log entry where client contains 'itta', status contains 'B', matter does not contain 'Corporate Formation', and hours are greater than or equal to 1.2",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

LOG_DELETE = _uc(
    "LOG_DELETE",
    prompt="Delete the time log where hours is NOT equal to '6.0', matter does NOT CONTAIN 'Franchise Agreement', status CONTAINS 'Bill', and client is NOT equal to 'Strategic Partners'.",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

BILLING_SEARCH = _uc(
    "BILLING_SEARCH",
    prompt="Retrieve billing entries where the query equals 'Regulatory Approval' and the date_filter contains 'Previous 2 weeks'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

CHANGE_USER_NAME = _uc(
    "CHANGE_USER_NAME",
    prompt="Change user name to 'John Smith' that does NOT contain 'Builder'",
    actions=[
        NavigateAction(url="http://localhost:8004/?seed=1"),
    ],
)

HELP_VIEWED = _uc(
    "HELP_VIEWED",
    prompt="Open the help/FAQ page.",
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
