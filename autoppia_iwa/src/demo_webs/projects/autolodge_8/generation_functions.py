import random
from datetime import datetime, timedelta
from random import choice
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_CONFIRM_AND_PAY_MAP,
    FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP,
    FIELD_OPERATORS_INCREASE_GUESTS_MAP,
    FIELD_OPERATORS_MESSAGE_HOST_MAP,
    FIELD_OPERATORS_RESERVE_HOTEL_MAP,
    FIELD_OPERATORS_SEARCH_HOTEL_MAP,
    FIELD_OPERATORS_VIEW_HOTEL_MAP,
    HOTELS_DATA_MODIFIED,
    parse_datetime,
)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None
    if field == "amenities" and isinstance(field_value, list):
        field_value = choice(field_value) if field_value else ""

    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        elif operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        elif operator == ComparisonOperator.GREATER_EQUAL or operator == ComparisonOperator.LESS_EQUAL or operator == ComparisonOperator.EQUALS:
            return field_value
        elif operator == ComparisonOperator.NOT_EQUALS:
            return field_value + timedelta(days=delta_days + 1)

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        if isinstance(field_value, str):
            valid = [v[field] for v in dataset if v.get(field) and v.get(field) != field_value]
            return random.choice(valid) if valid else None
        elif isinstance(field_value, list):
            valid = [v[f] for v in dataset for f in field_value if v.get(f) and v.get(f) != field_value]
            return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        while True:
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str

    elif operator == ComparisonOperator.IN_LIST:
        all_values = []
        for v in dataset:
            if field in v:
                val = v.get(field)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = []
        for v in dataset:
            if field in v:
                val = v.get(field)
                if isinstance(val, list):
                    all_values.extend(val)
                elif val is not None:
                    all_values.append(val)
        all_values = list(set(all_values))

        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float)]
        if numeric_values:
            base = random.choice(numeric_values)
            delta = random.uniform(1, 3)
            if operator == ComparisonOperator.GREATER_THAN:
                return round(base - delta, 2)
            elif operator == ComparisonOperator.LESS_THAN:
                return round(base + delta, 2)
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                return round(base, 2)

    return value


def generate_search_hotel_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = [
        "search_term",
        "dateFrom",
        "dateTo",
        "adults",
        "children",
        "infants",
        "pets",
    ]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    sample_hotel = random.choice(HOTELS_DATA_MODIFIED)

    # Dummy guests and date ranges to simulate constraint values
    sample_guests = {
        "adults": random.randint(1, 4),
        "children": random.randint(0, 2),
        "infants": random.randint(0, 1),
        "pets": random.randint(0, 1),
    }

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SEARCH_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        if field == "search_term":
            value = sample_hotel.get("location") or sample_hotel.get("title")
        elif field in ["date_from", "date_to"]:
            value = sample_hotel.get(field)
            if not value:
                logger.warning(f"Field {field} is empty!")
        else:
            value = sample_guests.get(field)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


# def generate_search_cleared_constraints() -> list[dict[str, Any]]:
#     constraints_list: list[dict[str, Any]] = []
#
#     field = "source"
#     possible_sources = ["location", "date", "guests"]
#
#     allowed_ops = [
#         ComparisonOperator.EQUALS.value,
#         ComparisonOperator.NOT_EQUALS.value,
#         ComparisonOperator.CONTAINS.value,
#         ComparisonOperator.NOT_CONTAINS.value,
#     ]
#
#     operator_str = random.choice(allowed_ops)
#     operator = ComparisonOperator(operator_str)
#
#     source_value = random.choice(possible_sources)
#
#     if operator == ComparisonOperator.EQUALS:
#         value = source_value
#
#     elif operator == ComparisonOperator.NOT_EQUALS:
#         value = random.choice([s for s in possible_sources if s != source_value])
#
#     elif operator == ComparisonOperator.CONTAINS:
#         # Substring of the selected source
#         if len(source_value) > 3:
#             start = random.randint(0, len(source_value) - 2)
#             end = random.randint(start + 1, len(source_value))
#             value = source_value[start:end]
#         else:
#             value = source_value
#
#     elif operator == ComparisonOperator.NOT_CONTAINS:
#         # Substring not in any of the source values
#         alphabet = "abcdefghijklmnopqrstuvwxyz"
#         while True:
#             random_substring = "".join(random.choices(alphabet, k=3))
#             if all(random_substring not in s for s in possible_sources):
#                 value = random_substring
#                 break
#
#     constraint = create_constraint_dict(field, operator, value)
#     constraints_list.append(constraint)
#
#     return constraints_list


def _generate_num_of_guests_field_value(operator: str, actual_value: int, field: str, max_value: int) -> int:
    if operator == ComparisonOperator.EQUALS:
        return actual_value
    elif operator == ComparisonOperator.NOT_EQUALS:
        return random.choice([val for val in range(1, max_value + 1) if val != actual_value])
    elif operator == ComparisonOperator.LESS_THAN:
        if actual_value > 1:
            val = random.randint(1, actual_value - 1)
            return max(1, min(val, max_value))
        else:
            return max_value if max_value > 1 else 2
    elif operator == ComparisonOperator.LESS_EQUAL:
        val = random.randint(1, actual_value)
        v_val = max(1, min(val, max_value))
        return v_val if v_val < max_value else max_value - 1
    elif operator == ComparisonOperator.GREATER_THAN:
        if actual_value < max_value:
            val = random.randint(actual_value + 1, max_value)
            return max(1, min(val, max_value))
        else:
            return max_value - 1
    elif operator == ComparisonOperator.GREATER_EQUAL:
        val = random.randint(actual_value, max_value)
        return max(1, min(val, max_value))
    else:
        return max(1, min(actual_value, max_value))


def __generate_view_hotel_constraints() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(FIELD_OPERATORS_VIEW_HOTEL_MAP.keys())
    num_constraints = random.randint(3, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)
    hotel = choice(HOTELS_DATA_MODIFIED)

    for field in selected_fields:
        operator = ComparisonOperator(choice(FIELD_OPERATORS_VIEW_HOTEL_MAP[field]))
        field_value = hotel.get(field)
        if field_value is None:
            continue
        if field == "guests":
            max_guests = hotel.get("maxGuests") or hotel.get("guests") or 1
            field_value = _generate_num_of_guests_field_value(operator, field_value, field, max_guests)
        elif field == "amenities":
            hotel_amenities = hotel.get("amenities", [])
            all_amenities = set()
            for h in HOTELS_DATA_MODIFIED:
                all_amenities.update(h.get("amenities", []))
            hotel_amenities_set = set(hotel_amenities)
            available_amenities = list(all_amenities - hotel_amenities_set)

            if operator == ComparisonOperator.CONTAINS:
                if hotel_amenities:
                    field_value = random.choice(hotel_amenities)
                else:
                    continue  # Cannot create this constraint
            elif operator == ComparisonOperator.NOT_CONTAINS:
                field_value = random.choice(available_amenities) if available_amenities else "Non-existent amenity"
            elif operator == ComparisonOperator.IN_LIST:
                if hotel_amenities:
                    num_amenities = min(len(hotel_amenities), random.randint(1, 2))
                    field_value = random.sample(hotel_amenities, num_amenities)
                else:
                    continue  # Cannot create this constraint
            elif operator == ComparisonOperator.NOT_IN_LIST:
                if available_amenities:
                    num_amenities = min(len(available_amenities), random.randint(1, 3))
                    field_value = random.sample(available_amenities, num_amenities)
                else:
                    field_value = ["Non-existent amenity"]
            else:
                field_value = hotel_amenities
        else:
            field_value = _generate_constraint_value(operator, field_value, field, HOTELS_DATA_MODIFIED)
            if field_value is None:
                continue

        constraint = create_constraint_dict(field, operator, field_value)
        constraints_list.append(constraint)
    return constraints_list, hotel


def generate_view_hotel_constraints() -> list[dict[str, Any]]:
    constraints_list, _ = __generate_view_hotel_constraints()

    return constraints_list


def generate_reserve_hotel_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    view_hotel_constraints = generate_view_hotel_constraints()

    selected_fields = ["guests"]
    possible_fields = list(FIELD_OPERATORS_RESERVE_HOTEL_MAP.keys())
    possible_fields = [field for field in possible_fields if field not in selected_fields]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields.extend(random.sample(possible_fields, num_constraints))

    hotel = random.choice(HOTELS_DATA_MODIFIED)
    max_guests = hotel.get("maxGuests") or hotel.get("guests") or 1
    field_map = {"checkin": "datesFrom", "checkout": "datesTo"}

    for field in selected_fields:
        if field == "guests" and any(f.get("field") == "guests" for f in view_hotel_constraints):
            continue
        allowed_ops = FIELD_OPERATORS_RESERVE_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        field = field_map.get(field, field)

        value = random.randint(1, max_guests) if field == "guests" else hotel.get(field, hotel.get("maxGuests", 1))

        if value is None:
            continue

        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)
    constraints_list.extend(view_hotel_constraints)
    return constraints_list


def generate_increase_guests_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    hotel = choice(HOTELS_DATA_MODIFIED)
    max_value = hotel.get("maxGuests") or hotel.get("guests") or 2  # fallback if missing

    from_guests = 1
    to_guests = random.randint(from_guests + 1, max_value)

    sample_event_data = {"from_guests": from_guests, "to_guests": to_guests}
    sample_event_data.update(hotel)

    selected_fields = ["to_guests"]

    possible_fields = list(FIELD_OPERATORS_INCREASE_GUESTS_MAP.keys())
    possible_fields = [field for field in possible_fields if field not in selected_fields]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields.extend(random.sample(possible_fields, num_constraints))

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_INCREASE_GUESTS_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        actual_value = sample_event_data.get(field)
        if not actual_value:
            continue
        if field == "to_guests":
            value = _generate_num_of_guests_field_value(operator, actual_value, field, max_value)
        else:
            value = _generate_constraint_value(operator, actual_value, field, HOTELS_DATA_MODIFIED)
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


# def generate_decrease_guests_constraints() -> list[dict[str, Any]]:
#     constraints_list: list[dict[str, Any]] = []
#
#     # Always decrement by 1
#     from_guests = random.randint(2, 5)  # to_guests must remain ≥1
#     to_guests = from_guests - 1
#
#     sample_event_data = {
#         "from_guests": from_guests,
#         "to_guests": to_guests,
#     }
#
#     possible_fields = ["from_guests", "to_guests"]
#     num_constraints = random.randint(1, len(possible_fields))
#     selected_fields = random.sample(possible_fields, num_constraints)
#
#     for field in selected_fields:
#         allowed_ops = FIELD_OPERATORS_GUESTS_CHANGE_MAP.get(field, [])
#         if not allowed_ops:
#             continue
#
#         operator = ComparisonOperator(random.choice(allowed_ops))
#         value = sample_event_data[field]
#         constraint = create_constraint_dict(field, operator, value)
#         constraints_list.append(constraint)
#
#     return constraints_list


def generate_edit_checkin_checkout_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    possible_fields = ["checkin", "checkout", "source"]
    num_constraints = random.randint(1, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    sample_hotel = random.choice(HOTELS_DATA_MODIFIED)
    checkin = parse_datetime(sample_hotel.get("checkin", "2025-08-01"))
    checkout = parse_datetime(sample_hotel.get("checkout", "2025-08-05"))
    source = "calendar_edit"

    sample_data = {
        "checkin": checkin,
        "checkout": checkout,
        "source": source,
    }

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_EDIT_CHECKIN_OUT_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        value = sample_data[field]
        if not value:
            continue

        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


def generate_confirm_and_pay_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    # payment_methods = ["VISA", "MasterCard", "PayPal"]
    card_numbers = ["4111111111111111", "5500000000000004", "340000000000009", "30000000000004"]
    expiration = ["12/25", "01/27", "06/26", "11/24"]
    cvv = ["123", "456", "789", "321"]
    zipcode = ["12345", "67890", "54321", "98765"]
    countries = ["United States", "Canada", " United Kingdom", "Australia", "Germany", "France", "India", "Japan"]

    hotel = random.choice(HOTELS_DATA_MODIFIED)

    # Basic field mapping
    field_mapping = {
        "checkin": "datesFrom",
        "checkout": "datesTo",
        "guests": "guests",
        "listingTitle": "title",
        "pricePerNight": "price",
        "nights": None,
        "priceSubtotal": None,
    }

    sample_data = {
        "total": lambda h: ((h["datesTo"] - h["datesFrom"]).days * h["price"] + 15 + 34),
        # "paymentMethod": lambda _: random.choice(payment_methods),
        "card_number": lambda _: random.choice(card_numbers),
        "expiration": lambda _: random.choice(expiration),
        "cvv": lambda _: random.choice(cvv),
        "zipcode": lambda _: random.choice(zipcode),
        "country": lambda _: random.choice(countries),
    }

    # Initial required fields
    selected_fields = ["checkin", "checkout", "guests", "card_number", "expiration", "cvv", "zipcode", "country"]

    # Additional confirm-and-pay fields
    extra_confirm_fields = list(FIELD_OPERATORS_CONFIRM_AND_PAY_MAP.keys())
    extra_confirm_fields = [f for f in extra_confirm_fields if f not in selected_fields]
    confirm_sample_count = random.randint(1, len(extra_confirm_fields))
    selected_fields += random.sample(extra_confirm_fields, confirm_sample_count)

    # Random view-hotel fields
    hotel_sample_count = random.randint(2, len(FIELD_OPERATORS_VIEW_HOTEL_MAP.keys()))
    selected_fields += random.sample(list(FIELD_OPERATORS_VIEW_HOTEL_MAP.keys()), hotel_sample_count)

    # Merge operator maps
    field_operators = {**FIELD_OPERATORS_CONFIRM_AND_PAY_MAP, **FIELD_OPERATORS_VIEW_HOTEL_MAP}

    # Generate constraints
    for field in selected_fields:
        allowed_ops = field_operators.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        value = None

        # Value from sample_data
        if field in sample_data:
            value = sample_data[field](hotel)

        # Value from mapped hotel field
        elif field in field_mapping:
            mapped = field_mapping[field]
            if isinstance(mapped, str):
                value = hotel.get(mapped)
            elif field in ["checkin", "checkout"]:
                raw_date = hotel.get(field_mapping[field])
                value = parse_datetime(raw_date)

        elif field in hotel:
            value = hotel[field]
            value = _generate_constraint_value(operator, value, field, HOTELS_DATA_MODIFIED)

        # Computed values
        if field == "nights":
            nights = (parse_datetime(hotel["datesTo"]) - parse_datetime(hotel["datesFrom"])).days
            value = nights
        elif field == "priceSubtotal":
            nights = (parse_datetime(hotel["datesTo"]) - parse_datetime(hotel["datesFrom"])).days
            value = nights * hotel["price"]

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def generate_message_host_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
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
    constraint_list_for_view, hotel_dict = __generate_view_hotel_constraints()

    selected_fields = ["message", "host_name"]
    sample_data = {"host_name": hotel_dict.get("host_name", ""), "message": random.choice(msgs_list)}

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_MESSAGE_HOST_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))
        value = sample_data.get(field)
        constraint = (
            _generate_constraint_value(operator, value, field, [{"message": msg} for msg in msgs_list])
            if field == "message"
            else _generate_constraint_value(operator, value, field, HOTELS_DATA_MODIFIED)
        )
        constraints_list.append(constraint)
    constraints_list.extend(constraint_list_for_view)
    return constraints_list
