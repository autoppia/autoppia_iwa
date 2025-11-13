import datetime
import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.projects.data_provider import load_dataset_data

from ..shared_utils import create_constraint_dict, generate_mock_date_strings, generate_mock_dates
from .data import (
    CUSINE,
    OPERATORS_ALLOWED_BOOK_RESTAURANT,
    OPERATORS_ALLOWED_COUNTRY_SELECTED,
    OPERATORS_ALLOWED_DATE_DROPDOWN_OPENED,
    OPERATORS_ALLOWED_FOR_RESTAURANT,
    OPERATORS_ALLOWED_PEOPLE_DROPDOWN_OPENED,
    OPERATORS_ALLOWED_RESERVATION_COMPLETE,
    OPERATORS_ALLOWED_SCROLL_VIEW,
    OPERATORS_ALLOWED_SEARCH_RESTAURANT,
    OPERATORS_ALLOWED_TIME_DROPDOWN_OPENED,
    RESTAURANT_COUNTRIES,
    RESTAURANT_DATA,
    RESTAURANT_OCCASIONS,
    RESTAURANT_PEOPLE_COUNTS,
    RESTAURANT_TIMES,
    SCROLL_DIRECTIONS,
    SCROLL_SECTIONS_TITLES,
)
from .main import FRONTEND_PORT_INDEX, dining_project

PROJECT_KEY = f"web_{FRONTEND_PORT_INDEX + 1}_{dining_project.id}"
ENTITY_TYPE = "restaurants"


async def _get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    items = await load_dataset_data(
        backend_url=dining_project.backend_url, project_key=PROJECT_KEY, entity_type=ENTITY_TYPE, seed_value=seed_value if seed_value is not None else 0, limit=count, method="shuffle"
    )
    if items:
        return items
    from .data import RESTAURANT_DATA

    return RESTAURANT_DATA


MOCK_DATES = generate_mock_dates()
MOCK_DATE_STRINGS = generate_mock_date_strings(MOCK_DATES)
# MOCK_PEOPLE_COUNT_STRINGS = ["1 person", "2 people", "4 guests"]
MOCK_RESTAURANT_QUERIES = ["pizza", "mexican food", "nearby cafes"] + [r["name"] for r in RESTAURANT_DATA]
MOCK_RESTAURANT_ACTIONS = ["view_full_menu", "collapse_menu"]
MOCK_PHONE_NUMBERS = ["555-1234", "9876543210", "+1-202-555-0182"]
MOCK_SPECIAL_REQUESTS = ["window seat", "allergies: nuts", "quiet table"]


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    if operator == ComparisonOperator.EQUALS:
        return field_value
    if field == "restaurant_name":
        field = "name"
    if field == "rating":
        return random.choice([2, 3])
    elif operator == ComparisonOperator.NOT_EQUALS:
        if field == "direction":
            valid = [v for v in SCROLL_DIRECTIONS if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "section_title":
            valid = [v for v in SCROLL_SECTIONS_TITLES if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "selected_time":
            valid = [v for v in RESTAURANT_TIMES if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "people_count":
            valid = [v for v in RESTAURANT_PEOPLE_COUNTS if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "occasion_type":
            valid = [v for v in RESTAURANT_OCCASIONS if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "country_name":
            valid = [v["name"] for v in RESTAURANT_COUNTRIES if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "country_code":
            valid = [v["code"] for v in RESTAURANT_COUNTRIES if v != field_value]
            return random.choice(valid) if valid else None

        valid = [v[field] for v in dataset if v.get(field) != field_value]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if field == "direction":
            valid = [v for v in SCROLL_DIRECTIONS if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "section_title":
            valid = [v for v in SCROLL_SECTIONS_TITLES if v != field_value]
            return random.choice(valid) if valid else None
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        if field == "direction":
            valid = [v for v in SCROLL_DIRECTIONS if v != field_value]
            return random.choice(valid) if valid else None
        elif field == "section_title":
            valid = [v for v in SCROLL_SECTIONS_TITLES if v != field_value]
            return random.choice(valid) if valid else None
        valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if field_value in all_values:
            all_values.remove(field_value)
        return random.sample(all_values, min(2, len(all_values))) if all_values else []

    elif operator in {
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    }:
        numeric_values = [v.get(field) for v in dataset if isinstance(v.get(field), int | float | datetime.datetime)]
        if numeric_values:
            base = random.choice(numeric_values)
            if isinstance(base, datetime.datetime):
                delta = datetime.timedelta(days=random.randint(1, 5))
                if operator == ComparisonOperator.GREATER_THAN:
                    return base - delta
                elif operator == ComparisonOperator.LESS_THAN:
                    return base + delta
                else:
                    return base
            else:
                delta = random.uniform(1, 3)
                if operator == ComparisonOperator.GREATER_THAN:
                    return round(base - delta, 2)
                elif operator == ComparisonOperator.LESS_THAN:
                    return round(base + delta, 2)
                else:
                    return round(base, 2)

    return field_value


def _generate_value_for_field(field_name: str) -> Any:
    if field_name == "selected_date":
        return random.choice(MOCK_DATES) if MOCK_DATES else datetime.datetime.now(datetime.UTC)
    elif field_name == "selected_time" or field_name == "time" or field_name == "reservation_time":
        return random.choice(RESTAURANT_TIMES)
    elif field_name == "people" or field_name == "people_count":
        return random.choice(RESTAURANT_PEOPLE_COUNTS)
    elif field_name == "query":
        return random.choice(MOCK_RESTAURANT_QUERIES)
    elif field_name == "restaurant_name" or field_name == "name":
        return random.choice(RESTAURANT_DATA)["name"] if RESTAURANT_DATA else "Default Restaurant"
    elif field_name == "action":
        return random.choice(MOCK_RESTAURANT_ACTIONS)
    elif field_name == "country_code":
        return random.choice(RESTAURANT_COUNTRIES)["code"] if RESTAURANT_COUNTRIES else "US"
    elif field_name == "country_name":
        return random.choice(RESTAURANT_COUNTRIES)["name"] if RESTAURANT_COUNTRIES else "United States"
    elif field_name == "occasion" or field_name == "occasion_type":
        return random.choice(RESTAURANT_OCCASIONS)
    elif field_name == "reservation_date_str":
        return random.choice(MOCK_DATE_STRINGS)
    elif field_name == "phone_number":
        return random.choice(MOCK_PHONE_NUMBERS)
    elif field_name == "special_request":
        return random.choice(MOCK_SPECIAL_REQUESTS)
    elif field_name == "direction":
        return random.choice(SCROLL_DIRECTIONS)
    elif field_name == "section_title":
        return random.choice(SCROLL_SECTIONS_TITLES)
    elif field_name == "desc":
        return "Enjoy a delightful experience at"
    elif field_name == "cuisine":
        return random.choice(CUSINE)
    elif field_name == "rating":
        return random.choice([2, 3, 4])

    print(f"Warning: No specific mock value generator for field '{field_name}'. Using default string.")
    return "mock_value"


# --- Constraint Generators ---
async def generate_view_restaurant_constraints():
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=4, dataset=await _get_data()
    )


async def generate_view_full_menu_constraints():
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=4, dataset=await _get_data()
    )


async def generate_collapse_menu_constraints():
    return generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=4, dataset=await _get_data()
    )


def generate_date_dropdown_opened_constraints():
    return generate_constraints_for_single_field("selected_date", OPERATORS_ALLOWED_DATE_DROPDOWN_OPENED)


def generate_time_dropdown_opened_constraints():
    return generate_constraints_for_single_field("selected_time", OPERATORS_ALLOWED_TIME_DROPDOWN_OPENED)


def generate_people_dropdown_opened_constraints():
    return generate_constraints_for_single_field("people_count", OPERATORS_ALLOWED_PEOPLE_DROPDOWN_OPENED)


def generate_search_restaurant_constraints():
    return generate_constraints_for_single_field("query", OPERATORS_ALLOWED_SEARCH_RESTAURANT)


def generate_constraints_for_single_field(field: str, allowed_operators: dict[str, list[str]]) -> list[dict[str, Any]]:
    op = ComparisonOperator(random.choice(allowed_operators[field]))
    value = _generate_value_for_field(field)
    # if field == 'selected_date' and isinstance(value, datetime.datetime):
    #     value = value.date().isoformat()
    if isinstance(value, datetime.datetime):
        value = value.isoformat()
    return [create_constraint_dict(field, op, value)]


async def generate_book_restaurant_constraints():
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=3, dataset=await _get_data()
    )
    booking_contraints = _generate_constraints_for_fields(
        all_fields=["people_count", "selected_date", "selected_time"],
        allowed_ops=OPERATORS_ALLOWED_BOOK_RESTAURANT,
        required_fields=["people_count", "selected_date", "selected_time"],
        validate_dates=True,
        dataset=await _get_data(),
    )
    all_constraints = restaurant_constraints + booking_contraints
    return all_constraints


async def generate_country_selected_constraints():
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=3, dataset=await _get_data()
    )
    country_field = random.choice(["country_name", "country_code"])
    booking_contraints = _generate_constraints_for_fields(
        all_fields=["people_count", "selected_date", "selected_time"],
        allowed_ops=OPERATORS_ALLOWED_COUNTRY_SELECTED,
        required_fields=[country_field],
        validate_dates=True,
        dataset=await _get_data(),
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


async def generate_occasion_selected_constraints():
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=3, dataset=await _get_data()
    )
    booking_contraints = _generate_constraints_for_fields(
        all_fields=["people_count", "selected_date", "selected_time"],
        allowed_ops=OPERATORS_ALLOWED_COUNTRY_SELECTED,
        required_fields=["occasion_type"],
        validate_dates=True,
        dataset=await _get_data(),
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


async def generate_reservation_complete_constraints():
    restaurant_constraints = generate_restaurant_constraints(
        fields=["name", "desc", "rating", "reviews", "cuisine", "bookings"], allowed_ops=OPERATORS_ALLOWED_FOR_RESTAURANT, max_constraints=3, dataset=await _get_data()
    )
    booking_contraints = _generate_constraints_for_fields(
        all_fields=["people_count", "country_code", "phone_number", "occasion_typeselected_date", "selected_time"],
        allowed_ops=OPERATORS_ALLOWED_RESERVATION_COMPLETE,
        required_fields=["occasion_type"],
        validate_dates=True,
        max_optional=3,
        dataset=await _get_data(),
    )
    all_constraints = restaurant_constraints + booking_contraints

    return all_constraints


def generate_scroll_view_constraints():
    return _generate_constraints_for_fields(all_fields=["section_title", "direction"], allowed_ops=OPERATORS_ALLOWED_SCROLL_VIEW, required_fields=["section_title", "direction"])


# --- Internal Helper ---


def _generate_constraints_for_fields(
    all_fields: list[str],
    allowed_ops: dict[str, list[str]],
    required_fields: list[str] | None = None,
    max_optional: int | None = None,
    validate_dates: bool = False,
    dataset: list[dict[str, Any]] = RESTAURANT_DATA,
) -> list[dict[str, Any]]:
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
        default_val = _generate_value_for_field(field)
        value = _generate_constraint_value(op, default_val, field, dataset)

        if isinstance(value, datetime.datetime) and validate_dates and MOCK_DATES:
            min_date, max_date = min(MOCK_DATES), max(MOCK_DATES)
            value = max(min(value, max_date), min_date)

        if isinstance(value, datetime.datetime):
            value = value.isoformat()

        constraint = create_constraint_dict(field, op, value)
        constraints.append(constraint)

    return constraints


# ─────────────────── helpers ──────────────────────
def _substring(s: str) -> str:
    start = random.randint(0, len(s) - 1)
    end = random.randint(start + 1, len(s))
    return s[start:end]


def _random_string_not_in(s: str, length: int = 6) -> str:
    letters = "abcdefghijklmnopqrstuvwxyz"
    out = "".join(random.choice(letters) for _ in range(length))
    while out in s:
        out = "".join(random.choice(letters) for _ in range(length))
    return out


# ─────────────────────── main generator ───────────────────
def generate_restaurant_constraints(
    *,
    dataset: list[dict[str, Any]] = RESTAURANT_DATA,
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
    if not dataset:
        raise ValueError("dataset cannot be empty")
    if not fields:
        raise ValueError("fields cannot be empty")

    # 1️⃣ Registro “solución”
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

        # Valor compatible con el operador para que target lo satisfaga
        if op == ComparisonOperator.EQUALS:
            value = tgt_val

        elif op == ComparisonOperator.NOT_EQUALS:
            value = _random_string_not_in(tgt_val) if isinstance(tgt_val, str) else tgt_val + 1

        elif op == ComparisonOperator.CONTAINS:
            value = _substring(tgt_val) if isinstance(tgt_val, str) else str(tgt_val)

        elif op == ComparisonOperator.NOT_CONTAINS:
            value = _random_string_not_in(tgt_val) if isinstance(tgt_val, str) else "xyz"

        elif op in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.GREATER_THAN}:
            value = tgt_val - 1

        elif op in {ComparisonOperator.LESS_EQUAL, ComparisonOperator.LESS_THAN}:
            value = tgt_val + 1

        elif op == ComparisonOperator.IN_LIST:
            value = [tgt_val, _random_string_not_in(str(tgt_val))]

        elif op == ComparisonOperator.NOT_IN_LIST:
            value = [_random_string_not_in(str(tgt_val))]

        else:  # fallback improbable
            value = tgt_val

        # Fechas → ISO
        if isinstance(value, datetime.date | datetime.datetime):
            value = value.isoformat()

        constraints.append({"field": field, "operator": ComparisonOperator(op), "value": value})
        print(target, constraints)
    return constraints
