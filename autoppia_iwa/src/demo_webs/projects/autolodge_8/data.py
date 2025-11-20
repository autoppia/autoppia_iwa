from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST
from ..shared_utils import parse_datetime


def get_modify_data(hotels_data=None):
    if not hotels_data:
        return []
    modified_data = []
    for hotel in hotels_data:
        new_dict = {}
        for k, v in hotel.items():
            if isinstance(v, str):
                if k in ["datesFrom", "datesTo"]:
                    new_dict[k] = parse_datetime(v)
                else:
                    new_dict[k] = v
            elif isinstance(v, dict):
                for nk, nv in v.items():
                    new_dict[k + "_" + nk] = nv
            elif isinstance(v, list):
                if k == "amenities":
                    new_dict["amenities"] = [sv["title"] for sv in v if sv.get("title")]
            else:
                new_dict[k] = v

        modified_data.append(new_dict)
    return modified_data


LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
ARRAY_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]

FIELD_OPERATORS_SEARCH_HOTEL_MAP = {
    "search_term": STRING_OPERATORS,
    "adults": LOGICAL_OPERATORS,
    "children": LOGICAL_OPERATORS,
    "infants": LOGICAL_OPERATORS,
    "pets": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_VIEW_HOTEL_MAP = {
    "title": STRING_OPERATORS,
    "location": STRING_OPERATORS,
    "rating": LOGICAL_OPERATORS,
    "price": LOGICAL_OPERATORS,
    "reviews": LOGICAL_OPERATORS,
    "guests": LOGICAL_OPERATORS,
    "host_name": STRING_OPERATORS,
    "amenities": ARRAY_OPERATORS,
}

FIELD_OPERATORS_INCREASE_GUESTS_MAP = {
    # "from_guests": [EQUALS, GREATER_EQUAL, GREATER_THAN],
    "guests_to": [EQUALS, LESS_EQUAL, LESS_THAN],
    **{k: v for k, v in FIELD_OPERATORS_VIEW_HOTEL_MAP.items() if k != "guests"},
}

FIELD_OPERATORS_RESERVE_HOTEL_MAP = {
    **{k: v for k, v in FIELD_OPERATORS_VIEW_HOTEL_MAP.items() if k != "guests"},
    "guests_set": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP = {
    **FIELD_OPERATORS_RESERVE_HOTEL_MAP,
    "checkin": LOGICAL_OPERATORS,
    "checkout": LOGICAL_OPERATORS,
}

FIELD_OPERATORS_CONFIRM_AND_PAY_MAP = {
    **FIELD_OPERATORS_RESERVE_HOTEL_MAP,
    # "nights": LOGICAL_OPERATORS,  # int
    # "priceSubtotal": LOGICAL_OPERATORS,  # int
    # "total": LOGICAL_OPERATORS,  # int
    "card_number": [EQUALS, NOT_EQUALS],
    "expiration": [EQUALS, NOT_EQUALS],
    "cvv": [EQUALS, NOT_EQUALS],
    "zipcode": [EQUALS, NOT_EQUALS],
    "country": [EQUALS, NOT_EQUALS],
}

FIELD_OPERATORS_MESSAGE_HOST_MAP = {
    **FIELD_OPERATORS_VIEW_HOTEL_MAP,
    "message": STRING_OPERATORS,
    "host_name": STRING_OPERATORS,
    # "source": STRING_OPERATORS,
}

FIELD_OPERATORS_SHARE_HOTEL_MAP = {**FIELD_OPERATORS_VIEW_HOTEL_MAP, "email": STRING_OPERATORS}

FIELD_OPERATORS_BACK_TO_ALL_HOTELS_MAP = {**FIELD_OPERATORS_VIEW_HOTEL_MAP}
