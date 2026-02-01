from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST



POPULAR_SKILLS = [
    "JavaScript",
    "TypeScript",
    "Python",
    "Java",
    "C#",
    "C++",
    "Ruby",
    "Go",
    "Swift",
    "Kotlin",
    "Objective-C",
    "PHP",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue.js",
    "Node.js",
    "Django",
    "Flask",
]


def expert_data_modified(experts):
    expert_data_modified = []
    for data in experts:
        new_data = data.copy()
        if data.get("lastReview") and isinstance(data["lastReview"], dict):
            for k, v in data["lastReview"].items():
                new_data["lastReview" + k.title()] = v
        expert_data_modified.append(new_data)
    return expert_data_modified


STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
LIST_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]

FIELD_OPERATORS_USER_BOOK_CONSULTANT_MAP = {
    "country": STRING_OPERATORS,
    "name": STRING_OPERATORS,
    "jobs": LOGICAL_OPERATORS,
    "rate": STRING_OPERATORS,
    "rating": LOGICAL_OPERATORS,
    "role": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_HIRE_BUTTON = {
    "country": STRING_OPERATORS,
    "name": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_HIRING_TEAM = {
    "name": STRING_OPERATORS,
    "team": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_HIRING_CONSULTANT = {
    "country": STRING_OPERATORS,
    "name": STRING_OPERATORS,
    "increaseHowMuch": STRING_OPERATORS,
    "increaseWhen": STRING_OPERATORS,
    "paymentType": EQUALITY_OPERATORS,
    "role": STRING_OPERATORS,
    "rate": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_CANCEL_HIRE = {
    "country": STRING_OPERATORS,
    "name": STRING_OPERATORS,
    "rate": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_POSTING_A_JOB = {"page": STRING_OPERATORS, "source": STRING_OPERATORS}

FIELD_OPERATORS_MAP_WRITING_A_JOB_TITLE = {
    "query": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SEARCH_SKILL = {
    "skill": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_ADD_SKILL = {
    "skill": STRING_OPERATORS,
}
FIELD_OPERATORS_MAP_REMOVE_SKILL = {
    "skill": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SUBMIT_JOB = {
    "description": STRING_OPERATORS,
    "budgetType": STRING_OPERATORS,
    "duration": STRING_OPERATORS,
    "rate_from": LOGICAL_OPERATORS,
    "rate_to": LOGICAL_OPERATORS,
    "scope": STRING_OPERATORS,
    "skills": LIST_OPERATORS,
    "title": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_BUDGET_TYPE = {
    "budget_type": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_PROJECT_SIZE = {
    "scope": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_TIMELINE = {
    "duration": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_RATE_RANGE = {
    "rate_from": LOGICAL_OPERATORS,
    "rate_to": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_MAP_JOB_DESCRIPTION = {
    "description": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_CLOSE_JOB_POSTING = {**FIELD_OPERATORS_MAP_SUBMIT_JOB}

FIELD_OPERATORS_MAP_NAVBAR_CLICK = {
    "label": STRING_OPERATORS,
    "href": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_FAVORITE_EXPERT = {
    "expert_name": STRING_OPERATORS,
    "expert_slug": STRING_OPERATORS,
    "source": STRING_OPERATORS,
    "country": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_BROWSE_FAVORITE_EXPERT = {
    "source": STRING_OPERATORS,
}


FIELD_OPERATORS_MAP_CONTACT_EXPERT_MESSAGE = {
    "expert_name": STRING_OPERATORS,
    "expert_slug": STRING_OPERATORS,
    "source": STRING_OPERATORS,
    "message_length": LOGICAL_OPERATORS,
    "message": STRING_OPERATORS,
    "country": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_EDIT_ABOUT = {
    "username": STRING_OPERATORS,
    "length": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_MAP_EDIT_PROFILE_FIELD = {
    "value": STRING_OPERATORS,
}
FIELD_OPERATORS_MAP_CONTACT_EXPERT_MESSAGE_SENT = {
    **FIELD_OPERATORS_MAP_HIRE_BUTTON,
    "message": STRING_OPERATORS,
}
