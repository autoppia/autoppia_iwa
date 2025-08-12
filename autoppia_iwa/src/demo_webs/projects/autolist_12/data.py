from datetime import datetime

from ...projects.operators import (
    CONTAINS,
    EQUALS,
    GREATER_EQUAL,
    GREATER_THAN,
    LESS_EQUAL,
    LESS_THAN,
    NOT_CONTAINS,
    NOT_EQUALS,
)

TASKS_DATA = [
    {
        "name": "Buy groceries",
        "description": "Milk, Bread, Eggs, and Cheese",
        "date": datetime(2025, 8, 15),
        "priority": 1,
        "priority_label": "High",
        "action": "add",
        "source": "main_view",
        "is_editing": False,
        "was_previously_selected": False,
    },
    {
        "name": "Finish project report",
        "description": "Complete the Q3 financial analysis section.",
        "date": datetime(2025, 8, 20),
        "priority": 2,
        "priority_label": "Medium",
        "action": "update",
        "source": "task_modal",
        "is_editing": True,
        "was_previously_selected": True,
    },
    {
        "name": "Call the doctor",
        "description": "Schedule annual check-up.",
        "date": datetime(2025, 9, 1),
        "priority": 3,
        "priority_label": "Low",
        "action": "add",
        "source": "quick_add",
        "is_editing": False,
        "was_previously_selected": False,
    },
    {
        "name": "Plan team meeting",
        "description": "Agenda: review sprint goals and assign tasks.",
        "date": None,
        "priority": 4,
        "priority_label": "None",
        "action": "add",
        "source": "main_view",
        "is_editing": False,
        "was_previously_selected": False,
    },
]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]


# --- Field Operator Mappings ---
FIELD_OPERATORS_ADD_TASK_CLICKED_MAP = {
    "source": STRING_OPERATORS,
}
FIELD_OPERATORS_SELECT_DATE_MAP = {
    "wasPreviouslySelected": EQUALITY_OPERATORS,
}
FIELD_OPERATORS_SELECT_PRIORITY_MAP = {
    "priority": LOGICAL_OPERATORS,
    "label": STRING_OPERATORS,
}
FIELD_OPERATORS_TASK_ADDED_MAP = {
    "action": EQUALITY_OPERATORS,
    "name": STRING_OPERATORS,
    "description": STRING_OPERATORS,
    "priority": EQUALITY_OPERATORS,
}
FIELD_OPERATORS_CANCEL_TASK_MAP = {
    "current_name": STRING_OPERATORS,
    "priority": EQUALITY_OPERATORS,
    "is_editing": EQUALITY_OPERATORS,
}
FIELD_OPERATORS_EDIT_MODAL_MAP = {
    "name": STRING_OPERATORS,
    "description": STRING_OPERATORS,
    "priority": STRING_OPERATORS,
}
FIELD_OPERATORS_COMPLETE_TASK_MAP = {
    "name": STRING_OPERATORS,
}
FIELD_OPERATORS_DELETE_TASK_MAP = {
    "name": STRING_OPERATORS,
}
