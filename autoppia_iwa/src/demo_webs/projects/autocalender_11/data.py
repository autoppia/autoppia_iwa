from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

CALENDAR_NAMES = ["Personal", "Fitness", "Study", "Travel", "Holidays", "Birthdays", "Projects"]
EVENT_TITLES = ["Meeting", "Doctor appointment", "Lunch", "Conference call", "Workout", "Study session"]
EXISTING_CALENDAR_NAMES = ["Work", "Family"]
DESCRIPTIONS = [
    "Team meeting to discuss project updates",
    "Doctor's appointment",
    "Birthday celebration for a friend",
    "Weekly fitness class",
    "Family dinner at home",
    "Business trip to New York",
    "Online webinar on productivity",
    "Study session for exams",
    "Holiday planning session",
    "Client presentation review",
]

REMINDER_MINUTES = [5, 10, 15, 30, 60, 120]
ATTENDEE_EMAILS = ["test@example.com", "user1@work.com", "friend@email.net", "contact@domain.org"]


LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]

FIELD_OPERATORS_CREATE_CALENDAR_MAP = {
    "name": STRING_OPERATORS,
    "description": STRING_OPERATORS,
}
FIELD_OPERATORS_CHOOSE_CALENDAR_MAP = {
    "calendar_name": STRING_OPERATORS,
    "selected": [EQUALS],
}
FIELD_OPERATORS_ADD_EVENT_MAP = {
    "title": STRING_OPERATORS,
    "calendar": STRING_OPERATORS,
    "date": LOGICAL_OPERATORS,
    "start_time": LOGICAL_OPERATORS,
    "end_time": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_CLICK_CELL_MAP = {
    "source": STRING_OPERATORS,
    "date": LOGICAL_OPERATORS,
    "hour": LOGICAL_OPERATORS,
    "view": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_CANCEL_ADD_EVENT_MAP = {
    "source": STRING_OPERATORS,
    "date": LOGICAL_OPERATORS,
    "title": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_DELETE_ADD_EVENT_MAP = {
    "source": STRING_OPERATORS,
    "date": LOGICAL_OPERATORS,
    "event_title": STRING_OPERATORS,
    "calendar": STRING_OPERATORS,
}
FIELD_OPERATORS_SEARCH_SUBMIT_MAP = {
    "query": STRING_OPERATORS,
}

FIELD_OPERATORS_EVENT_REMINDER_MAP = {
    "minutes": LOGICAL_OPERATORS,
    "idx": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_EVENT_ATTENDEE_MAP = {
    "email": STRING_OPERATORS,
}
