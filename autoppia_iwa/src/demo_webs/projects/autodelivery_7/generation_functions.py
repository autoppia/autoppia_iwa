import random
from typing import Any

from autoppia_iwa.src.demo_webs.projects.criterion_helper import ComparisonOperator

from ..shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_ADD_TO_CART_MAP,
    FIELD_OPERATORS_ADD_TO_CART_MODAL_OPEN_MAP,
    FIELD_OPERATORS_ADDRESS_ADDED_MAP,
    FIELD_OPERATORS_DELETE_REVIEW_MAP,
    FIELD_OPERATORS_DROPOFF_OPTION_MAP,
    FIELD_OPERATORS_INCREMENT_QUANTITY_MAP,
    FIELD_OPERATORS_PLACE_ORDER_MAP,
    FIELD_OPERATORS_SEARCH_RESTAURANT_MAP,
    FIELD_OPERATORS_VIEW_RESTAURANT_MAP,
    RESTAURANTS_DATA,
)


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        valid = [v[field] for v in dataset if v.get(field) != field_value]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        valid = [v[field] for v in dataset if isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.IN_LIST:
        all_values = list({v.get(field) for v in dataset if field in v})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
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


def generate_search_restaurant_constraints() -> list[dict[str, Any]]:
    constraints_list: list[dict[str, Any]] = []

    search_terms = []
    for item in RESTAURANTS_DATA:
        if item.get("name"):
            search_terms.append(item["name"])
        if item.get("cuisine"):
            search_terms.append(item["cuisine"])
        for menu_item in item.get("menu", []):
            if menu_item.get("name"):
                search_terms.append(menu_item["name"])

    query = random.choice(search_terms)
    field = "query"
    allowed_ops = FIELD_OPERATORS_SEARCH_RESTAURANT_MAP.get(field, [])
    operator = ComparisonOperator(random.choice(allowed_ops))

    value = _generate_constraint_value(operator, query, field, [{"query": t} for t in search_terms])

    if value is not None:
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


def __generate_view_restaurant_constraints() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list = []
    fields = ["name", "cuisine", "rating", "description"]
    num_constraints = random.randint(2, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    restaurant = random.choice(RESTAURANTS_DATA)

    for field in selected_fields:
        field_value = restaurant.get(field)
        allowed_ops = FIELD_OPERATORS_VIEW_RESTAURANT_MAP.get(field, [])
        if not allowed_ops:
            return []
        operator = ComparisonOperator(random.choice(allowed_ops))

        value = _generate_constraint_value(operator, field_value, field, RESTAURANTS_DATA)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list, restaurant


def generate_view_restaurant_constraints() -> list[dict]:
    constraints_list, _ = __generate_view_restaurant_constraints()

    return constraints_list


def _get_menu_items() -> list[dict[str, Any]]:
    menu_items = []
    for restaurant in RESTAURANTS_DATA:
        for menu_item in restaurant.get("menu", []):
            menu_items.append(
                {
                    "item": menu_item.get("name"),
                    "price": menu_item.get("price"),
                    "size": menu_item.get("size"),
                    "quantity": random.randint(1, 5),
                    "restaurant": restaurant.get("name"),
                }
            )
    return menu_items


def _get_menu_items_for_restaurant(restaurant: dict) -> list[dict[str, Any]]:
    return [
        {
            "item": menu_item.get("name"),
            "price": menu_item.get("price"),
            "size": menu_item.get("size"),
            "quantity": random.randint(1, 5),
            "restaurant": restaurant.get("name"),
        }
        for menu_item in restaurant.get("menu", [])
    ]


def __generate_add_to_cart_modal_open_constraints() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list = []
    if not RESTAURANTS_DATA:
        return [], {}
    restaurant = random.choice(RESTAURANTS_DATA)
    menu_items = _get_menu_items_for_restaurant(restaurant)
    if not menu_items:
        return [], {}
    item = random.choice(menu_items)
    menu_dataset = _get_menu_items()
    fields = ["item", "price"]
    num_constraints = random.randint(1, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    selected_fields.append("restaurant")
    for field in selected_fields:
        field_value = item.get(field)
        allowed_ops = FIELD_OPERATORS_ADD_TO_CART_MODAL_OPEN_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        value = _generate_constraint_value(operator, field_value, field, dataset=menu_dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list, item


def generate_add_to_cart_modal_open_constraints() -> list[dict]:
    constraints_list, _ = __generate_add_to_cart_modal_open_constraints()
    return constraints_list


def _get_new_quantity_value(operator: ComparisonOperator) -> int:
    # new_quantity must be between 2 and 10 (inclusive), can't be 0 or 1
    if operator == ComparisonOperator.EQUALS:
        return random.randint(2, 10)
    elif operator == ComparisonOperator.NOT_EQUALS:
        # Pick a value not equal to a randomly chosen forbidden value (2-10)
        forbidden = random.randint(2, 10)
        choices = [v for v in range(2, 11) if v != forbidden]
        return random.choice(choices)
    elif operator == ComparisonOperator.GREATER_THAN:
        # Must be at least 3 (since can't be 1 or 2)
        return random.randint(3, 10)
    elif operator == ComparisonOperator.LESS_THAN:
        # Must be at most 9 (since can't be 1)
        return random.randint(2, 9)
    elif operator == ComparisonOperator.GREATER_EQUAL or operator == ComparisonOperator.LESS_EQUAL:
        return random.randint(2, 10)
    else:
        return random.randint(2, 10)


def __generate_add_to_cart_options_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    model_constraints, _ = __generate_add_to_cart_modal_open_constraints()
    field = "quantity"

    allowed_ops = FIELD_OPERATORS_INCREMENT_QUANTITY_MAP.get(field, [])
    if not allowed_ops:
        return []
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = _get_new_quantity_value(operator)
    constraints_list.append(create_constraint_dict(field, operator, field_value))
    constraints_list.extend(model_constraints)
    return constraints_list


def generate_increment_item_restaurant_constraints() -> list[dict]:
    constraints_list = __generate_add_to_cart_options_constraints()
    return constraints_list


def __get_delete_review_fields(restaurants):
    result = []
    for r in restaurants:
        base = {
            "name": r.get("name"),
            "cuisine": r.get("cuisine"),
            "rating": r.get("rating"),
            "description": r.get("description"),
        }
        for review in r.get("reviews", []):
            entry = base.copy()
            entry.update(
                {
                    "review_rating": review.get("rating"),
                    "author": review.get("author"),
                    "date": review.get("date"),
                    "comment": review.get("comment"),
                }
            )
            result.append(entry)
    return result


def generate_delete_review_constraints() -> list[dict]:
    constraints_list, _ = __generate_view_restaurant_constraints()
    delete_review_dict = __get_delete_review_fields(RESTAURANTS_DATA)

    fields = ["author", "review_rating", "comment"]  # , "date"]
    num_constraints = random.randint(1, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_DELETE_REVIEW_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        field_values = [d[field] for d in delete_review_dict if field in d]
        if not field_values:
            continue
        field_value = random.choice(field_values)
        dataset = [{field: d[field]} for d in delete_review_dict if field in d]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


def generate_add_to_cart_constraints() -> list[dict]:
    constraints_list = []
    sizes_list = ["small", "medium", "large"]
    preferences_list = [
        "vegan",
        "vegetarian",
        "gluten-free",
        "dairy-free",
        "nut-free",
        "halal",
        "kosher",
        "paleo",
        "keto",
        "low-carb",
        "low-fat",
        "high-protein",
        "organic",
        "sugar-free",
        "soy-free",
        "egg-free",
        "seafood-free",
        "spicy",
        "mild",
        "no-onion",
        "no-garlic",
        "whole30",
        "lactose-free",
        "peanut-free",
        "shellfish-free",
    ]
    common_add_to_cart_constraints = __generate_add_to_cart_options_constraints()
    fields = ["size", "preferences"]
    num_constraints = random.randint(1, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_ADD_TO_CART_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        if field == "size":
            field_value = random.choice(sizes_list)
            dataset = [{"size": s} for s in sizes_list]
        elif field == "preferences":
            field_value = random.choice(preferences_list)
            dataset = [{"preferences": p} for p in preferences_list]
        else:
            field_value = None
        if field_value is not None:
            value = _generate_constraint_value(operator, field_value, field, dataset)
            if value is not None:
                constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(common_add_to_cart_constraints)
    return constraints_list


def generate_dropoff_option_constraints() -> list[dict]:
    constraints_list = []
    dropoffOptions = ["Leave it at my door", "Hand it to me", "Meet outside", "Meet in the lobby", "Call upon arrival", "Text when arriving"]

    field = "delivery_preference"
    allowed_ops = FIELD_OPERATORS_DROPOFF_OPTION_MAP[field]
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(dropoffOptions)
    dataset = [{"delivery_preference": opt} for opt in dropoffOptions]
    value = _generate_constraint_value(operator, field_value, field, dataset)
    constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


ADDRESSES = [
    "123 Maple Street, Springfield",
    "456 Oak Avenue, Metropolis",
    "789 Pine Road, Riverdale",
    "101 Elm Drive, Centerville",
    "202 Birch Lane, Lakeview",
    "303 Cedar Court, Hilltown",
    "404 Walnut Blvd, Brookside",
    "505 Cherry Circle, Fairview",
    "606 Aspen Way, Greenfield",
    "707 Willow Place, Sunnyvale",
]


def _get_address_dataset():
    return [{"address": addr} for addr in ADDRESSES]


def generate_address_added_constraints() -> list[dict]:
    constraints_list = []
    add_to_cart_constraint = generate_add_to_cart_constraints()

    field = "address"
    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_ADDRESS_ADDED_MAP[field]))
    field_value = random.choice(ADDRESSES)
    dataset = _get_address_dataset()
    value = _generate_constraint_value(operator, field_value, field, dataset)
    constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(add_to_cart_constraint)
    return constraints_list


# def generate_pickup_mode_constraints() -> list[dict]:
#     constraints_list = []
#     add_to_cart_constraint = generate_add_to_cart_constraints()
#     field = "mode" # pickup mode
#     operator = random.choice(FIELD_OPERATORS_PICKUP_MODE_MAP[field])
#     modes=['delivery', 'pickup']
#     field_value = random.choice(modes)
#     value = _generate_constraint_value(operator, field_value, field, [{"mode": v} for v in modes])
#     constraints_list.append(create_constraint_dict(field, operator, value))
#     constraints_list.extend(add_to_cart_constraint)
#     return constraints_list


def generate_place_order_constraints() -> list[dict]:
    constraints = []
    names = [
        "Alice Johnson",
        "Bob Smith",
        "Charlie Lee",
        "Diana Patel",
        "Ethan Brown",
        "Fiona Garcia",
        "George Kim",
        "Hannah Nguyen",
        "Ivan Martinez",
        "Julia Chen",
    ]

    phones = [
        "+1-555-123-4567",
        "+1-555-234-5678",
        "+1-555-345-6789",
        "+1-555-456-7890",
        "+1-555-567-8901",
        "+1-555-678-9012",
        "+1-555-789-0123",
        "+1-555-890-1234",
        "+1-555-901-2345",
        "+1-555-012-3456",
    ]

    # Create mock order_data instead of referencing undefined variable
    order_data = {
        "username": random.choice(names),
        "phone": random.choice(phones),
        "address": random.choice(ADDRESSES),
        "mode": random.choice(["delivery", "pickup"]),
    }

    fields = ["username", "phone", "address", "mode"]
    num_constraints = random.randint(2, len(fields))
    selected_fields = random.sample(fields, num_constraints)

    for field in selected_fields:
        ops = FIELD_OPERATORS_PLACE_ORDER_MAP[field]
        operator = ComparisonOperator(random.choice(ops))
        field_value = order_data.get(field)
        value = _generate_constraint_value(operator, field_value, field, dataset=[{field: v} for v in order_data[field] if v is not None])
        if value:
            constraints.append(create_constraint_dict(field, operator, value))
    add_to_cart_constraint = generate_add_to_cart_constraints()
    constraints.extend(add_to_cart_constraint)
    return constraints
