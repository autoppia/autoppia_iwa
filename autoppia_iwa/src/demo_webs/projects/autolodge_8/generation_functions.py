import random
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import resolve_v2_seed_from_url

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


async def _ensure_hotel_dataset(task_url: str | None = None, dataset: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    seed = await resolve_v2_seed_from_url(task_url) if task_url else None
    hotels = await fetch_data(seed_value=seed)
    dataset = {"hotels": hotels}

    if dataset and "hotels" in dataset:
        return dataset["hotels"]
    if dataset:
        return dataset
    return []


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

    # Handle datetime comparisons
    if isinstance(field_value, datetime):
        delta_days = random.randint(1, 5)
        if operator == ComparisonOperator.GREATER_THAN:
            return field_value - timedelta(days=delta_days)
        elif operator == ComparisonOperator.LESS_THAN:
            return field_value + timedelta(days=delta_days)
        elif operator in {
            ComparisonOperator.GREATER_EQUAL,
            ComparisonOperator.LESS_EQUAL,
            ComparisonOperator.EQUALS,
        }:
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
            # For lists, find a value in dataset that is not equal to the list
            valid = []
            for v in dataset:
                val = v.get(field)
                if val and val != field_value:
                    if isinstance(val, list):
                        valid.extend([item for item in val if item not in field_value])
                    else:
                        valid.append(val)
            return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        for _ in range(100):
            test_str = "".join(random.choice(alphabet) for _ in range(3))
            if test_str.lower() not in field_value.lower():
                return test_str
        return "xyz"  # fallback

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
        base = field_value
        if isinstance(base, int | float):
            delta = random.uniform(0.5, 2.0) if isinstance(base, float) else random.randint(1, 5)
            if operator == ComparisonOperator.GREATER_THAN:
                return round(base - delta, 2)
            elif operator == ComparisonOperator.LESS_THAN:
                return round(base + delta, 2)
            elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                return base

    # Fallback: return None
    return None


async def generate_search_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url, dataset)
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
    if not data:
        logger.warning("No hotel data available for generating search hotel constraints")
        return []
    sample_hotel = random.choice(data)
    max_guests = sample_hotel.get("maxGuests", 2)

    # Generate adults and children such that their sum <= max_guests
    adults = random.randint(0, max_guests)
    children = random.randint(0, max_guests - adults)

    sample_guests = {
        "adults": adults,
        "children": children,
        "infants": random.randint(0, 5),
        "pets": random.randint(0, 5),
    }

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_SEARCH_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        op_str = random.choice(allowed_ops)
        operator = ComparisonOperator(op_str)

        if field == "search_term":
            if sample_hotel.get("location"):
                new_field = "location"
                value = sample_hotel.get("location")
            else:
                new_field = "title"
                value = sample_hotel.get("title")
            if not value:
                continue
            value = _generate_constraint_value(operator, value, new_field, data)

        elif field in ["datesFrom", "datesTo"]:
            value = sample_hotel.get(field)
            if not value:
                logger.warning(f"Field {field} is empty!")
            value = _generate_constraint_value(operator, value, field, data)

        elif field in ["adults", "children"]:
            actual_value = sample_guests.get(field, 0)
            other_field = "children" if field == "adults" else "adults"
            other_value = sample_guests.get(other_field, 0)

            # Ensure sum of adults + children ≤ maxGuests
            value = _generate_num_of_guests_field_value(operator=operator, actual_value=actual_value, max_value=max_guests - other_value)

        else:  # infants, pets
            value = sample_guests.get(field)
            value = _generate_num_of_guests_field_value(operator, value, max_guests)

        if value is not None:
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    return constraints_list


def _generate_num_of_guests_field_value(operator: str, actual_value: int, max_value: int) -> int:
    if operator == ComparisonOperator.EQUALS:
        return actual_value
    elif operator == ComparisonOperator.NOT_EQUALS:
        # Pick any value except the actual one
        choices = [val for val in range(1, max_value + 1) if val != actual_value]
        return random.choice(choices) if choices else actual_value + 1
    elif operator == ComparisonOperator.LESS_THAN:
        # actual_value < generated_value
        if actual_value < max_value:
            val = random.randint(actual_value + 1, max_value)
            return val
        else:
            return max_value + 1
    elif operator == ComparisonOperator.LESS_EQUAL:
        # actual_value <= generated_value
        if actual_value < max_value:
            val = random.randint(actual_value, max_value)
            return val
        else:
            return max_value
    elif operator == ComparisonOperator.GREATER_THAN:
        # actual_value > generated_value
        if actual_value > 1:
            val = random.randint(1, actual_value - 1)
            return val
        else:
            return 1
    elif operator == ComparisonOperator.GREATER_EQUAL:
        # actual_value >= generated_value
        if actual_value > 1:
            val = random.randint(1, actual_value)
            return val
        else:
            return 1
    else:
        return max(1, min(actual_value, max_value))


async def __generate_view_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    possible_fields = list(FIELD_OPERATORS_VIEW_HOTEL_MAP.keys())
    num_constraints = random.randint(3, len(possible_fields))
    selected_fields = random.sample(possible_fields, num_constraints)

    # Ensure both 'datesFrom' and 'datesTo' are present if either is selected
    if "datesFrom" in selected_fields and "datesTo" not in selected_fields:
        selected_fields.append("datesTo")
    elif "datesTo" in selected_fields and "datesFrom" not in selected_fields:
        selected_fields.append("datesFrom")
    data = await _ensure_hotel_dataset(task_url, dataset)
    if not data:
        logger.warning("No hotel data available for generating view hotel constraints")
        return [], {}
    hotel = random.choice(data)
    # hotel = random.choice(HOTELS_DATA_MODIFIED)

    for field in selected_fields:
        operator = ComparisonOperator(random.choice(FIELD_OPERATORS_VIEW_HOTEL_MAP[field]))
        field_value = hotel.get(field)
        if field_value is None:
            continue
        if field == "guests":
            max_guests = hotel.get("maxGuests") or hotel.get("guests") or 1
            field_value = _generate_num_of_guests_field_value(operator, field_value, max_guests)
        elif field == "amenities":
            hotel_amenities = hotel.get("amenities", [])
            all_amenities = set()
            for h in data:
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
            field_value = _generate_constraint_value(operator, field_value, field, data)
            if field_value is None:
                continue

        constraint = create_constraint_dict(field, operator, field_value)
        constraints_list.append(constraint)
    return constraints_list, hotel


async def generate_view_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list, _ = await __generate_view_hotel_constraints(task_url, dataset=dataset)

    return constraints_list


async def _generate_reserve_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url, dataset)
    if not data:
        logger.warning("No hotel data available for generating reserve hotel constraints")
        return [], {}
    view_hotel_constraints, sample_hotel = await __generate_view_hotel_constraints(task_url, dataset=data)
    view_hotel_constraints = [c for c in view_hotel_constraints if c.get("field") != "guests"]

    view_fields = {f.get("field") for f in view_hotel_constraints}
    selected_fields = ["guests_set"]
    if "datesTo" not in view_fields:
        selected_fields.append("datesTo")
    if "datesFrom" not in view_fields:
        selected_fields.append("datesFrom")

    max_guests = sample_hotel.get("maxGuests") or sample_hotel.get("guests") or 1

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_RESERVE_HOTEL_MAP.get(field, [])
        if not allowed_ops:
            continue

        operator = ComparisonOperator(random.choice(allowed_ops))

        if field == "guests_set":
            value = random.randint(1, max_guests)
            field_value = _generate_num_of_guests_field_value(operator, value, max_guests)
            constraint = create_constraint_dict(field, operator, field_value)
            constraints_list.append(constraint)
        else:
            field_value = sample_hotel.get(field)
            if field_value is None:
                continue
            value = _generate_constraint_value(operator, field_value, field, data)
            if value is None:
                continue
            constraint = create_constraint_dict(field, operator, value)
            constraints_list.append(constraint)

    constraints_list.extend(view_hotel_constraints)
    return constraints_list, sample_hotel


async def generate_reserve_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list, sample_hotel = await _generate_reserve_hotel_constraints(task_url, dataset=dataset)
    return constraints_list


async def generate_edit_guests_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url, dataset)
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


async def generate_edit_checkin_checkout_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    reserve_constraints_list, sample_hotel = await _generate_reserve_hotel_constraints(task_url, dataset=dataset)

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


async def generate_confirm_and_pay_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    reserve_constraints, sample_hotel = await _generate_reserve_hotel_constraints(task_url, dataset=dataset)

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


async def generate_message_host_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url, dataset)
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
    constraint_list_for_view, hotel_dict = await __generate_view_hotel_constraints(task_url, dataset=data)

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


async def generate_share_hotel_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []
    data = await _ensure_hotel_dataset(task_url, dataset)
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

    constraint_list_for_view, hotel_dict = await __generate_view_hotel_constraints(task_url, dataset=data)

    field = "email"
    email_dataset = [{"email": email} for email in emails_list]

    allowed_ops = FIELD_OPERATORS_SHARE_HOTEL_MAP.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(emails_list)
    value = _generate_constraint_value(operator, field_value, field, email_dataset)

    constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(constraint_list_for_view)
    return constraints_list


async def generate_apply_filter_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    await _ensure_hotel_dataset(task_url, dataset)
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


async def generate_submit_hotel_review_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url, dataset)
    if not data:
        logger.warning("No hotel data available for generating submit review constraints")
        return []
    constraint_list_for_view, hotel_dict = await __generate_view_hotel_constraints(task_url, dataset=data)
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


async def generate_payment_method_selected_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url, dataset)
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
        value = random.choice(["card", "cash_on_arrival"]) if field == "method" else sample.get("id", 0) if field == "hotel_id" else (sample.get("title") or "")[:5]
        constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_book_from_wishlist_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    data = await _ensure_hotel_dataset(task_url, dataset)
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
        value = sample.get("id", 0) if field == "hotel_id" else (sample.get("title") or "")[:5]
        constraints.append(create_constraint_dict(field, op, value))
    return constraints


async def generate_faq_opened_constraints() -> list[dict[str, Any]]:
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
