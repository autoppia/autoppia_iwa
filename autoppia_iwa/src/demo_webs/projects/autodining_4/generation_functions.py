import datetime
import random
from random import choice
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..shared_utils import create_constraint_dict, generate_mock_date_strings, generate_mock_dates
from .data import (
    ABOUT_FEATURES,
    CONTACT_CARD_TYPES,
    CONTACT_MESSAGES,
    CONTACT_SUBJECTS,
    CUISINE,
    FAQ_QUESTIONS,
    HELP_CATEGORIES,
    NAMES,
    OPERATORS_ALLOWED_ABOUT_FEATURE_CLICK,
    OPERATORS_ALLOWED_BOOK_RESTAURANT,
    OPERATORS_ALLOWED_CONTACT,
    OPERATORS_ALLOWED_CONTACT_CARD_CLICK,
    OPERATORS_ALLOWED_COUNTRY_SELECTED,
    OPERATORS_ALLOWED_DATE_DROPDOWN_OPENED,
    OPERATORS_ALLOWED_FOR_RESTAURANT,
    OPERATORS_ALLOWED_HELP_CATEGORY_SELECTED,
    OPERATORS_ALLOWED_HELP_FAQ_TOGGLED,
    OPERATORS_ALLOWED_PEOPLE_DROPDOWN_OPENED,
    OPERATORS_ALLOWED_RESERVATION_COMPLETE,
    OPERATORS_ALLOWED_SCROLL_VIEW,
    OPERATORS_ALLOWED_SEARCH_RESTAURANT,
    OPERATORS_ALLOWED_TIME_DROPDOWN_OPENED,
    RESTAURANT_COUNTRIES,
    RESTAURANT_OCCASIONS,
    RESTAURANT_PEOPLE_COUNTS,
    RESTAURANT_TIMES,
    SAMPLE_EMAILS,
    SCROLL_DIRECTIONS,
    SCROLL_SECTIONS_TITLES,
)
from .data_utils import fetch_data

# ============================================================================
# CONSTANTS
# ============================================================================
MOCK_DATES = generate_mock_dates()
MOCK_DATE_STRINGS = generate_mock_date_strings(MOCK_DATES)
# MOCK_PEOPLE_COUNT_STRINGS = ["1 person", "2 people", "4 guests"]
# Base restaurant queries - will be extended with actual restaurant names when data is loaded
_BASE_RESTAURANT_QUERIES = ["pizza", "mexican food", "nearby cafes"]
MOCK_RESTAURANT_ACTIONS = ["view_full_menu", "collapse_menu"]
MOCK_PHONE_NUMBERS = ["555-1234", "9876543210", "+1-202-555-0182"]
MOCK_SPECIAL_REQUESTS = ["window seat", "allergies: nuts", "quiet table"]


# ============================================================================
# DATA FETCHING HELPERS
# ============================================================================
async def _get_restaurant_queries() -> list[str]:
    """Get restaurant queries including names from API data."""
    try:
        restaurant_data = await fetch_data(count=50)  # Get a reasonable sample
        restaurant_names = [r.get("name", "") for r in restaurant_data if r.get("name")]
        return _BASE_RESTAURANT_QUERIES + restaurant_names
    except Exception:
        # Fallback to base queries if API fails
        return _BASE_RESTAURANT_QUERIES


# ============================================================================
# CONSTRAINT VALUE GENERATION HELPERS
# ============================================================================
def _normalize_field_name(field: str) -> str:
    """Normalize field name variations."""
    if field in ("name", "restaurant_name"):
        return "name"
    return field


def _get_special_field_list(field: str) -> list[str] | None:
    """Get list for special fields that use predefined constants."""
    field_mapping = {
        "direction": SCROLL_DIRECTIONS,
        "section": SCROLL_SECTIONS_TITLES,
        "time": RESTAURANT_TIMES,
        "people": RESTAURANT_PEOPLE_COUNTS,
        "occasion": RESTAURANT_OCCASIONS,
        "username": NAMES,
        "message": CONTACT_MESSAGES,
        "subject": CONTACT_SUBJECTS,
        "email": SAMPLE_EMAILS,
    }
    return field_mapping.get(field)


def _get_country_field_value(field: str, field_value: Any) -> Any:
    """Get country field value (name or code)."""
    if field == "country":
        valid = [v["name"] for v in RESTAURANT_COUNTRIES if v["name"] != field_value]
        return random.choice(valid) if valid else None
    if field == "code":
        valid = [v["code"] for v in RESTAURANT_COUNTRIES if v["code"] != field_value]
        return random.choice(valid) if valid else None
    return None


def _handle_not_equals_special_field(field: str, field_value: Any) -> Any:
    """Handle NOT_EQUALS operator for special fields."""
    special_list = _get_special_field_list(field)
    if special_list:
        valid = [v for v in special_list if v != field_value]
        return random.choice(valid) if valid else None
    country_value = _get_country_field_value(field, field_value)
    if country_value is not None:
        return country_value
    return None


def _handle_not_equals_generic(field: str, field_value: Any, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for generic fields."""
    valid = [v[field] for v in dataset if v.get(field) != field_value]
    return random.choice(valid) if valid else None


def _handle_not_equals_operator(field: str, field_value: Any, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator."""
    special_result = _handle_not_equals_special_field(field, field_value)
    if special_result is not None:
        return special_result
    return _handle_not_equals_generic(field, field_value, dataset)


def _handle_contains_special_field(field: str, field_value: str) -> Any:
    """Handle CONTAINS operator for special fields."""
    if field in ("direction", "section"):
        special_list = _get_special_field_list(field)
        if special_list:
            valid = [v for v in special_list if v != field_value]
            return random.choice(valid) if valid else None
    return None


def _handle_contains_string(field_value: str) -> str:
    """Handle CONTAINS operator for strings."""
    if len(field_value) > 2:
        start = random.randint(0, max(0, len(field_value) - 2))
        end = random.randint(start + 1, len(field_value))
        return field_value[start:end]
    return field_value


def _handle_contains_operator(field: str, field_value: str) -> Any:
    """Handle CONTAINS operator."""
    special_result = _handle_contains_special_field(field, field_value)
    if special_result is not None:
        return special_result
    return _handle_contains_string(field_value)


def _handle_not_contains_special_field(field: str, field_value: str) -> Any:
    """Handle NOT_CONTAINS operator for special fields."""
    special_list = _get_special_field_list(field)
    if special_list:
        valid = [v for v in special_list if v != field_value]
        return random.choice(valid) if valid else None
    return None


def _handle_not_contains_generic(field: str, field_value: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_CONTAINS operator for generic fields."""
    valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
    return random.choice(valid) if valid else None


def _handle_not_contains_operator(field: str, field_value: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_CONTAINS operator."""
    special_result = _handle_not_contains_special_field(field, field_value)
    if special_result is not None:
        return special_result
    return _handle_not_contains_generic(field, field_value, dataset)


def _handle_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle IN_LIST operator."""
    all_values = list({v.get(field) for v in dataset if field in v})
    if not all_values:
        return [field_value]
    subset = random.sample(all_values, min(2, len(all_values)))
    if field_value not in subset:
        subset.append(field_value)
    return list(set(subset))


def _handle_not_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle NOT_IN_LIST operator."""
    all_values = list({v.get(field) for v in dataset if field in v})
    if field_value in all_values:
        all_values.remove(field_value)
    return random.sample(all_values, min(2, len(all_values))) if all_values else []


def _handle_datetime_comparison(operator: ComparisonOperator, base: datetime.datetime) -> datetime.datetime:
    """Handle numeric comparison operators for datetime."""
    delta = datetime.timedelta(days=random.randint(1, 5))
    if operator == ComparisonOperator.GREATER_THAN:
        return base - delta
    if operator == ComparisonOperator.LESS_THAN:
        return base + delta
    return base


def _handle_numeric_comparison(operator: ComparisonOperator, base: int | float) -> float:
    """Handle numeric comparison operators for numbers."""
    delta = random.uniform(1, 3)
    if operator == ComparisonOperator.GREATER_THAN:
        return round(base - delta, 2)
    if operator == ComparisonOperator.LESS_THAN:
        return round(base + delta, 2)
    return round(base, 2)


def _handle_numeric_operators(operator: ComparisonOperator, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle numeric comparison operators."""
    numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float | datetime.datetime)]
    if not numeric_values:
        return None
    base = random.choice(numeric_values)
    if isinstance(base, datetime.datetime):
        return _handle_datetime_comparison(operator, base)
    return _handle_numeric_comparison(operator, base)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]] | dict[str, list[dict[str, Any]]] | list[str]) -> Any:
    # Extract restaurant list if dataset is a dict, otherwise use dataset as-is
    dataset = dataset["restaurants"] if isinstance(dataset, dict) and "restaurants" in dataset else dataset

    field = _normalize_field_name(field)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    if field == "rating":
        return random.choice([2, 3])

    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(field, field_value, dataset)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        return _handle_contains_operator(field, field_value)

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return _handle_not_contains_operator(field, field_value, dataset)

    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(field_value, field, dataset)

    if operator == ComparisonOperator.NOT_IN_LIST:
        return _handle_not_in_list_operator(field_value, field, dataset)

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        return _handle_numeric_operators(operator, field, dataset)

    return field_value


# ============================================================================
# FIELD VALUE GENERATION HELPERS
# ============================================================================
def _get_date_field_value() -> datetime.datetime:
    """Get value for date fields."""
    return random.choice(MOCK_DATES) if MOCK_DATES else datetime.datetime.now(datetime.UTC)


def _get_time_field_value() -> str:
    """Get value for time fields."""
    return random.choice(RESTAURANT_TIMES)


def _get_people_field_value() -> str:
    """Get value for people fields."""
    return random.choice(RESTAURANT_PEOPLE_COUNTS)


async def _get_query_field_value() -> str:
    """Get value for query fields."""
    possible_queries = await _get_restaurant_queries()
    return random.choice(possible_queries) if possible_queries else "pizza"


async def _get_name_field_value() -> str:
    """Get value for name/restaurant_name fields."""
    restaurant_data = await fetch_data()
    if restaurant_data:
        return random.choice(restaurant_data).get("name", "Default Restaurant")
    return "Default Restaurant"


def _get_country_code_value() -> str:
    """Get value for country code fields."""
    return random.choice(RESTAURANT_COUNTRIES)["code"] if RESTAURANT_COUNTRIES else "US"


def _get_country_name_value() -> str:
    """Get value for country name fields."""
    return random.choice(RESTAURANT_COUNTRIES)["name"] if RESTAURANT_COUNTRIES else "United States"


def _get_field_value_mapping() -> dict[str, Any]:
    """Get mapping of field names to their value generators (synchronous)."""
    return {
        "action": lambda: random.choice(MOCK_RESTAURANT_ACTIONS),
        "occasion": lambda: random.choice(RESTAURANT_OCCASIONS),
        "reservation": lambda: random.choice(MOCK_DATE_STRINGS),
        "phone": lambda: random.choice(MOCK_PHONE_NUMBERS),
        "request": lambda: random.choice(MOCK_SPECIAL_REQUESTS),
        "feature": lambda: random.choice(ABOUT_FEATURES),
        "category": lambda: random.choice(HELP_CATEGORIES),
        "question": lambda: random.choice(FAQ_QUESTIONS),
        "card_type": lambda: random.choice(CONTACT_CARD_TYPES),
        "direction": lambda: random.choice(SCROLL_DIRECTIONS),
        "section": lambda: random.choice(SCROLL_SECTIONS_TITLES),
        "desc": lambda: "Enjoy a delightful experience at",
        "cuisine": lambda: random.choice(CUISINE),
        "rating": lambda: random.choice([2, 3, 4]),
        "username": lambda: random.choice(NAMES),
        "email": lambda: random.choice(SAMPLE_EMAILS),
        "message": lambda: random.choice(CONTACT_MESSAGES),
        "subject": lambda: random.choice(CONTACT_SUBJECTS),
    }


async def _generate_value_for_field(field_name: str) -> Any:
    # Date fields
    if field_name in ("date", "selected_date"):
        return _get_date_field_value()

    # Time fields
    if field_name in ("time", "selected_time", "reservation_time"):
        return _get_time_field_value()

    # People fields
    if field_name in ("people", "people_count"):
        return _get_people_field_value()

    # Query field
    if field_name == "query":
        return await _get_query_field_value()

    # Name fields
    if field_name in ("name", "restaurant_name"):
        return await _get_name_field_value()

    # Country code fields
    if field_name in ("code", "country_code"):
        return _get_country_code_value()

    # Country name fields
    if field_name in ("country", "country_name"):
        return _get_country_name_value()

    # Reservation date string
    if field_name == "reservation_date_str":
        return random.choice(MOCK_DATE_STRINGS)

    # Special request
    if field_name == "special_request":
        return random.choice(MOCK_SPECIAL_REQUESTS)

    # Section title
    if field_name == "section_title":
        return random.choice(SCROLL_SECTIONS_TITLES)

    # Occasion type
    if field_name == "occasion_type":
        return random.choice(RESTAURANT_OCCASIONS)

    # Phone number
    if field_name == "phone_number":
        return random.choice(MOCK_PHONE_NUMBERS)

    # Try synchronous field mapping
    field_mapping = _get_field_value_mapping()
    if field_name in field_mapping:
        return field_mapping[field_name]()

    print(f"Warning: No specific mock value generator for field '{field_name}'. Using default string.")
    return "mock_value"


# ============================================================================
# RESTAURANT CONSTRAINTS
# ============================================================================
async def generate_view_restaurant_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=4,
        dataset=restaurants,
    )


async def generate_view_full_menu_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=4,
        dataset=restaurants,
    )


async def generate_collapse_menu_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=4,
        dataset=restaurants,
    )


async def generate_search_restaurant_constraints():
    return await generate_constraints_for_single_field("query", OPERATORS_ALLOWED_SEARCH_RESTAURANT)


async def generate_constraints_for_single_field(field: str, allowed_operators: dict[str, list[str]]) -> list[dict[str, Any]]:
    op = ComparisonOperator(random.choice(allowed_operators[field]))
    value = await _generate_value_for_field(field)
    # if field == 'selected_date' and isinstance(value, datetime.datetime):
    #     value = value.date().isoformat()
    if isinstance(value, datetime.datetime):
        value = value.isoformat()
    return [create_constraint_dict(field, op, value)]


# ============================================================================
# BOOKING CONSTRAINTS
# ============================================================================
async def generate_date_dropdown_opened_constraints():
    return await generate_constraints_for_single_field("date", OPERATORS_ALLOWED_DATE_DROPDOWN_OPENED)


async def generate_time_dropdown_opened_constraints():
    return await generate_constraints_for_single_field("time", OPERATORS_ALLOWED_TIME_DROPDOWN_OPENED)


async def generate_people_dropdown_opened_constraints():
    return await generate_constraints_for_single_field("people", OPERATORS_ALLOWED_PEOPLE_DROPDOWN_OPENED)


async def generate_book_restaurant_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=3,
        dataset=restaurants,
    )
    booking_constraints = await _generate_constraints_for_fields(
        all_fields=["people", "date", "time"],
        allowed_ops=OPERATORS_ALLOWED_BOOK_RESTAURANT,
        required_fields=["people", "date", "time"],
        validate_dates=True,
        dataset=restaurants,
    )
    all_constraints = restaurant_constraints + booking_constraints
    return all_constraints


async def generate_country_selected_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=3,
        dataset=restaurants,
    )
    country_field = random.choice(["country", "code"])
    booking_contraints = await _generate_constraints_for_fields(
        all_fields=["people", "date", "time"],
        allowed_ops=OPERATORS_ALLOWED_COUNTRY_SELECTED,
        required_fields=[country_field],
        validate_dates=True,
        dataset=restaurants,
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


async def generate_occasion_selected_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=3,
        dataset=restaurants,
    )
    booking_contraints = await _generate_constraints_for_fields(
        all_fields=["people", "date", "time"],
        allowed_ops=OPERATORS_ALLOWED_COUNTRY_SELECTED,
        required_fields=["occasion"],
        validate_dates=True,
        dataset=restaurants,
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


async def generate_reservation_complete_constraints(task_url: str | None = None, dataset: list[dict] | None = None):
    if not dataset:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
    else:
        restaurants = dataset
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"],
        allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT,
        max_constraints=3,
        dataset=restaurants,
    )
    booking_contraints = await _generate_constraints_for_fields(
        all_fields=["people", "code", "phone", "occasion", "date", "time"],
        allowed_ops=OPERATORS_ALLOWED_RESERVATION_COMPLETE,
        required_fields=["occasion"],
        validate_dates=True,
        max_optional=3,
        dataset=restaurants,
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


# ============================================================================
# SCROLL CONSTRAINTS
# ============================================================================
async def generate_scroll_view_constraints():
    return await _generate_constraints_for_fields(all_fields=["section", "direction"], allowed_ops=OPERATORS_ALLOWED_SCROLL_VIEW, required_fields=["section", "direction"])


# ============================================================================
# CONTACT CONSTRAINTS
# ============================================================================
async def generate_contact_constraints():
    constraint_list = []
    possible_fields = list(OPERATORS_ALLOWED_CONTACT.keys())
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    for field in selected_fields:
        allowed_ops = OPERATORS_ALLOWED_CONTACT.get(field, "")
        if not allowed_ops:
            continue

        op = ComparisonOperator(choice(allowed_ops))
        value = None
        if field == "username":
            default_value = await _generate_value_for_field(field)
            value = _generate_constraint_value(op, default_value, field, NAMES)
        if field == "message":
            default_value = await _generate_value_for_field(field)
            value = _generate_constraint_value(op, default_value, field, CONTACT_MESSAGES)
        if field == "email":
            default_value = await _generate_value_for_field(field)
            value = _generate_constraint_value(op, default_value, field, SAMPLE_EMAILS)
        if field == "subject":
            default_value = await _generate_value_for_field(field)
            value = _generate_constraint_value(op, default_value, field, CONTACT_SUBJECTS)

        if value is not None:
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        else:
            return []

    return constraint_list


# ============================================================================
# HELP CONSTRAINTS
# ============================================================================
async def generate_about_feature_click_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field = "feature"
    operators = OPERATORS_ALLOWED_ABOUT_FEATURE_CLICK.get(field, [])
    if not operators:
        return constraints_list
    op = ComparisonOperator(random.choice(operators))
    value = await _generate_value_for_field(field)
    constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


async def generate_help_category_selected_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field = "category"
    operators = OPERATORS_ALLOWED_HELP_CATEGORY_SELECTED.get(field, [])
    if not operators:
        return constraints_list
    op = ComparisonOperator(random.choice(operators))
    value = await _generate_value_for_field(field)
    constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


async def generate_help_faq_toggled_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field = "question"
    operators = OPERATORS_ALLOWED_HELP_FAQ_TOGGLED.get(field, [])
    if not operators:
        return constraints_list
    op = ComparisonOperator(random.choice(operators))
    value = await _generate_value_for_field(field)
    constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


async def generate_contact_card_click_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    field = "card_type"
    operators = OPERATORS_ALLOWED_CONTACT_CARD_CLICK.get(field, [])
    if not operators:
        return constraints_list
    op = ComparisonOperator(random.choice(operators))
    value = await _generate_value_for_field(field)
    constraints_list.append(create_constraint_dict(field, op, value))
    return constraints_list


# ============================================================================
# INTERNAL HELPERS
# ============================================================================
async def _generate_constraints_for_fields(
    all_fields: list[str],
    allowed_ops: dict[str, list[str]],
    required_fields: list[str] | None = None,
    max_optional: int | None = None,
    validate_dates: bool = False,
    dataset: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Generate constraints for fields. If dataset is None, it will be fetched when needed."""
    if not dataset:
        dataset = []
    if required_fields is None:
        required_fields = []
    constraints = []

    optional_fields = [f for f in all_fields if f not in required_fields]
    if max_optional is not None:
        optional_fields = random.sample(optional_fields, min(max_optional, len(optional_fields)))

    final_fields = required_fields + optional_fields

    for field in final_fields:
        if field not in allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops[field]))
        default_val = await _generate_value_for_field(field)
        value = _generate_constraint_value(op, default_val, field, dataset)

        if isinstance(value, datetime.datetime) and validate_dates and MOCK_DATES:
            min_date, max_date = min(MOCK_DATES), max(MOCK_DATES)
            value = max(min(value, max_date), min_date)

        if isinstance(value, datetime.datetime):
            value = value.isoformat()

        constraint = create_constraint_dict(field, op, value)
        constraints.append(constraint)

    return constraints


# ============================================================================
# RESTAURANT CONSTRAINT GENERATION HELPERS
# ============================================================================
def _substring(s: str) -> str:
    """Extract a random substring from a string."""
    start = random.randint(0, len(s) - 1)
    end = random.randint(start + 1, len(s))
    return s[start:end]


def _random_string_not_in(s: str, length: int = 6) -> str:
    """Generate a random string not in the given string."""
    letters = "abcdefghijklmnopqrstuvwxyz"
    out = "".join(random.choice(letters) for _ in range(length))
    while out in s:
        out = "".join(random.choice(letters) for _ in range(length))
    return out


def _generate_value_for_operator(operator: ComparisonOperator, tgt_val: Any) -> Any:
    """Generate constraint value based on operator and target value."""
    if operator == ComparisonOperator.EQUALS:
        return tgt_val

    if operator == ComparisonOperator.NOT_EQUALS:
        return _random_string_not_in(tgt_val) if isinstance(tgt_val, str) else tgt_val + 1

    if operator == ComparisonOperator.CONTAINS:
        return _substring(tgt_val) if isinstance(tgt_val, str) else str(tgt_val)

    if operator == ComparisonOperator.NOT_CONTAINS:
        return _random_string_not_in(tgt_val) if isinstance(tgt_val, str) else "xyz"

    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.GREATER_THAN}:
        return tgt_val - 1

    if operator in {ComparisonOperator.LESS_EQUAL, ComparisonOperator.LESS_THAN}:
        return tgt_val + 1

    if operator == ComparisonOperator.IN_LIST:
        return [tgt_val, _random_string_not_in(str(tgt_val))]

    if operator == ComparisonOperator.NOT_IN_LIST:
        return [_random_string_not_in(str(tgt_val))]

    return tgt_val


def _normalize_date_value(value: Any) -> Any:
    """Normalize date/datetime values to ISO format."""
    if isinstance(value, datetime.date | datetime.datetime):
        return value.isoformat()
    return value


# ============================================================================
# RESTAURANT CONSTRAINT GENERATION
# ============================================================================
def generate_restaurant_constraints(
    *,
    dataset: list[dict[str, Any]],
    fields: list[str],
    allowed_ops: dict[str, list[str]],
    max_constraints: int = 3,
) -> list[dict[str, Any]]:
    """
    Devuelve entre 1 y `max_constraints` constraints; todos usan campos de `fields`
    y, por construcción, los cumple al menos un registro del `dataset`.

    Parameters
    ----------
    dataset : list[dict]
        Lista de dicts con los datos.
    fields : list[str]
        Subconjunto de campos a usar (p.ej. ["name", "desc"]).
    allowed_ops : dict[str, list[ComparisonOperator]]
        Operadores permitidos por campo.
    max_constraints : int
        Máximo de constraints a generar (mínimo 1).

    Returns
    -------
    list[dict] con claves: ``field``, ``operator``, ``value``.
    """
    if not dataset or dataset == {}:
        raise ValueError("dataset cannot be empty")
    if not fields:
        raise ValueError("fields cannot be empty")

    # 1️⃣ Registro "solución"
    dataset = dataset.get("restaurants", [])
    target = random.choice(dataset)

    # 2️⃣ Campos que existen en target y están en `fields`
    candidate_fields = [f for f in fields if f in target and f in allowed_ops]
    if not candidate_fields:
        raise ValueError("None of the requested fields exist in both dataset and allowed_ops")

    n = random.randint(1, min(max_constraints, len(candidate_fields)))
    chosen_fields = random.sample(candidate_fields, n)

    constraints: list[dict[str, Any]] = []

    # 3️⃣ Genera un constraint por campo
    for field in chosen_fields:
        op: ComparisonOperator = random.choice(allowed_ops[field])
        tgt_val = target[field]
        value = _generate_value_for_operator(op, tgt_val)
        value = _normalize_date_value(value)
        constraints.append({"field": field, "operator": ComparisonOperator(op), "value": value})
    return constraints
