from autoppia_iwa.src.demo_webs.projects.operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

COMPANIES = [
    {"name": "Adobe", "desc": "Company • Design tools", "logo": "https://logo.clearbit.com/adobe.com"},
    {"name": "Y Combinator", "desc": "Company • Start up accelerator", "logo": "https://logo.clearbit.com/ycombinator.com"},
    {"name": "TED", "desc": "TEDTalks • TEDConferences", "logo": "https://logo.clearbit.com/ted.com"},
    {"name": "Figma", "desc": "Company • Design systems", "logo": "https://logo.clearbit.com/figma.com"},
    {"name": "Notion", "desc": "Company • Productivity", "logo": "https://logo.clearbit.com/notion.so"},
    {"name": "Stripe", "desc": "Company • Fintech", "logo": "https://logo.clearbit.com/stripe.com"},
]

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]

FIELD_OPERATORS_VIEW_USER_PROFILE_MAP = {
    "name": STRING_OPERATORS,
}

FIELD_OPERATORS_CONNECT_WITH_USER_MAP = {
    "target_username": STRING_OPERATORS,
    "target_name": STRING_OPERATORS,
}

FIELD_OPERATORS_LIKE_POST_MAP = {
    "poster_name": STRING_OPERATORS,
    "poster_content": STRING_OPERATORS,
}

FIELD_OPERATORS_COMMENT_ON_POST_MAP = {
    "comment_text": STRING_OPERATORS,
    "poster_name": STRING_OPERATORS,
    "poster_content": STRING_OPERATORS,
}
FIELD_OPERATORS_POST_STATUS_MAP = {
    "content": STRING_OPERATORS,
}

FIELD_OPERATORS_SEARCH_USERS_MAP = {
    "query": STRING_OPERATORS,
}

FIELD_OPERATORS_FOLLOW_PAGE_MAP = {
    "company": STRING_OPERATORS,
}

FIELD_OPERATORS_UNFOLLOW_PAGE_MAP = {
    "company": STRING_OPERATORS,
}

FIELD_OPERATORS_VIEW_JOB_MAP = {
    "job_title": STRING_OPERATORS,
    "company": STRING_OPERATORS,
    "location": STRING_OPERATORS,
}

FIELD_OPERATORS_APPLY_FOR_JOB_MAP = {
    "job_title": STRING_OPERATORS,
    "company": STRING_OPERATORS,
    "location": STRING_OPERATORS,
}

FIELD_OPERATORS_SEARCH_JOBS_MAP = {
    "query": STRING_OPERATORS,
}

FIELD_OPERATORS_FILTER_JOBS_MAP = {
    "filters": [CONTAINS, NOT_CONTAINS, EQUALS],
    "result_count": LOGICAL_OPERATORS,
}
