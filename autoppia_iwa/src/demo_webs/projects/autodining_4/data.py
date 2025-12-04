from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

RESTAURANT_TIMES = ["12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM"]
RESTAURANT_PEOPLE_COUNTS = [1, 2, 3, 4, 5, 6, 7, 8]
RESTAURANT_COUNTRIES = [
    {"code": "AR", "name": "Argentina"},
    {"code": "AU", "name": "Australia"},
    {"code": "BD", "name": "Bangladesh"},
    {"code": "BR", "name": "Brazil"},
    {"code": "CA", "name": "Canada"},
    {"code": "CN", "name": "China"},
    {"code": "EG", "name": "Egypt"},
    {"code": "FR", "name": "France"},
    {"code": "DE", "name": "Germany"},
    {"code": "IN", "name": "India"},
    {"code": "ID", "name": "Indonesia"},
    {"code": "IT", "name": "Italy"},
    {"code": "JP", "name": "Japan"},
    {"code": "MX", "name": "Mexico"},
    {"code": "MY", "name": "Malaysia"},
    {"code": "NG", "name": "Nigeria"},
    {"code": "NL", "name": "Netherlands"},
    {"code": "PK", "name": "Pakistan"},
    {"code": "PH", "name": "Philippines"},
    {"code": "PL", "name": "Poland"},
    {"code": "RU", "name": "Russia"},
    {"code": "SA", "name": "Saudi Arabia"},
    {"code": "ZA", "name": "South Africa"},
    {"code": "KR", "name": "South Korea"},
    {"code": "ES", "name": "Spain"},
    {"code": "SE", "name": "Sweden"},
    {"code": "CH", "name": "Switzerland"},
    {"code": "TH", "name": "Thailand"},
    {"code": "TR", "name": "Turkey"},
    {"code": "AE", "name": "United Arab Emirates"},
    {"code": "GB", "name": "United Kingdom"},
    {"code": "US", "name": "United States"},
    {"code": "VN", "name": "Vietnam"},
]
RESTAURANT_OCCASIONS = ["birthday", "anniversary", "business", "other"]
SCROLL_DIRECTIONS = ["left", "right"]
SCROLL_SECTIONS_TITLES = ["Available for lunch now", "Introducing OpenDinning Icons", "Award Winners"]

CUISINE = ["Japanese", "Mexican", "American"]
NAMES = [
    "James",
    "William",
    "Benjamin",
    "Alexander",
    "Daniel",
    "Samuel",
    "Matthew",
    "Jonathan",
    "Christopher",
    "Andrew",
    "Olivia",
    "Emma",
    "Charlotte",
    "Amelia",
    "Sophia",
    "Grace",
    "Emily",
    "Hannah",
    "Abigail",
    "Madison",
]
SAMPLE_EMAILS = [
    "james.wilson@example.com",
    "emma.johnson@example.com",
    "liam.smith@example.com",
    "olivia.brown@example.com",
    "noah.jones@example.com",
    "ava.miller@example.com",
    "william.davis@example.com",
    "sophia.garcia@example.com",
    "benjamin.rodriguez@example.com",
    "mia.martinez@example.com",
    "lucas.harris@example.com",
    "charlotte.clark@example.com",
    "henry.lewis@example.com",
    "amelia.walker@example.com",
    "alexander.hall@example.com",
    "harper.allen@example.com",
    "michael.young@example.com",
    "ella.king@example.com",
    "daniel.wright@example.com",
    "grace.scott@example.com",
]
CONTACT_SUBJECTS = [
    "Inquiry About Your Services",
    "Request for More Information",
    "Feedback on Recent Experience",
    "Issue With My Account",
    "Need Assistance With Booking",
    "Suggestion for Improvement",
    "Request for Collaboration",
    "Question About Pricing",
    "Follow-up on Previous Conversation",
    "Concern About a Recent Order",
    "Request for Appointment",
    "New Business Inquiry",
    "Support Request",
    "Website Issue Report",
    "Subscription Inquiry",
    "Product Information Needed",
    "Billing and Payment Question",
    "Technical Issue Assistance",
    "Request for Demo",
    "General Inquiry",
]
CONTACT_MESSAGES = [
    "Hi, I would like to learn more about your services. Please share the details.",
    "Hello, I'm facing an issue with my account login. Can you help me resolve it?",
    "I am interested in booking an appointment. Please guide me through the process.",
    "I would like to collaborate with your team on an upcoming project.",
    "Can you provide more information about your pricing plans?",
    "I recently made an order and have a few concerns. Please assist.",
    "Your website seems to have a problem on the checkout page. Kindly check.",
    "I want to know if you offer any discounts or special packages.",
    "I have some feedback regarding your customer support experience.",
    "Could you please send me a demo of how your system works?",
    "I need help understanding the billing details for my last payment.",
    "I am unable to access certain features on my account. Please look into this.",
    "Can you share details about your recent updates or new features?",
    "Please assist me in updating my profile information.",
    "I want to subscribe to your newsletter. How can I do it?",
    "I am confused about a recent notification I received. Kindly clarify.",
    "Can you help me track the status of my order?",
    "I would like to cancel my previous request. Please confirm.",
    "I am reaching out to report a technical bug I encountered.",
    "Thank you for your services. I just wanted to share my appreciation.",
]

HELP_CATEGORIES = [
    "Reservations",
    "Payments",
    "Account",
    "Cancellations",
    "Feedback",
]

FAQ_QUESTIONS = [
    "How do I modify a reservation?",
    "Can I get a refund?",
    "How do I change my password?",
    "Is there a cancellation fee?",
    "How do I contact support?",
]

ABOUT_FEATURES = [
    "Curated chefs",
    "Live availability",
    "Trusted reviews",
]

CONTACT_CARD_TYPES = ["Email", "Phone", "Chat", "Office"]
OPERATORS_ALLOWED_DATE_DROPDOWN_OPENED = {
    "selected_date": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
}

OPERATORS_ALLOWED_TIME_DROPDOWN_OPENED = {
    "selected_time": [EQUALS],
}

OPERATORS_ALLOWED_PEOPLE_DROPDOWN_OPENED = {
    "people_count": [EQUALS, GREATER_EQUAL],
}

OPERATORS_ALLOWED_SEARCH_RESTAURANT = {
    "query": [EQUALS, CONTAINS],
}

OPERATORS_ALLOWED_FOR_RESTAURANT = {
    "name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "desc": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "rating": [EQUALS, NOT_EQUALS, GREATER_EQUAL, LESS_EQUAL, LESS_THAN, GREATER_THAN],
    "reviews": [EQUALS, NOT_EQUALS, GREATER_EQUAL, LESS_EQUAL, LESS_THAN, GREATER_THAN],
    "bookings": [EQUALS, NOT_EQUALS, GREATER_EQUAL, LESS_EQUAL, LESS_THAN, GREATER_THAN],
    "cuisine": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}


OPERATORS_ALLOWED_BOOK_RESTAURANT = {
    "people_count": [EQUALS, GREATER_EQUAL],
    "selected_date": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
    "selected_time": [EQUALS, NOT_EQUALS],
}

OPERATORS_ALLOWED_COUNTRY_SELECTED = {
    **OPERATORS_ALLOWED_BOOK_RESTAURANT,
    "country_name": [EQUALS, NOT_EQUALS],
    "country_code": [EQUALS, NOT_EQUALS],
}

OPERATORS_ALLOWED_OCCASION_SELECTED = {
    **OPERATORS_ALLOWED_BOOK_RESTAURANT,
    "occasion_type": [EQUALS, NOT_EQUALS],
}

OPERATORS_ALLOWED_RESERVATION_COMPLETE = {
    **OPERATORS_ALLOWED_OCCASION_SELECTED,
    "country_name": [EQUALS, NOT_EQUALS],
    "country_code": [EQUALS, NOT_EQUALS],
    "phone_number": [EQUALS],
}

OPERATORS_ALLOWED_SCROLL_VIEW = {
    "section_title": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "direction": [EQUALS, NOT_EQUALS],
}
OPERATORS_ALLOWED_CONTACT = {
    "username": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "email": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "message": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "subject": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

OPERATORS_ALLOWED_HELP_CATEGORY_SELECTED = {"category": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]}
OPERATORS_ALLOWED_HELP_FAQ_TOGGLED = {"question": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]}
OPERATORS_ALLOWED_ABOUT_FEATURE_CLICK = {"feature": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]}
OPERATORS_ALLOWED_CONTACT_CARD_CLICK = {"card_type": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]}
