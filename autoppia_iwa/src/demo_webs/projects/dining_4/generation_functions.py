import datetime
import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import (
    RESTAURANT_COUNTRIES,
    RESTAURANT_DATA,
    RESTAURANT_OCCASIONS,
    RESTAURANT_PEOPLE_COUNTS,
    RESTAURANT_TIMES,
    SCROLL_DIRECTIONS,
)


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
        # Convert date_before.date() (which is a date object) to a datetime object at midnight
        mock_dates_raw.append(datetime.datetime.combine(date_before.date(), datetime.time.min, tzinfo=datetime.UTC))

        # Date after today
        date_after = today + datetime.timedelta(days=i)
        # Convert date_after.date() (which is a date object) to a datetime object at midnight
        mock_dates_raw.append(datetime.datetime.combine(date_after.date(), datetime.time.min, tzinfo=datetime.UTC))

    # Remove duplicates and sort the list.
    return sorted(list(set(mock_dates_raw)))


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


MOCK_DATES = generate_mock_dates()
MOCK_DATE_STRINGS = generate_mock_date_strings(MOCK_DATES)
MOCK_PEOPLE_COUNT_STRINGS = ["1 person", "2 people", "4 guests"]
MOCK_RESTAURANT_QUERIES = ["pizza", "mexican food", "nearby cafes"] + [r["name"] for r in RESTAURANT_DATA]
MOCK_RESTAURANT_ACTIONS = ["view_full_menu", "collapse_menu"]
MOCK_PHONE_NUMBERS = ["555-1234", "9876543210", "+1-202-555-0182"]
MOCK_SPECIAL_REQUESTS = ["window seat", "allergies: nuts", "quiet table"]


def _generate_value_for_field(field_name: str) -> Any:
    """
    Generates a mock value for a given field and operator, using the updated RESTAURANT_DATA.
    """
    if field_name == "selected_date":  # datetime object for DateDropdownOpenedEvent
        return random.choice(MOCK_DATES) if MOCK_DATES else datetime.datetime.now(datetime.UTC)
    elif field_name == "selected_time":
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people_count":
        return random.choice(RESTAURANT_PEOPLE_COUNTS)
    elif field_name == "query":
        return random.choice(MOCK_RESTAURANT_QUERIES)
    elif field_name == "restaurant_id":
        return random.choice(RESTAURANT_DATA)["id"] if RESTAURANT_DATA else "r_default"
    elif field_name == "restaurant_name":
        return random.choice(RESTAURANT_DATA)["name"] if RESTAURANT_DATA else "Default Restaurant"
    elif field_name == "action":
        return random.choice(MOCK_RESTAURANT_ACTIONS)
    elif field_name == "time":
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people":
        return random.choice(RESTAURANT_PEOPLE_COUNTS)
    elif field_name == "country_code":
        return random.choice(RESTAURANT_COUNTRIES)["code"] if RESTAURANT_COUNTRIES else "US"
    elif field_name == "country_name":
        return random.choice(RESTAURANT_COUNTRIES)["name"] if RESTAURANT_COUNTRIES else "United States"
    elif field_name == "occasion":
        return random.choice(RESTAURANT_OCCASIONS)
    elif field_name == "reservation_date_str":
        return random.choice(MOCK_DATE_STRINGS)
    elif field_name == "reservation_time":
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people_count_str":
        return random.choice(MOCK_PEOPLE_COUNT_STRINGS)
    elif field_name == "phone_number":
        return random.choice(MOCK_PHONE_NUMBERS)
    elif field_name == "special_request":
        return random.choice(MOCK_SPECIAL_REQUESTS)
    elif field_name == "direction":
        return random.choice(SCROLL_DIRECTIONS)

    print(f"Warning: No specific mock value generator for field '{field_name}'. Using default string.")
    return "mock_value"


# --- Constraint Generators with Inline Operators ---


def generate_date_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "selected_date"
    allowed_operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(criteria_field)
    constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_time_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "selected_time"
    allowed_operators = [ComparisonOperator.EQUALS]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(criteria_field)
    constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_people_dropdown_opened_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "people_count"
    allowed_operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(criteria_field)
    constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_search_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "query"
    allowed_operators = [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(criteria_field)
    constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_view_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields in ViewRestaurantEvent.ValidationCriteria: restaurant_id, restaurant_name
    possible_fields = [("restaurant_id", [ComparisonOperator.EQUALS]), ("restaurant_name", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS])]

    # Generate constraints for 1 or 2 fields
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field, operators in selected_fields:
        op = random.choice(operators)
        value = _generate_value_for_field(field)
        constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_view_full_menu_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = [
        ("restaurant_name", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
        ("selected_date", [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]),
        ("time", [ComparisonOperator.EQUALS]),
        ("people", [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL]),
        ("action", [ComparisonOperator.EQUALS]),
    ]

    num_constraints = random.randint(1, min(3, len(possible_fields)))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field, operators in selected_fields:
        op = random.choice(operators)
        # Special handling for selected_date to ensure it's a date object
        value = (random.choice([d for d in MOCK_DATES if isinstance(d, datetime.date)]) if MOCK_DATES else datetime.date.today()) if field == "selected_date" else _generate_value_for_field(field)
        constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_collapse_menu_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = [
        ("restaurant_name", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
        ("action", [ComparisonOperator.EQUALS]),  # Always "collapse_menu"
    ]

    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field, operators in selected_fields:
        op = random.choice(operators)
        value = "collapse_menu" if field == "action" else _generate_value_for_field(field)
        constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_book_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = [
        ("restaurant_name", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
        ("selected_date", [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]),
        ("time", [ComparisonOperator.EQUALS]),
        ("people", [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL]),
    ]

    num_constraints = random.randint(2, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field, operators in selected_fields:
        op = random.choice(operators)
        value = random.choice([d for d in MOCK_DATES if isinstance(d, datetime.date)]) if MOCK_DATES else datetime.date.today() if field == "selected_date" else _generate_value_for_field(field)

        constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_country_selected_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Randomly choose between code or name
    field_to_generate = random.choice([("country_code", [ComparisonOperator.EQUALS]), ("country_name", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS])])

    field, operators = field_to_generate
    op = random.choice(operators)
    value = _generate_value_for_field(field)
    constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


def generate_occasion_selected_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    criteria_field = "occasion"
    allowed_operators = [ComparisonOperator.EQUALS, ComparisonOperator.IN_LIST]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(criteria_field)
    constraints_list.append(create_constraint_dict(criteria_field, op, value))
    return constraints_list


def generate_reservation_complete_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    possible_fields = [
        ("restaurant_id", [ComparisonOperator.EQUALS]),
        ("reservation_date_str", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
        ("reservation_time", [ComparisonOperator.EQUALS]),
        ("people_count_str", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
        ("occasion", [ComparisonOperator.EQUALS, ComparisonOperator.IN_LIST]),
        ("phone_number", [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]),
    ]

    num_constraints = random.randint(2, min(4, len(possible_fields)))
    selected_fields = random.sample(possible_fields, num_constraints)

    for field, operators in selected_fields:
        op = random.choice(operators)
        value = _generate_value_for_field(field)
        constraints_list.append(create_constraint_dict(field, op, value))

    return constraints_list


def generate_scroll_view_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    selected_field = "direction"
    allowed_operators = [ComparisonOperator.EQUALS]

    op = random.choice(allowed_operators)
    value = _generate_value_for_field(selected_field)
    constraints_list.append(create_constraint_dict(selected_field, op, value))
    return constraints_list
