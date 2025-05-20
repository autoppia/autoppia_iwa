import datetime
import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import RESTAURANT_COUNTRIES, RESTAURANT_DATA as MOCK_RESTAURANTS_DATA, RESTAURANT_OCCASIONS, RESTAURANT_PEOPLE_COUNTS, RESTAURANT_TIMES, SCROLL_DIRECTIONS


def generate_mock_dates():
    """
    Generates a list of mock dates, including today's date and dates
    within a range of 7 days before and after today.
    """
    today = datetime.datetime.now(datetime.UTC)
    mock_dates_raw = []

    # Today's date (datetime)
    mock_dates_raw.append(today.replace(hour=19, minute=0, second=0, microsecond=0, tzinfo=datetime.UTC))

    # Dates within +/- 7 days (as date objects)
    for i in range(1, 8):
        # Date before today
        date_before = today - datetime.timedelta(days=i)
        mock_dates_raw.append(date_before.date())

        # Date after today
        date_after = today + datetime.timedelta(days=i)
        mock_dates_raw.append(date_after.date())

    return sorted(list(set(mock_dates_raw)))  # Remove duplicates and sort


def generate_mock_date_strings(dates: list):
    """
    Generates a list of date strings (e.g., "Jul 18") from the mock dates.
    Prioritizes 'date' objects over 'datetime' objects for strings.
    """
    date_strings = []
    for d in dates:
        if isinstance(d, datetime.date | datetime.datetime):
            date_strings.append(d.strftime("%b %d"))
    return sorted(list(set(date_strings)))


# --- MOCK DATA GENERATION ---
MOCK_DATES = generate_mock_dates()
MOCK_DATE_STRINGS = generate_mock_date_strings(MOCK_DATES)


MOCK_PEOPLE_COUNT_STRINGS = ["1 person", "2 people", "4 guests"]


MOCK_RESTAURANT_QUERIES = ["pizza", "mexican food", "nearby cafes"] + [r["name"] for r in MOCK_RESTAURANTS_DATA]
MOCK_RESTAURANT_ACTIONS = ["view_full_menu", "collapse_menu"]
MOCK_PHONE_NUMBERS = ["555-1234", "9876543210", "+1-202-555-0182"]
MOCK_SPECIAL_REQUESTS = ["window seat", "allergies: nuts", "quiet table"]

FIELD_OPERATORS_MAP_RESTAURANT_EVENTS = {
    # DateDropdownOpenedEvent
    "selected_date": [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL],
    # TimeDropdownOpenedEvent
    "selected_time": [ComparisonOperator.EQUALS],
    # PeopleDropdownOpenedEvent
    "people_count": [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL],
    # SearchRestaurantEvent
    "query": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    # ViewRestaurantEvent & others with restaurant identity
    "restaurant_id": [ComparisonOperator.EQUALS],
    "restaurant_name": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    # ViewFullMenuEvent, CollapseMenuEvent
    "action": [ComparisonOperator.EQUALS],
    "time": [ComparisonOperator.EQUALS],  # Note: distinct from selected_time
    # "selected_date" (date object) handled above, "people" handled by people_count
    # BookRestaurantEvent
    # uses "restaurant_id", "restaurant_name", "time", "selected_date" (date obj), "people" (int)
    "people": [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL],  # For integer people count
    # CountrySelectedEvent
    "country_code": [ComparisonOperator.EQUALS],
    "country_name": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    # OccasionSelectedEvent
    "occasion": [ComparisonOperator.EQUALS, ComparisonOperator.IN_LIST],
    # ReservationCompleteEvent
    "reservation_date_str": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    "reservation_time": [ComparisonOperator.EQUALS],
    "people_count_str": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    "phone_number": [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS],
    "special_request": [ComparisonOperator.CONTAINS, ComparisonOperator.EQUALS],
    # ScrollViewEvent
    "direction": [ComparisonOperator.EQUALS],
}


def _generate_value_for_field(field_name: str, operator: ComparisonOperator) -> Any:
    """
    Generates a mock value for a given field and operator, using the updated MOCK_RESTAURANTS_DATA.
    """
    if field_name == "selected_date":  # datetime object for DateDropdownOpenedEvent
        return random.choice(MOCK_DATES) if MOCK_DATES else datetime.datetime.now(datetime.UTC)
    elif field_name == "selected_time":  # string for TimeDropdownOpenedEvent
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people_count":  # int for PeopleDropdownOpenedEvent
        return random.choice(RESTAURANT_PEOPLE_COUNTS)
    elif field_name == "query":  # string for SearchRestaurantEvent
        return random.choice(MOCK_RESTAURANT_QUERIES)
    elif field_name == "restaurant_id":
        # Use the 'id' key from the new MOCK_RESTAURANTS_DATA structure
        return random.choice(MOCK_RESTAURANTS_DATA)["id"] if MOCK_RESTAURANTS_DATA else "r_default"
    elif field_name == "restaurant_name":
        return random.choice(MOCK_RESTAURANTS_DATA)["name"] if MOCK_RESTAURANTS_DATA else "Default Restaurant"
    elif field_name == "action":  # For ViewFullMenu, CollapseMenu
        return random.choice(MOCK_RESTAURANT_ACTIONS)
    elif field_name == "time":  # For ViewFullMenu, BookRestaurant (booking time)
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people":  # int for BookRestaurant, ViewFullMenu
        return random.choice(RESTAURANT_PEOPLE_COUNTS)
    # For CountrySelectedEvent
    elif field_name == "country_code":
        return random.choice(RESTAURANT_COUNTRIES)["code"] if RESTAURANT_COUNTRIES else "US"
    elif field_name == "country_name":
        return random.choice(RESTAURANT_COUNTRIES)["name"] if RESTAURANT_COUNTRIES else "United States"
    elif field_name == "occasion":  # For OccasionSelectedEvent
        return random.choice(RESTAURANT_OCCASIONS)
    # For ReservationCompleteEvent
    elif field_name == "reservation_date_str":
        return random.choice(MOCK_DATE_STRINGS)
    elif field_name == "reservation_time":  # Duplicates 'time', but context is reservation completion
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people_count_str":
        return random.choice(MOCK_PEOPLE_COUNT_STRINGS)
    elif field_name == "phone_number":
        return random.choice(MOCK_PHONE_NUMBERS)
    elif field_name == "special_request":
        return random.choice(MOCK_SPECIAL_REQUESTS)
    # For ScrollViewEvent
    elif field_name == "direction":
        return random.choice(SCROLL_DIRECTIONS)

    # Fallback for unhandled fields, though ideally all relevant fields are covered above
    print(f"Warning: No specific mock value generator for field '{field_name}'. Using default string.")
    return "mock_value"


# --- Generator Functions (remain the same, using the updated _generate_value_for_field) ---


def generate_date_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "selected_date"  # Field in DateDropdownOpenedEvent.ValidationCriteria

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(criteria_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(criteria_field, op)
        constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_time_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "selected_time"

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(criteria_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(criteria_field, op)
        constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_people_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "people_count"

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(criteria_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(criteria_field, op)
        constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_search_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "query"  # Field in SearchRestaurantEvent.ValidationCriteria

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(criteria_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(criteria_field, op)
        constraints_list.append(create_constraint_dict(criteria_field, op, value))
    else:  # Fallback if map is incomplete
        constraints_list.append(create_constraint_dict(criteria_field, ComparisonOperator.CONTAINS, "restaurant"))
    return constraints_list


def generate_view_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields in ViewRestaurantEvent.ValidationCriteria: restaurant_id, restaurant_name
    possible_fields = ["restaurant_id", "restaurant_name"]

    # Generate constraints for 1 or 2 fields
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field)
        if allowed_operators:
            op = random.choice(allowed_operators)
            value = _generate_value_for_field(field, op)
            constraints_list.append(create_constraint_dict(field, op, value))

    if not constraints_list:  # Fallback: ensure at least one constraint
        value = _generate_value_for_field("restaurant_name", ComparisonOperator.EQUALS)
        constraints_list.append(create_constraint_dict("restaurant_name", ComparisonOperator.EQUALS, value))
    return constraints_list


def generate_view_full_menu_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields in ViewFullMenuEvent.ValidationCriteria: restaurant_id, restaurant_name, action, time, selected_date, people
    possible_fields = ["restaurant_name", "selected_date", "time", "people", "action"]  # restaurant_id often implied by name

    num_constraints = random.randint(1, min(3, len(possible_fields)))  # Generate 1 to 3 constraints
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field)
        if allowed_operators:
            op = random.choice(allowed_operators)
            # Special handling for selected_date to ensure it's a date object
            if field == "selected_date":
                value = random.choice([d for d in MOCK_DATES if isinstance(d, datetime.date)]) if MOCK_DATES else datetime.date.today()
            else:
                value = _generate_value_for_field(field, op)
            constraints_list.append(create_constraint_dict(field, op, value))

    if not constraints_list:  # Fallback
        value = _generate_value_for_field("restaurant_name", ComparisonOperator.EQUALS)
        constraints_list.append(create_constraint_dict("restaurant_name", ComparisonOperator.EQUALS, value))
    return constraints_list


def generate_collapse_menu_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields in CollapseMenuEvent.ValidationCriteria: restaurant_id, restaurant_name, action
    possible_fields = ["restaurant_name", "action"]

    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field)
        if allowed_operators:
            op = random.choice(allowed_operators)
            value = _generate_value_for_field(field, op)
            # Ensure action is 'collapse_menu' if field is 'action' for this specific event
            if field == "action":
                value = "collapse_menu"
            constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


def generate_book_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields in BookRestaurantEvent.ValidationCriteria: restaurant_id, restaurant_name, time, selected_date, people
    possible_fields = ["restaurant_name", "selected_date", "time", "people"]

    num_constraints = random.randint(2, len(possible_fields))  # Typically need a few details for booking
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field)
        if allowed_operators:
            op = random.choice(allowed_operators)
            if field == "selected_date":  # Ensure it's a date object
                value = random.choice([d for d in MOCK_DATES if isinstance(d, datetime.date)]) if MOCK_DATES else datetime.date.today()
            else:
                value = _generate_value_for_field(field, op)
            constraints_list.append(create_constraint_dict(field, op, value))
    if not any(c["field"] == "restaurant_name" for c in constraints_list):  # Ensure restaurant name is included
        value = _generate_value_for_field("restaurant_name", ComparisonOperator.EQUALS)
        constraints_list.append(create_constraint_dict("restaurant_name", ComparisonOperator.EQUALS, value))
    return constraints_list


def generate_country_selected_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields: country_code, country_name
    field_to_generate = random.choice(["country_code", "country_name"])

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field_to_generate)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(field_to_generate, op)
        constraints_list.append(create_constraint_dict(field_to_generate, op, value))
    return constraints_list


def generate_occasion_selected_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "occasion"

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(criteria_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(criteria_field, op)
        constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_reservation_complete_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields: restaurant_id, reservation_date_str, reservation_time, people_count_str,
    # country_code, country_name, phone_number, occasion, special_request
    possible_fields = ["restaurant_id", "reservation_date_str", "reservation_time", "people_count_str", "occasion", "phone_number"]

    num_constraints = random.randint(2, min(4, len(possible_fields)))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field in selected_fields:
        allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(field)
        if allowed_operators:
            op = random.choice(allowed_operators)
            value = _generate_value_for_field(field, op)
            constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_scroll_view_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    selected_field = "direction"

    allowed_operators = FIELD_OPERATORS_MAP_RESTAURANT_EVENTS.get(selected_field)
    if allowed_operators:
        op = random.choice(allowed_operators)
        value = _generate_value_for_field(selected_field, op)
        constraints_list.append(create_constraint_dict(selected_field, op, value))
    return constraints_list
