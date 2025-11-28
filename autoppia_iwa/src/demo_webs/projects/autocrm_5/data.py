from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

NEW_LOGS_DATA = [
    {"matter": "Estate Planning", "description": "Consultation", "hours": 2},
    {"matter": "IP Filing", "description": "Draft application", "hours": 1.5},
    {"matter": "M&A Advice", "description": "Negotiation call", "hours": 3},
    {"matter": "Trademark Filing", "description": "Prepare documents", "hours": 2.5},
    {"matter": "NDA Review", "description": "Review clauses", "hours": 1.2},
    {"matter": "Shareholder Dispute", "description": "Strategy meeting", "hours": 4},
    {"matter": "Franchise Agreement", "description": "Legal drafting", "hours": 2.7},
    {"matter": "Employment Contract", "description": "HR consultation", "hours": 1},
    {"matter": "Investor Due Diligence", "description": "Risk assessment", "hours": 3.3},
    {"matter": "Corporate Compliance", "description": "Documentation check", "hours": 2.1},
    {"matter": "Patent Filing", "description": "Patent search", "hours": 2},
    {"matter": "Business Sale", "description": "Contract review", "hours": 5},
    {"matter": "Internal Audit", "description": "Financial review", "hours": 3.5},
    {"matter": "Trademark Renewal", "description": "Online filing", "hours": 0.8},
    {"matter": "Merger Strategy", "description": "Planning call", "hours": 4.2},
    {"matter": "Copyright Dispute", "description": "Case analysis", "hours": 2.9},
    {"matter": "IP Agreement", "description": "Client call", "hours": 1.1},
    {"matter": "SaaS Contract", "description": "Contract draft", "hours": 2.6},
    {"matter": "Annual Return Filing", "description": "Compliance filing", "hours": 3.4},
    {"matter": "Legal Memo", "description": "Drafting memo", "hours": 1.8},
    {"matter": "Founder Agreement", "description": "Review terms", "hours": 2.7},
    {"matter": "Funding Round", "description": "Legal prep", "hours": 4.6},
    {"matter": "Property Lease", "description": "Lease review", "hours": 2.9},
    {"matter": "Board Meeting", "description": "Meeting notes", "hours": 1.3},
    {"matter": "Tax Advisory", "description": "Tax analysis", "hours": 2.5},
    {"matter": "Startup Incorporation", "description": "Setup docs", "hours": 3.7},
    {"matter": "Product Licensing", "description": "Review contract", "hours": 2.2},
    {"matter": "Compliance Review", "description": "Checklist audit", "hours": 1.9},
    {"matter": "Trademark Filing", "description": "Filing form", "hours": 0.9},
    {"matter": "Business Valuation", "description": "Valuation call", "hours": 4.5},
    {"matter": "Policy Drafting", "description": "Drafting policy", "hours": 3.2},
    {"matter": "Court Filing", "description": "File case", "hours": 2.8},
    {"matter": "Contract Dispute", "description": "Client discussion", "hours": 1.4},
    {"matter": "Risk Assessment", "description": "Review & report", "hours": 3},
    {"matter": "Startup Pitch Deck", "description": "Legal feedback", "hours": 2.3},
    {"matter": "Non-Compete Review", "description": "Review & advise", "hours": 1.7},
]

CALENDAR_DATA = [
    {
        "id": 1,
        "date": "2025-05-06",
        "label": "Smith Matter: Signing",
        "time": "11:00am",
        "color": "forest",
    },
    {
        "id": 2,
        "date": "2025-05-07",
        "label": "Internal Review",
        "time": "2:30pm",
        "color": "indigo",
    },
    {
        "id": 3,
        "date": "2025-05-13",
        "label": "Court Filing",
        "time": "9:00am",
        "color": "blue",
    },
    {
        "id": 4,
        "date": "2025-05-18",
        "label": "Client Call - Jessica",
        "time": "2:00pm",
        "color": "forest",
    },
    {
        "id": 5,
        "date": "2025-05-18",
        "label": "M&A: Docs Due",
        "time": "5:00pm",
        "color": "indigo",
    },
    {
        "id": 6,
        "date": "2025-05-22",
        "label": "Staff Meeting",
        "time": "1:30pm",
        "color": "zinc",
    },
]
ALLOWED_EVENT_COLORS = [
    "Matter/Event",  # originally "forest"
    "Internal",  # originally "indigo"
    "Filing",  # originally "blue"
    "Other",  # originally "zinc"
]


# AutoCRM (Web 5)
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
ARRAY_OPERATORS = [EQUALS, NOT_EQUALS, IN_LIST, NOT_IN_LIST]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]


FIELD_OPERATORS_MAP_MATTER = {
    "name": STRING_OPERATORS,
    "client": STRING_OPERATORS,
    "status": EQUALITY_OPERATORS,
    "updated": ARRAY_OPERATORS,
}

FIELD_OPERATORS_MAP_CLIENT_VIEW_MATTER = {
    "name": STRING_OPERATORS,
    "email": EQUALITY_OPERATORS,
    "status": ARRAY_OPERATORS,
    "matters": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_MAP_CHANGE_USER_NAME = {
    "name": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_DOCUMENT = {
    "name": STRING_OPERATORS,
    "size": LOGICAL_OPERATORS,
    "version": EQUALITY_OPERATORS,
    # "updated": EQUALITY_OPERATORS,
    "status": ARRAY_OPERATORS,
}
FIELD_OPERATORS_MAP_CALENDAR = {
    "label": STRING_OPERATORS,
    "date": LOGICAL_OPERATORS,
    "time": LOGICAL_OPERATORS,
    "event_type": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_LOG = {
    "matter": STRING_OPERATORS,
    "client": STRING_OPERATORS,
    "hours": LOGICAL_OPERATORS,
    "status": ARRAY_OPERATORS,
}

FIELD_OPERATORS_MAP_NEW_LOG = {
    "matter": STRING_OPERATORS,
    "description": STRING_OPERATORS,
    "hours": [EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
}
