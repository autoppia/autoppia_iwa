import random
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import get_seed_from_url

from ..operators import EQUALS, GREATER_EQUAL, LESS_EQUAL
from ..shared_utils import create_constraint_dict, parse_datetime
from .data import (
    FIELD_OPERATORS_APPLY_FILTERS_MAP,
    FIELD_OPERATORS_BOOK_FROM_WISHLIST_MAP,
    FIELD_OPERATORS_CONFIRM_AND_PAY_MAP,
    FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP,
    FIELD_OPERATORS_EDIT_GUESTS_MAP,
    FIELD_OPERATORS_FAQ_OPENED_MAP,
    FIELD_OPERATORS_MESSAGE_HOST_MAP,
    FIELD_OPERATORS_PAYMENT_METHOD_SELECTED_MAP,
    FIELD_OPERATORS_RESERVE_HOTEL_MAP,
    FIELD_OPERATORS_SEARCH_HOTEL_MAP,
    FIELD_OPERATORS_SHARE_HOTEL_MAP,
    FIELD_OPERATORS_SUBMIT_REVIEW_MAP,
    FIELD_OPERATORS_VIEW_HOTEL_MAP,
)
from .data_utils import fetch_data


# ============================================================================
# DATA FETCHING HELPERS
# ============================================================================
async def _ensure_hotel_dataset(task_url: str | None = None) -> list[dict[str, Any]]:
    seed = get_seed_from_url(task_url)
    hotels = await fetch_data(seed_value=seed)
    hotels_dataset = {"hotels": hotels}

    if hotels_dataset and "hotels" in hotels_dataset:
        return hotels_dataset["hotels"]
    if hotels_dataset:
        return hotels_dataset
    return []


# ============================================================================
# CONSTRAINT VALUE GENERATION HELPERS
# ============================================================================
def _handle_datetime_constraint(operator: ComparisonOperator, field_value: datetime) -> datetime:
    """Handle constraint value generation for datetime types."""
    delta_days = random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return field_value - timedelta(days=delta_days)
    if operator == ComparisonOperator.LESS_THAN:
        return field_value + timedelta(days=delta_days)
    if operator in {
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
        ComparisonOperator.EQUALS,
    }:
        return field_value
    if operator == ComparisonOperator.NOT_EQUALS:
        return field_value + timedelta(days=delta_days + 1)
    return field_value


def _handle_equals_operator(field_value: Any) -> Any:
    """Handle EQUALS operator."""
    return field_value


def _handle_not_equals_string(field_value: str, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for strings."""
    valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
    return random.choice(valid) if valid else None


def _handle_not_equals_list(field_value: list, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for lists."""
    valid = []
    for v in dataset:
        val = v.get(field)
        if val and val != field_value:
            if isinstance(val, list):
                valid.extend([item for item in val if item not in field_value])
            else:
                valid.append(val)
    return random.choice(valid) if valid else None


def _handle_contains_operator(field_value: str) -> str:
    """Handle CONTAINS operator for strings."""
    if len(field_value) > 2:
        start = random.randint(0, max(0, len(field_value) - 2))
        end = random.randint(start + 1, len(field_value))
        return field_value[start:end]
    return field_value


def _handle_not_contains_operator(field_value: str) -> str:
    """Handle NOT_CONTAINS operator for strings."""
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for _ in range(100):
        test_str = "".join(random.choice(alphabet) for _ in range(3))
        if test_str.lower() not in field_value.lower():
            return test_str
    return "xyz"  # fallback


def _extract_all_values_from_dataset(field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Extract all values for a given field from dataset, handling lists."""
    all_values = []
    for v in dataset:
        if field in v:
            val = v.get(field)
            if isinstance(val, list):
                all_values.extend(val)
            elif val is not None:
                all_values.append(val)
    return list(set(all_values))


def _handle_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle IN_LIST operator."""
    all_values = _extract_all_values_from_dataset(field, dataset)

    if not all_values:
        return [field_value]
    random.shuffle(all_values)
    subset = random.sample(all_values, min(2, len(all_values)))
    if field_value not in subset:
        subset.append(field_value)
    return list(set(subset))


def _handle_not_in_list_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> list[Any]:
    """Handle NOT_IN_LIST operator."""
    all_values = _extract_all_values_from_dataset(field, dataset)

    if field_value in all_values:
        all_values.remove(field_value)
    return random.sample(all_values, min(2, len(all_values))) if all_values else []


def _handle_numeric_comparison(operator: ComparisonOperator, base: int | float) -> int | float | None:
    """Handle numeric comparison operators."""
    delta = random.uniform(0.5, 2.0) if isinstance(base, float) else random.randint(1, 5)
    if operator == ComparisonOperator.GREATER_THAN:
        return round(base - delta, 2)
    if operator == ComparisonOperator.LESS_THAN:
        return round(base + delta, 2)
    if operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
        return base
    return None


def _generate_constraint_value(
    operator: ComparisonOperator,
    field_value: Any,
    field: str,
    dataset: list[dict[str, Any]],
) -> Any:
    """
    Generate a constraint value for a given operator, field, and dataset.
    Handles various data types and operators robustly.
    """
    # Handle amenities as a list: pick a random amenity if present
    if field == "amenities" and isinstance(field_value, list):
        field_value = random.choice(field_value) if field_value else ""

    if isinstance(field_value, datetime):
        return _handle_datetime_constraint(operator, field_value)

    if operator == ComparisonOperator.EQUALS:
        return _handle_equals_operator(field_value)

    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_not_equals_operator(field_value, field, dataset)

    if operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        return _handle_contains_operator(field_value)

    if operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        return _handle_not_contains_operator(field_value)

    if operator == ComparisonOperator.IN_LIST:
        return _handle_in_list_operator(field_value, field, dataset)

    if operator == ComparisonOperator.NOT_IN_LIST:
        return _handle_not_in_list_operator(field_value, field, dataset)

    if operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    } and isinstance(field_value, int | float):
        return _handle_numeric_comparison(operator, field_value)

    return None


def _handle_not_equals_operator(field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    """Handle NOT_EQUALS operator for different types."""
    if isinstance(field_value, str):
        return _handle_not_equals_string(field_value, field, dataset)
    if isinstance(field_value, list):
        return _handle_not_equals_list(field_value, field, dataset)
    return None


# ============================================================================
# SEARCH HOTEL CONSTRAINT HELPERS
# ============================================================================
def _select_search_fields() -> list[str]:
    """Select fields for search hotel constraints."""
    possible_fields = [
        "search_term",
        "datesFrom",
        "datesTo",
        "adults",
        "children",
        "infants",
        "pets",
    ]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    # Ensure if 'datesTo' is selected, 'datesFrom' is also selected
    if "datesTo" in selected_fields and "datesFrom" not in selected_fields:
        selected_fields.append("datesFrom")
    return selected_fields


def _generate_sample_guests(max_guests: int) -> dict[str, int]:
    """Generate sample guests data."""
    adults = random.randint(0, max_guests)
    children = random.randint(0, max_guests - adults)
    return {
        "adults": adults,
        "children": children,
        "infants": random.randint(0, 5),
        "pets": random.randint(0, 5),
    }


def _process_search_term_field(sample_hotel: dict[str, Any], operator: ComparisonOperator, data: list[dict[str, Any]]) -> Any:
    """Process search_term field constraint."""
    if sample_hotel.get("location"):
        new_field = "location"
        value = sample_hotel.get("location")
    else:
        new_field = "title"
        value = sample_hotel.get("title")
    if not value:
        return None
    return _generate_constraint_value(operator, value, new_field, data)


def _process_date_field(sample_hotel: dict[str, Any], field: str, operator: ComparisonOperator, data: list[dict[str, Any]]) -> Any:
    """Process date field constraint."""
    value = sample_hotel.get(field)
    if not value:
        logger.warning(f"Field {field} is empty!")
        return None
    return _generate_constraint_value(operator, value, field, data)


def _process_guests_field(field: str, sample_guests: dict[str, int], max_guests: int, operator: ComparisonOperator) -> int:
    """Process guests field constraint (adults, children)."""
    actual_value = sample_guests.get(field, 0)
    other_field = "children" if field == "adults" else "adults"
    other_value = sample_guests.get(other_field, 0)
    return _generate_num_of_guests_field_value(operator=operator, actual_value=actual_value, max_value=max_guests - other_value)


# ============================================================================
# GUESTS FIELD VALUE GENERATION HELPERS
# ============================================================================
def _handle_guests_equals(actual_value: int) -> int:
    """Handle EQUALS operator for guests."""
    return actual_value


def _handle_guests_not_equals(actual_value: int, max_value: int) -> int:
    """Handle NOT_EQUALS operator for guests."""
    choices = [val for val in range(1, max_value + 1) if val != actual_value]
    return random.choice(choices) if choices else actual_value + 1


def _handle_guests_less_than(actual_value: int, max_value: int) -> int:
    """Handle LESS_THAN operator for guests."""
    if actual_value < max_value:
        return random.randint(actual_value + 1, max_value)
    return max_value + 1


def _handle_guests_less_equal(actual_value: int, max_value: int) -> int:
    """Handle LESS_EQUAL operator for guests."""
    if actual_value < max_value:
        return random.randint(actual_value, max_value)
    return max_value


def _handle_guests_greater_than(actual_value: int) -> int:
    """Handle GREATER_THAN operator for guests."""
    if actual_value > 1:
        return random.randint(1, actual_value - 1)
    return 1


def _handle_guests_greater_equal(actual_value: int) -> int:
    """Handle GREATER_EQUAL operator for guests."""
    if actual_value > 1:
        return random.randint(1, actual_value)
    return 1


def _generate_num_of_guests_field_value(operator: str, actual_value: int, max_value: int) -> int:
    """Generate a value for number of guests field based on operator."""
    if operator == ComparisonOperator.EQUALS:
        return _handle_guests_equals(actual_value)
    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_guests_not_equals(actual_value, max_value)
    if operator == ComparisonOperator.LESS_THAN:
        return _handle_guests_less_than(actual_value, max_value)
    if operator == ComparisonOperator.LESS_EQUAL:
        return _handle_guests_less_equal(actual_value, max_value)
    if operator == ComparisonOperator.GREATER_THAN:
        return _handle_guests_greater_than(actual_value)
    if operator == ComparisonOperator.GREATER_EQUAL:
        return _handle_guests_greater_equal(actual_value)
    return max(1, min(actual_value, max_value))


# ============================================================================
# CONSTRAINT GENERATION FUNCTIONS
# ============================================================================
# SEARCH CONSTRAINTS
async def generate_search_hotel_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url)
    selected_fields = _select_search_fields()

    if not data:
        logger.warning("No hotel data available for generating search hotel constraints")
        return []

    sample_hotel = random.choice(data)
    max_guests = sample_hotel.get("maxGuests", 2)
    sample_guests = _generate_sample_guests(max_guests)

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SEARCH_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        if field == "search_term":
            value = _process_search_term_field(sample_hotel, operator, data)
        elif field in ["datesFrom", "datesTo"]:
            value = _process_date_field(sample_hotel, field, operator, data)
        elif field in ["adults", "children"]:
            value = _process_guests_field(field, sample_guests, max_guests, operator)
        else:  # infants, pets
            value = sample_guests.get(field)
            value = _generate_num_of_guests_field_value(operator, value, max_guests)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def _generate_num_of_guests_field_value(operator: str, actual_value: int, max_value: int) -> int:
    """Generate a value for number of guests field based on operator."""
    if operator == ComparisonOperator.EQUALS:
        return _handle_guests_equals(actual_value)
    if operator == ComparisonOperator.NOT_EQUALS:
        return _handle_guests_not_equals(actual_value, max_value)
    if operator == ComparisonOperator.LESS_THAN:
        return _handle_guests_less_than(actual_value, max_value)
    if operator == ComparisonOperator.LESS_EQUAL:
        return _handle_guests_less_equal(actual_value, max_value)
    if operator == ComparisonOperator.GREATER_THAN:
        return _handle_guests_greater_than(actual_value)
    if operator == ComparisonOperator.GREATER_EQUAL:
        return _handle_guests_greater_equal(actual_value)
    return max(1, min(actual_value, max_value))


# ============================================================================
# VIEW HOTEL CONSTRAINT HELPERS
# ============================================================================
def _select_view_hotel_fields() -> list[str]:
    """Select fields for view hotel constraints."""
    possible_fields = list(FIELD_OPERATORS_VIEW_HOTEL_MAP.keys())
    num_constraints = random.randint(3, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    # Ensure both 'datesFrom' and 'datesTo' are present if either is selected
    if "datesFrom" in selected_fields and "datesTo" not in selected_fields:
        selected_fields.append("datesTo")
    elif "datesTo" in selected_fields and "datesFrom" not in selected_fields:
        selected_fields.append("datesFrom")
    return selected_fields


def _get_all_amenities_from_data(data: list[dict[str, Any]]) -> set[str]:
    """Get all unique amenities from hotel data."""
    all_amenities = set()
    for h in data:
        all_amenities.update(h.get("amenities", []))
    return all_amenities


def _process_amenities_contains(hotel_amenities: list[str]) -> str | None:
    """Process amenities field with CONTAINS operator."""
    if hotel_amenities:
        return random.choice(hotel_amenities)
    return None


def _process_amenities_not_contains(available_amenities: list[str]) -> str:
    """Process amenities field with NOT_CONTAINS operator."""
    return random.choice(available_amenities) if available_amenities else "Non-existent amenity"


def _process_amenities_in_list(hotel_amenities: list[str]) -> list[str] | None:
    """Process amenities field with IN_LIST operator."""
    if hotel_amenities:
        num_amenities = min(len(hotel_amenities), random.randint(1, 2))
        return random.sample(hotel_amenities, num_amenities)
    return None


def _process_amenities_not_in_list(available_amenities: list[str]) -> list[str]:
    """Process amenities field with NOT_IN_LIST operator."""
    if available_amenities:
        num_amenities = min(len(available_amenities), random.randint(1, 3))
        return random.sample(available_amenities, num_amenities)
    return ["Non-existent amenity"]


def _process_amenities_field(operator: ComparisonOperator, hotel_amenities: list[str], all_amenities: set[str]) -> Any:
    """Process amenities field constraint."""
    hotel_amenities_set = set(hotel_amenities)
    available_amenities = list(all_amenities - hotel_amenities_set)

    if operator == ComparisonOperator.CONTAINS:
        return _process_amenities_contains(hotel_amenities)
    if operator == ComparisonOperator.NOT_CONTAINS:
        return _process_amenities_not_contains(available_amenities)
    if operator == ComparisonOperator.IN_LIST:
        return _process_amenities_in_list(hotel_amenities)
    if operator == ComparisonOperator.NOT_IN_LIST:
        return _process_amenities_not_in_list(available_amenities)
    return hotel_amenities


def _process_view_hotel_field(field: str, hotel: dict[str, Any], operator: ComparisonOperator, data: list[dict[str, Any]], all_amenities: set[str]) -> Any:
    """Process a single field for view hotel constraints."""
    field_value = hotel.get(field)
    if field_value is None:
        return None

    if field == "guests":
        max_guests = hotel.get("maxGuests") or hotel.get("guests") or 1
        return _generate_num_of_guests_field_value(operator, field_value, max_guests)

    if field == "amenities":
        hotel_amenities = hotel.get("amenities", [])
        return _process_amenities_field(operator, hotel_amenities, all_amenities)

    return _generate_constraint_value(operator, field_value, field, data)


async def __generate_view_hotel_constraints(task_url: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    selected_fields = _select_view_hotel_fields()
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating view hotel constraints")
        return [], {}
    hotel = random.choice(data)
    all_amenities = _get_all_amenities_from_data(data)

    for field in selected_fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_VIEW_HOTEL_MAP[field]))
        field_value = _process_view_hotel_field(field, hotel, operator, data, all_amenities)

        if field_value is None:
            continue

        constraint = create_constraint_dict(field, operator, field_value)
        constraints_list.append(constraint)
    return constraints_list, hotel


# VIEW HOTEL CONSTRAINTS
async def generate_view_hotel_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list, _ = await __generate_view_hotel_constraints(task_url)

    return constraints_list


# ============================================================================
# RESERVE HOTEL CONSTRAINT HELPERS
# ============================================================================
def _select_reserve_hotel_fields(view_fields: set[str]) -> list[str]:
    """Select fields for reserve hotel constraints."""
    selected_fields = ["guests_set"]
    if "datesTo" not in view_fields:
        selected_fields.append("datesTo")
    if "datesFrom" not in view_fields:
        selected_fields.append("datesFrom")
    return selected_fields


def _process_reserve_hotel_field(field: str, sample_hotel: dict[str, Any], operator: ComparisonOperator, max_guests: int, data: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Process a single field for reserve hotel constraints."""
    if field == "guests_set":
        value = random.randint(1, max_guests)
        field_value = _generate_num_of_guests_field_value(operator, value, max_guests)
        return create_constraint_dict(field, operator, field_value)

    field_value = sample_hotel.get(field)
    if field_value is None:
        return None
    value = _generate_constraint_value(operator, field_value, field, data)
    if value is None:
        return None
    return create_constraint_dict(field, operator, value)


async def _generate_reserve_hotel_constraints(task_url: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating reserve hotel constraints")
        return [], {}
    view_hotel_constraints, sample_hotel = await __generate_view_hotel_constraints(task_url)
    view_hotel_constraints = [c for c in view_hotel_constraints if c.get("field") != "guests"]

    view_fields = {f.get("field") for f in view_hotel_constraints}
    selected_fields = _select_reserve_hotel_fields(view_fields)

    max_guests = sample_hotel.get("maxGuests") or sample_hotel.get("guests") or 1

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_RESERVE_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        constraint = _process_reserve_hotel_field(field, sample_hotel, operator, max_guests, data)
        if constraint:
            constraints_list.append(constraint)

    constraints_list.extend(view_hotel_constraints)
    return constraints_list, sample_hotel


async def generate_reserve_hotel_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list, _ = await _generate_reserve_hotel_constraints(task_url)
    return constraints_list


async def generate_edit_guests_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url)
    # Prefer hotels that allow increasing guests (capacity >= 2). If none, bail out early.
    capacity_hotels = [h for h in data if (h.get("maxGuests") or h.get("guests") or 0) >= 2]
    if not capacity_hotels:
        logger.warning("No hotel with capacity >=2 found; cannot generate EDIT_NUMBER_OF_GUESTS constraints.")
        return []

    hotel = random.choice(capacity_hotels)
    # hotel = random.choice(HOTELS_DATA_MODIFIED)
    max_value = hotel.get("maxGuests") or hotel.get("guests") or 2  # fallback if missing

    from_guests = 1
    guests_to = random.randint(from_guests + 1, max_value)

    sample_event_data = {"from_guests": from_guests, "guests_to": guests_to}
    sample_event_data.update(hotel)

    selected_fields = ["guests_to"]

    possible_fields = list(FIELD_OPERATORS_EDIT_GUESTS_MAP.keys())
    possible_fields = [field for field in possible_fields if field not in selected_fields]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields.extend(random.sample(possible_fields, num_constraints))

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_EDIT_GUESTS_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        actual_value = sample_event_data.get(field)
        if not actual_value:
            continue
        value = _generate_num_of_guests_field_value(operator, actual_value, max_value) if field == "guests_to" else _generate_constraint_value(operator, actual_value, field, data)
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


async def generate_edit_checkin_checkout_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    reserve_constraints_list, sample_hotel = await _generate_reserve_hotel_constraints(task_url)

    possible_fields = list(FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP.keys())
    possible_fields = [field for field in possible_fields if field not in ["checkin", "checkout"]]
    num_constraints = random.randint(1, len(possible_fields))
    random.sample(possible_fields, num_constraints)

    dates_from_str = sample_hotel.get("datesFrom", "2025-08-01")
    dates_to_str = sample_hotel.get("datesTo", "2025-08-10")
    dates_from = parse_datetime(dates_from_str)
    dates_to = parse_datetime(dates_to_str)

    total_days = (dates_to - dates_from).days
    if total_days < 2:
        total_days = 2  # Ensure there is at least a 1-day gap.

    # ----------------------------
    # Generate constraint for "checkin"
    # ----------------------------
    checkin_date = dates_from
    checkin_allowed_ops = FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP.get("checkin", [])
    if checkin_allowed_ops:
        op = random.choice(checkin_allowed_ops)
        checkin_op = ComparisonOperator(op)
        if op in [EQUALS, LESS_EQUAL, GREATER_EQUAL]:
            # checkin_value = dates_from.isoformat()
            constraints_list.append(create_constraint_dict("checkin", checkin_op, dates_from))
        else:
            # Pick a checkin date between dates_from and (dates_to - 1 day)
            max_offset = total_days - 1  # ensure there is room for checkout
            offset = random.randint(1, max_offset - 1)  # offset is at most max_offset-1
            checkin_date = dates_from + timedelta(days=offset)
            # checkin_value = checkin_date.isoformat()
            constraints_list.append(create_constraint_dict("checkin", checkin_op, checkin_date))

    # ----------------------------
    # Generate constraint for "checkout"
    # ----------------------------
    checkout_allowed_ops = FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP.get("checkout", [])
    if checkout_allowed_ops:
        op = random.choice(checkout_allowed_ops)
        checkout_op = ComparisonOperator(op)
        if op in [EQUALS, LESS_EQUAL, GREATER_EQUAL]:
            # checkout_value = dates_to.isoformat()
            constraints_list.append(create_constraint_dict("checkout", checkout_op, dates_to))
        else:
            # To ensure checkout > checkin, first determine a minimal checkout date.
            minimal_checkout = checkin_date + timedelta(days=1)
            remaining_days = (dates_to - minimal_checkout).days
            if remaining_days < 0:
                remaining_days = 0
            offset = random.randint(0, remaining_days)
            checkout_date = minimal_checkout + timedelta(days=offset)
            # checkout_value = checkout_date.isoformat()
            constraints_list.append(create_constraint_dict("checkout", checkout_op, checkout_date))

    constraints_list.extend(reserve_constraints_list)

    return constraints_list


async def generate_confirm_and_pay_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    reserve_constraints, sample_hotel = await _generate_reserve_hotel_constraints(task_url)

    # Payment specific fields
    payment_fields = ["card_number", "expiration", "cvv", "zipcode", "country"]

    # Payment field values
    payment_data = {
        "card_number": random.choice(["4111111111111111", "5500000000000004", "340000000000009", "30000000000004"]),
        "expiration": random.choice(["12/25", "01/27", "06/26", "11/24"]),
        "cvv": random.choice(["123", "456", "789", "321"]),
        "zipcode": random.choice(["12345", "67890", "54321", "98765"]),
        "country": random.choice(["United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "India", "Japan"]),
    }

    # Calculate nights and costs
    dates_from = None
    dates_to = None

    for constraint in reserve_constraints:
        if constraint["field"] == "datesFrom":
            dates_from = constraint["value"]
        elif constraint["field"] == "datesTo":
            dates_to = constraint["value"]

    if dates_from and dates_to:
        nights = (dates_to - dates_from).days
        price = sample_hotel.get("price", 100)  # Default if missing
        subtotal = nights * price
        service_fee = 15
        taxes = 34
        total = subtotal + service_fee + taxes

        # Add derived cost constraints
        payment_data.update({"nights": nights, "priceSubtotal": subtotal, "serviceFee": service_fee, "taxes": taxes, "total": total})

    # Create payment constraints
    payment_constraints = []
    for field in payment_fields:
        allowed_ops = FIELD_OPERATORS_CONFIRM_AND_PAY_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        value = payment_data.get(field)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            payment_constraints.append(constraint)

    constraints_list = reserve_constraints + payment_constraints

    return constraints_list


async def generate_message_host_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating message host constraints")
        return []
    msgs_list = [
        "Is your place available for the selected dates?",
        "Can you tell me more about the amenities?",
        "Do you allow pets in your property?",
        "What is the check-in time?",
        "Is there parking available nearby?",
        "Can I get a late checkout?",
        "Are there any restaurants close to the property?",
        "Is Wi-Fi included in the price?",
        "How far is the property from the city center?",
        "Is there a washing machine available for guests?",
    ]
    constraint_list_for_view, hotel_dict = await __generate_view_hotel_constraints(task_url)

    selected_fields = ["message", "host_name"]
    sample_data = {"host_name": hotel_dict.get("host_name", ""), "message": random.choice(msgs_list)}

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MESSAGE_HOST_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = sample_data.get(field)
        value = (
            _generate_constraint_value(operator, field_value, field, [{"message": msg} for msg in msgs_list]) if field == "message" else _generate_constraint_value(operator, field_value, field, data)
        )

        constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(constraint_list_for_view)
    return constraints_list


async def generate_share_hotel_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating share hotel constraints")
        return []
    emails_list = [
        "alice.smith@example.com",
        "john.doe@gmail.com",
        "maria.jones@yahoo.com",
        "kevin_lee@outlook.com",
        "nina.patel@company.org",
        "daniel_choi@webmail.net",
        "emma.watson@school.edu",
        "lucas.gray@workplace.io",
        "olivia.brown@startup.ai",
        "ethan.miller@techcorp.com",
        "sophia.morris@researchlab.org",
        "liam.johnson@business.co",
        "ava.wilson@healthcare.org",
        "noah.thomas@banksecure.com",
        "isabella.clark@freelancer.dev",
        "elijah.walker@codebase.io",
        "mia.hall@socialapp.me",
        "james.young@nonprofit.org",
        "amelia.king@greenenergy.com",
        "logan.scott@designhub.net",
        "harper.adams@newsdaily.com",
        "sebastian.moore@fintech.ai",
        "zoe.baker@civicgroup.org",
        "jackson.evans@customsoft.dev",
        "charlotte.cox@musicstream.fm",
    ]

    constraint_list_for_view, _ = await __generate_view_hotel_constraints(task_url)

    field = "email"
    email_dataset = [{"email": email} for email in emails_list]

    allowed_ops = FIELD_OPERATORS_SHARE_HOTEL_MAP.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(emails_list)
    value = _generate_constraint_value(operator, field_value, field, email_dataset)

    constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(constraint_list_for_view)
    return constraints_list


async def generate_apply_filter_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    await _ensure_hotel_dataset(task_url)
    rating_sample = [0, 4, 4.5, 4.7]
    region_sample = [
        "USA",
        "India",
        "Italy",
        "Scotland",
        "Belgium",
        "Sweden",
        "Ireland",
        "Czech Republic",
        "Australia",
        "France",
        "Japan",
        "Poland",
        "Switzerland",
        "UK",
        "Germany",
        "Indonesia",
        "Turkey",
        "Greece",
        "Spain",
        "Portugal",
        "Austria",
        "Hungary",
        "Iceland",
        "UAE",
        "Luxembourg",
        "Denmark",
        "Russia",
        "Norway",
        "Netherlands",
    ]
    possible_fields = ["rating", "region"]
    constraint_list = []
    for field in possible_fields:
        allowed_ops = FIELD_OPERATORS_APPLY_FILTERS_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        if field == "rating":
            value = random.choice(rating_sample)
            constraint_list.append(create_constraint_dict(field, operator, value))
        if field == "region":
            value = random.choice(region_sample)
            constraint_list.append(create_constraint_dict(field, operator, value))

    return constraint_list


async def generate_submit_hotel_review_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating submit review constraints")
        return []
    constraint_list_for_view, _ = await __generate_view_hotel_constraints(task_url)
    selected_fields = [random.choice(["name", "comment", "rating"])]
    constraints_list = []
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SUBMIT_REVIEW_MAP.get(field, [])
        operator = ComparisonOperator(random.choice(allowed_ops))
        if field == "rating":
            sample_rating = [3, 3.5, 4, 4.5, 5]
            rating = random.choice(sample_rating)

            constraints_list.append(create_constraint_dict("rating", operator, rating))
            # constraints_list.extend(constraint_list_for_view)

        # ----- For comment -----
        elif field == "comment":
            sample_comment = ["great stay!", "good environment"]
            comment = random.choice(sample_comment)

            constraints_list.append(create_constraint_dict("comment", operator, comment))
            # constraints_list.extend(constraint_list_for_view)

        # ----- For name -----
        elif field == "name":
            sample_name = ["Emily", "John", "Alex"]
            name = random.choice(sample_name)

            constraints_list.append(create_constraint_dict("name", operator, name))
            # constraints_list.extend(constraint_list_for_view)
    complete_constraint_list = constraint_list_for_view + constraints_list
    return complete_constraint_list


# REVIEW CONSTRAINTS
async def generate_submit_hotel_review_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating submit review constraints")
        return []
    constraint_list_for_view, _ = await __generate_view_hotel_constraints(task_url)
    selected_fields = [random.choice(["name", "comment", "rating"])]
    constraints_list = []
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SUBMIT_REVIEW_MAP.get(field, [])
        operator = ComparisonOperator(random.choice(allowed_ops))
        if field == "rating":
            sample_rating = [3, 3.5, 4, 4.5, 5]
            rating = random.choice(sample_rating)
            constraints_list.append(create_constraint_dict("rating", operator, rating))
        elif field == "comment":
            sample_comment = ["great stay!", "good environment"]
            comment = random.choice(sample_comment)
            constraints_list.append(create_constraint_dict("comment", operator, comment))
        elif field == "name":
            sample_name = ["Emily", "John", "Alex"]
            name = random.choice(sample_name)
            constraints_list.append(create_constraint_dict("name", operator, name))
    complete_constraint_list = constraint_list_for_view + constraints_list
    return complete_constraint_list


async def generate_payment_method_selected_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating payment method selected constraints")
        return []
    sample = random.choice(data)
    constraints = []
    for field in ["method", "hotel_id", "title"]:
        allowed_ops = {
            "method": FIELD_OPERATORS_PAYMENT_METHOD_SELECTED_MAP.get("method", []),
            "hotel_id": FIELD_OPERATORS_PAYMENT_METHOD_SELECTED_MAP.get("hotel_id", []),
            "title": FIELD_OPERATORS_PAYMENT_METHOD_SELECTED_MAP.get("title", []),
        }.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "method":
            value = random.choice(["card", "cash_on_arrival"])
        elif field == "hotel_id":
            value = sample.get("id", 0)
        else:
            value = (sample.get("title") or "")[:5]
        constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_book_from_wishlist_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url)
    if not data:
        logger.warning("No hotel data available for generating book from wishlist constraints")
        return []
    sample = random.choice(data)
    constraints: list[dict[str, Any]] = []
    for field in ["hotel_id", "title"]:
        allowed_ops = FIELD_OPERATORS_BOOK_FROM_WISHLIST_MAP.get(field, [])
        if not allowed_ops:
            continue
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "hotel_id":
            value = sample.get("id", 0)
        else:
            value = (sample.get("title") or "")[:5]
        constraints.append(create_constraint_dict(field, op, value))
    return constraints


def generate_faq_opened_constraints() -> list[dict[str, Any]]:
    sample_questions = [
        "How do I change or cancel my reservation?",
        "What payment options are available?",
        "How do I contact the host?",
        "How is pricing calculated?",
    ]
    question = random.choice(sample_questions)
    allowed_ops = FIELD_OPERATORS_FAQ_OPENED_MAP.get("question", [ComparisonOperator.CONTAINS.value])
    op = ComparisonOperator(random.choice(allowed_ops))
    return [create_constraint_dict("question", op, question[:6])]
