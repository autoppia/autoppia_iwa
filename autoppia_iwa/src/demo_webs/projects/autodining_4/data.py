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

CUSINE = ["Japanese", "Mexican", "American"]
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
