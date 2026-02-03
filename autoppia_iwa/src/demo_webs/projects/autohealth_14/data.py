from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

EMERGENCY_CONTACT = [
    "Alice Johnson",
    "Bob Smith",
    "Charlie Davis",
    "Diana Miller",
    "Ethan Brown",
    "Fiona Wilson",
    "George Harris",
    "Hannah Clark",
    "Ian Lewis",
    "Julia Walker",
    "Kevin Hall",
    "Laura Young",
    "Michael Allen",
    "Natalie King",
    "Oliver Scott",
]
MODIFIED_EMERGENCY_CONTACT = [{"name": n} for n in EMERGENCY_CONTACT]

EMERGENCY_PHONE = [
    "+1-202-555-0101",
    "+1-202-555-0102",
    "+1-202-555-0103",
    "+1-202-555-0104",
    "+1-202-555-0105",
    "+1-202-555-0106",
    "+1-202-555-0107",
    "+1-202-555-0108",
    "+1-202-555-0109",
    "+1-202-555-0110",
    "+1-202-555-0111",
    "+1-202-555-0112",
    "+1-202-555-0113",
    "+1-202-555-0114",
    "+1-202-555-0115",
]
MODIFIED_EMERGENCY_PHONE = [{"phone": p} for p in EMERGENCY_PHONE]

INSURANCE_NUMBER = [
    "INS-1001-2025",
    "INS-1002-2025",
    "INS-1003-2025",
    "INS-1004-2025",
    "INS-1005-2025",
    "INS-1006-2025",
    "INS-1007-2025",
    "INS-1008-2025",
    "INS-1009-2025",
    "INS-1010-2025",
    "INS-1011-2025",
    "INS-1012-2025",
    "INS-1013-2025",
    "INS-1014-2025",
    "INS-1015-2025",
]

MODIFIED_INSURANCE_NUMBER = [{"number": n} for n in INSURANCE_NUMBER]

INSURANCE_PROVIDER = [
    "Allianz Insurance",
    "State Farm",
    "AXA Insurance",
    "Prudential Insurance",
    "MetLife",
    "Zurich Insurance",
    "Progressive",
    "AIG (American International Group)",
    "Liberty Mutual",
    "Cigna",
    "UnitedHealthcare",
    "Chubb Insurance",
    "Travelers Insurance",
    "Humana",
    "Blue Cross Blue Shield",
]

MODIFIED_INSURANCE_PROVIDER = [{"provider": p} for p in INSURANCE_PROVIDER]

NOTES = [
    "Please review my latest blood test results.",
    "I have been experiencing frequent headaches lately.",
    "Can I adjust the dosage of my current medication?",
    "I would like to schedule a follow-up appointment.",
    "Are there any dietary restrictions I should follow?",
    "I noticed side effects after starting the new medicine.",
    "Could you recommend exercises for better joint health?",
    "I need a medical certificate for my workplace.",
    "Please advise if I should continue this prescription.",
    "I would like a second opinion on my diagnosis.",
    "Can I get a vaccination update at my next visit?",
    "Should I be concerned about my recent weight loss?",
    "I have trouble sleeping, can you suggest remedies?",
    "Is it safe to combine my medication with supplements?",
    "I would like guidance on managing stress effectively.",
]
MODIFIED_NOTES = [{"note": n} for n in NOTES]

PATIENT_NAMES = [
    "John Smith",
    "Emily Johnson",
    "Michael Brown",
    "Sophia Davis",
    "Daniel Wilson",
    "Olivia Miller",
    "James Anderson",
    "Ava Thompson",
    "William Taylor",
    "Isabella Moore",
    "Benjamin Clark",
    "Charlotte Lewis",
    "Ethan Walker",
    "Amelia Hall",
    "Alexander Young",
]
MODIFIED_PATIENT_NAMES = [{"patient_name": p} for p in PATIENT_NAMES]

PATIENT_EMAILS = [
    "john.smith@example.com",
    "emily.johnson@example.com",
    "michael.brown@example.com",
    "sophia.davis@example.com",
    "daniel.wilson@example.com",
    "olivia.miller@example.com",
    "james.anderson@example.com",
    "ava.thompson@example.com",
    "william.taylor@example.com",
    "isabella.moore@example.com",
    "benjamin.clark@example.com",
    "charlotte.lewis@example.com",
    "ethan.walker@example.com",
    "amelia.hall@example.com",
    "alexander.young@example.com",
]
MODIFIED_PATIENT_EMAILS = [{"email": e} for e in PATIENT_EMAILS]

PATIENT_PHONES = [
    "+1-202-555-0141",
    "+1-202-555-0142",
    "+1-202-555-0143",
    "+1-202-555-0144",
    "+1-202-555-0145",
    "+1-202-555-0146",
    "+1-202-555-0147",
    "+1-202-555-0148",
    "+1-202-555-0149",
    "+1-202-555-0150",
    "+1-202-555-0151",
    "+1-202-555-0152",
    "+1-202-555-0153",
    "+1-202-555-0154",
    "+1-202-555-0155",
]
MODIFIED_PATIENT_PHONES = [{"contact": c} for c in PATIENT_PHONES]

REASON_FOR_VISIT = [
    "Annual health check-up",
    "Flu-like symptoms",
    "Routine blood pressure monitoring",
    "Diabetes follow-up",
    "Back pain consultation",
    "Allergy testing",
    "Skin rash evaluation",
    "Chronic migraine management",
    "Post-surgery follow-up",
    "Prescription refill",
    "Chest pain assessment",
    "Weight management consultation",
    "Arthritis treatment review",
    "Sleep disorder evaluation",
    "General fatigue and weakness",
]
MODIFIED_REASON_FOR_VISIT = [{"reason": r} for r in REASON_FOR_VISIT]


STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
LIST_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]

FIELD_OPERATORS_MAP_BOOK_APPOINTMENT = {
    "date": EQUALITY_OPERATORS,
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "time": [EQUALS],
}

FIELD_OPERATORS_MAP_OPEN_APPOINTMENT_FORM = {
    "date": EQUALITY_OPERATORS,
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "time": [EQUALS],
    "source": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_APPOINTMENT_BOOKED_SUCCESSFULLY = {
    "date": EQUALITY_OPERATORS,
    "doctor_name": STRING_OPERATORS,
    "time": [EQUALS],
    "speciality": STRING_OPERATORS,
    "emergency_contact": STRING_OPERATORS,
    "emergency_phone": EQUALITY_OPERATORS,
    "insurance_number": EQUALITY_OPERATORS,
    "insurance_provider": STRING_OPERATORS,
    "notes": STRING_OPERATORS,
    "patient_name": STRING_OPERATORS,
    "patient_email": STRING_OPERATORS,
    "patient_phone": EQUALITY_OPERATORS,
    "reason_for_visit": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_REQUEST_APPOINTMENT = {
    "patient_name": STRING_OPERATORS,
    "patient_email": STRING_OPERATORS,
    "patient_phone": EQUALITY_OPERATORS,
    "specialty": STRING_OPERATORS,
    "source": STRING_OPERATORS,
    "action": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_REQUEST_QUICK_APPOINTMENT = {
    "patient_name": STRING_OPERATORS,
    "patient_email": STRING_OPERATORS,
    "patient_phone": EQUALITY_OPERATORS,
    "specialty": STRING_OPERATORS,
    "source": STRING_OPERATORS,
    "action": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SEARCH_APPOINTMENT = {
    "filter_type": STRING_OPERATORS,
    "doctor_name": STRING_OPERATORS,
    "specialty": STRING_OPERATORS,
    "date": EQUALITY_OPERATORS,
    "source": STRING_OPERATORS,
    "action": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SEARCH_DOCTORS = {
    "search_term": STRING_OPERATORS,
    "specialty": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SEARCH_PRESCRIPTION = {
    "medicine_name": STRING_OPERATORS,
    "doctor_name": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_PRESCRIPTION = {
    "doctor_name": STRING_OPERATORS,
    "dosage": STRING_OPERATORS,
    "medicine_name": STRING_OPERATORS,
    "start_date": EQUALITY_OPERATORS,
    "category": STRING_OPERATORS,
    "status": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_REFILL_PRESCRIPTION = {
    "medicine_name": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_SEARCH_MEDICAL_ANALYSIS = {
    "record_title": STRING_OPERATORS,
    "doctor_name": STRING_OPERATORS,
    "source": STRING_OPERATORS,
    "action": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_MEDICAL_ANALYSIS = {
    "record_title": STRING_OPERATORS,
    "record_type": STRING_OPERATORS,
    "record_date": EQUALITY_OPERATORS,
    "doctor_name": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE = {
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "rating": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_DOCTOR_EDUCATION = {
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "source": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_OPEN_CONTACT_DOCTOR_FORM = {
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "rating": LOGICAL_OPERATORS,
    "source": STRING_OPERATORS,
}

FIELD_OPERATORS_MAP_CONTACT_DOCTOR = {**FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE}

FIELD_MAP_CONTACT_DOCTOR_SUCCESSFULLY = {
    "doctor_name": STRING_OPERATORS,
    "message": STRING_OPERATORS,
    "patient_email": STRING_OPERATORS,
    "patient_phone": EQUALITY_OPERATORS,
    "patient_name": STRING_OPERATORS,
    "preferred_contact_method": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "subject": STRING_OPERATORS,
    "urgency": STRING_OPERATORS,
    "appointment_request": EQUALITY_OPERATORS,
}

FIELD_OPERATORS_MAP_VIEW_REVIEW_CLICKED = {
    **FIELD_OPERATORS_MAP_VIEW_DOCTOR_PROFILE,
}

FIELD_OPERATORS_MAP_FILTER_DOCTOR_REVIEWS = {
    "doctor_name": STRING_OPERATORS,
    "speciality": STRING_OPERATORS,
    "filter_rating": LOGICAL_OPERATORS,
    "sort_order": STRING_OPERATORS,
}
