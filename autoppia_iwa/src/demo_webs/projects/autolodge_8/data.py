from typing import Any

from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST
from ..shared_utils import parse_datetime

# ============================================================================
# DATA TRANSFORMATION HELPERS
# ============================================================================
def _process_string_value(k: str, v: str) -> Any:
    """Process string value, parsing datetime if needed."""
    if k in ["datesFrom", "datesTo"]:
        return parse_datetime(v)
    return v


def _process_dict_value(k: str, v: dict) -> dict[str, Any]:
    """Process dict value by flattening keys with prefix."""
    return {k + "_" + nk: nv for nk, nv in v.items()}


def _process_list_value(k: str, v: list) -> list[str] | None:
    """Process list value, extracting titles from amenities."""
    if k == "amenities":
        return [sv["title"] for sv in v if sv.get("title")]
    return None


def _transform_hotel_data(hotel: dict) -> dict[str, Any]:
    """Transform a single hotel dictionary by processing each field."""
    new_dict = {}
    for k, v in hotel.items():
        if isinstance(v, str):
            new_dict[k] = _process_string_value(k, v)
        elif isinstance(v, dict):
            new_dict.update(_process_dict_value(k, v))
        elif isinstance(v, list):
            processed = _process_list_value(k, v)
            if processed is not None:
                new_dict[k] = processed
        else:
            new_dict[k] = v
    return new_dict


# ============================================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================================
def get_modify_data(hotels_data=None):
    """Transform hotels data by processing nested structures and parsing dates."""
    if not hotels_data:
        return []
    return [_transform_hotel_data(hotel) for hotel in hotels_data]


LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
ARRAY_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]

FIELD_OPERATORS_FILTER_HOTELS_MAP = {
    "rating": LOGICAL_OPERATORS,
    "price": LOGICAL_OPERATORS,
    "region": STRING_OPERATORS,
    "results": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_APPLY_FILTERS_MAP = FIELD_OPERATORS_FILTER_HOTELS_MAP

FIELD_OPERATORS_SUBMIT_REVIEW_MAP = {
    "rating": LOGICAL_OPERATORS,
    "comment": STRING_OPERATORS,
    "name": STRING_OPERATORS,
}
FIELD_OPERATORS_SUBMIT_REVIEW_ALIAS_MAP = FIELD_OPERATORS_SUBMIT_REVIEW_MAP

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

FIELD_OPERATORS_EDIT_GUESTS_MAP = {
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
FIELD_OPERATORS_PAYMENT_METHOD_SELECTED_MAP = {
    "method": STRING_OPERATORS,
    "hotel_id": LOGICAL_OPERATORS,
    "title": STRING_OPERATORS,
}

FIELD_OPERATORS_MESSAGE_HOST_MAP = {
    **FIELD_OPERATORS_VIEW_HOTEL_MAP,
    "message": STRING_OPERATORS,
    "host_name": STRING_OPERATORS,
    # "source": STRING_OPERATORS,
}

FIELD_OPERATORS_SHARE_HOTEL_MAP = {**FIELD_OPERATORS_VIEW_HOTEL_MAP, "email": STRING_OPERATORS}

FIELD_OPERATORS_BACK_TO_ALL_HOTELS_MAP = {**FIELD_OPERATORS_VIEW_HOTEL_MAP}

FIELD_OPERATORS_WISHLIST_OPENED_MAP = {"count": LOGICAL_OPERATORS}
FIELD_OPERATORS_BOOK_FROM_WISHLIST_MAP = {"hotel_id": LOGICAL_OPERATORS, "title": STRING_OPERATORS}
FIELD_OPERATORS_FAQ_OPENED_MAP = {"question": STRING_OPERATORS}
