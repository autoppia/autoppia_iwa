import random
from typing import Any

from autoppia_iwa.src.demo_webs.criterion_helper import ComparisonOperator
from autoppia_iwa.src.demo_webs.data_provider import get_seed_from_url

from ...shared_utils import create_constraint_dict
from .data import (
    FIELD_OPERATORS_ADD_TO_CART_MAP,
    FIELD_OPERATORS_ADD_TO_CART_MODAL_OPEN_MAP,
    FIELD_OPERATORS_ADDRESS_ADDED_MAP,
    FIELD_OPERATORS_DELETE_REVIEW_MAP,
    FIELD_OPERATORS_DROPOFF_OPTION_MAP,
    FIELD_OPERATORS_INCREMENT_QUANTITY_MAP,
    FIELD_OPERATORS_PLACE_ORDER_MAP,
    FIELD_OPERATORS_QUICK_REORDER_MAP,
    FIELD_OPERATORS_RESTAURANT_FILTER_MAP,
    FIELD_OPERATORS_REVIEW_SUBMIT_MAP,
    FIELD_OPERATORS_SEARCH_RESTAURANT_MAP,
    FIELD_OPERATORS_VIEW_RESTAURANT_MAP,
    VISIBLE_FIELD_QUICK_REORDER,
    VISIBLE_FIELDS_DELETE_RESTAURANT_REVIEW,
    VISIBLE_FIELDS_MENU_ITEM_DETAIL,
    VISIBLE_FIELDS_RESTAURANT_DETAIL,
    VISIBLE_FIELDS_VIEW_RESTAURANT_DETAIL,
)
from .data_utils import fetch_data


def _format_price_for_ui(v):
    if v is None:
        return None
    # If already formatted like "$54.70"
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("$"):
            s = s[1:].strip()
        try:
            return f"${float(s):.2f}"
        except ValueError:
            return v  # fallback: keep original string
    if isinstance(v, int | float):
        return f"${float(v):.2f}"
    return v


def _build_data_extraction_result(
    selected_item: dict[str, Any],
    visible_fields: list[str],
    *,
    verify_field: str | None = None,
    question_fields_override: list[str] | None = None,
) -> dict[str, Any] | None:
    """Build constraints + question_fields_and_values for data_extraction_only; returns None on validation failure.

    When verify_field is provided, it is used as the verify field (fixed). Otherwise, verify field is chosen randomly
    from the available visible fields.

    When question_fields_override is provided and non-empty, those fields (that exist and have values) are used
    as the fixed question fields. The verify field is verify_field if it is provided and lies among the remaining
    visible fields; otherwise it is chosen randomly from the remaining available fields.
    If, apart from the verify field and the fixed question fields, there are 2 or more visible fields left,
    a random subset of those is added to the question fields.
    """
    available_fields = [f for f in visible_fields if selected_item.get(f) is not None]
    if len(available_fields) < 2:
        return None

    question_fields: list[str]
    chosen_verify_field: str

    if question_fields_override:
        question_fields = [f for f in question_fields_override if f in available_fields and selected_item.get(f) is not None]
        if question_fields:
            remaining = [f for f in available_fields if f not in question_fields]
            if not remaining:
                return None
            chosen_verify_field = verify_field if verify_field is not None and verify_field in remaining else random.choice(remaining)
            remaining_for_extra = [f for f in available_fields if f != chosen_verify_field and f not in question_fields]
            if len(remaining_for_extra) >= 2:
                num_extra = random.randint(1, len(remaining_for_extra))
                question_fields = question_fields + random.sample(remaining_for_extra, num_extra)
        else:
            question_fields = []
            chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
    else:
        chosen_verify_field = verify_field if verify_field is not None else random.choice(available_fields)
        question_fields = []

    if chosen_verify_field not in available_fields:
        return None
    verify_value = selected_item.get(chosen_verify_field)
    if verify_value is None:
        return None

    if question_fields:
        question_candidates = question_fields
    else:
        question_candidates = [f for f in available_fields if f != chosen_verify_field]
        if not question_candidates:
            return None
        num_question_fields = 1 if len(question_candidates) == 1 else 2
        question_candidates = random.sample(question_candidates, num_question_fields)

    question_fields_and_values: dict[str, Any] = {}
    for qf in question_candidates:
        val = selected_item.get(qf)
        if val is not None:
            question_fields_and_values[qf] = val
    if not question_fields_and_values:
        return None

    constraints = [create_constraint_dict(chosen_verify_field, ComparisonOperator.EQUALS, verify_value)]
    return {
        "constraints": constraints,
        "question_fields_and_values": question_fields_and_values,
    }


def _extract_entity_dataset(dataset: Any, entity_type: str) -> list[dict[str, Any]] | None:
    if dataset is None:
        return None
    if isinstance(dataset, list):
        return dataset
    if isinstance(dataset, dict):
        value = dataset.get(entity_type)
        if isinstance(value, list):
            return value
    return None


async def _ensure_restaurant_dataset(
    task_url: str | None = None,
    dataset: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Extract restaurant data from the pre-loaded dataset, or fetch from server if not available."""
    if isinstance(dataset, list):
        return dataset

    # Fetch data if dataset is not provided or is empty
    if dataset is None or dataset == {}:
        seed = get_seed_from_url(task_url)
        restaurants = await fetch_data(seed_value=seed)
        dataset = {"restaurants": restaurants}

    if dataset and "restaurants" in dataset:
        return dataset["restaurants"]
    return []


def _generate_constraint_value(operator: ComparisonOperator, field_value: Any, field: str, dataset: list[dict[str, Any]]) -> Any:
    value = None

    if operator == ComparisonOperator.EQUALS:
        return field_value

    elif operator == ComparisonOperator.NOT_EQUALS:
        # Only consider entries that actually include the field to avoid KeyError
        valid = [v.get(field) for v in dataset if isinstance(v, dict) and field in v and v.get(field) != field_value]
        valid = [x for x in valid if x is not None]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.CONTAINS and isinstance(field_value, str):
        if len(field_value) > 2:
            start = random.randint(0, max(0, len(field_value) - 2))
            end = random.randint(start + 1, len(field_value))
            return field_value[start:end]
        return field_value

    elif operator == ComparisonOperator.NOT_CONTAINS and isinstance(field_value, str):
        valid = [v.get(field) for v in dataset if isinstance(v, dict) and field in v and isinstance(v.get(field), str) and field_value not in v.get(field, "")]
        valid = [x for x in valid if x is not None]
        return random.choice(valid) if valid else None

    elif operator == ComparisonOperator.IN_LIST:
        # Use get() and guard for missing fields to avoid KeyError
        all_values = list({v.get(field) for v in dataset if isinstance(v, dict) and field in v and v.get(field) is not None})
        if not all_values:
            return [field_value]
        random.shuffle(all_values)
        subset = random.sample(all_values, min(2, len(all_values)))
        if field_value not in subset:
            subset.append(field_value)
        return list(set(subset))

    elif operator == ComparisonOperator.NOT_IN_LIST:
        # Use get() and guard for missing fields to avoid KeyError
        all_values = list({v.get(field) for v in dataset if isinstance(v, dict) and field in v and v.get(field) is not None})
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
            if field == "rating":
                min_val, max_val = 0.0, 5.0
                if operator == ComparisonOperator.GREATER_THAN:
                    if base > min_val:
                        min_dataset = min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                        return round(random.uniform(min_dataset, max(base - 0.5, min_dataset)), 2)
                    else:
                        return min((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=min_val)
                elif operator == ComparisonOperator.LESS_THAN:
                    if base < max_val:
                        max_dataset = max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                        return round(random.uniform(min(base + 0.1, max_dataset), max_dataset), 2)
                    else:
                        return max((v.get(field) for v in dataset if isinstance(v.get(field), int | float)), default=max_val)
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return round(base, 2)
            else:
                # Generic numeric logic
                delta = random.uniform(0.5, 2.0) if isinstance(base, float) else random.randint(1, 5)
                if operator == ComparisonOperator.GREATER_THAN:
                    return round(base - delta, 2)
                elif operator == ComparisonOperator.LESS_THAN:
                    return round(base + delta, 2)
                elif operator in {ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL}:
                    return base
    return value


async def generate_search_restaurant_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected = random.choice(restaurants)
        result = _build_data_extraction_result(selected, VISIBLE_FIELDS_RESTAURANT_DETAIL, question_fields_override=["name"])
        return result if result is not None else []

    constraints_list: list[dict[str, Any]] = []

    data_items = await _ensure_restaurant_dataset(task_url, dataset)
    search_terms = []
    for item in data_items:
        if item.get("name"):
            search_terms.append(item["name"])
        if item.get("cuisine"):
            search_terms.append(item["cuisine"])
        for menu_item in item.get("menu", []):
            if menu_item.get("name"):
                search_terms.append(menu_item["name"])

    if not search_terms:
        return constraints_list

    query = random.choice(search_terms)
    field = "query"
    allowed_ops = FIELD_OPERATORS_SEARCH_RESTAURANT_MAP.get(field, [])
    if not allowed_ops:
        return constraints_list
    operator = ComparisonOperator(random.choice(allowed_ops))

    value = _generate_constraint_value(operator, query, field, [{"query": t} for t in search_terms])

    if value is not None:
        constraint = create_constraint_dict(field, operator, value)
        constraints_list.append(constraint)

    return constraints_list


async def __generate_view_restaurant_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list = []
    restaurant_data = await _ensure_restaurant_dataset(task_url, dataset)
    fields = ["name", "cuisine", "rating", "description"]
    num_constraints = random.randint(2, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    restaurant = random.choice(restaurant_data)

    for field in selected_fields:
        field_value = restaurant.get(field)
        allowed_ops = FIELD_OPERATORS_VIEW_RESTAURANT_MAP.get(field, [])
        if not allowed_ops:
            return []
        operator = ComparisonOperator(random.choice(allowed_ops))

        value = _generate_constraint_value(operator, field_value, field, restaurant_data)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list, restaurant


async def generate_view_restaurant_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected = random.choice(restaurants)
        result = _build_data_extraction_result(selected, VISIBLE_FIELDS_VIEW_RESTAURANT_DETAIL, question_fields_override=["name"])
        return result if result is not None else []

    constraints_list, _ = await __generate_view_restaurant_constraints(task_url=task_url, dataset=dataset)

    return constraints_list


async def _get_menu_items(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    menu_items = []
    restaurant_data = await _ensure_restaurant_dataset(task_url, dataset)
    for restaurant in restaurant_data:
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
            "description": menu_item.get("description"),
            "size": menu_item.get("size"),
            "quantity": random.randint(1, 5),
            "restaurant": restaurant.get("name"),
        }
        for menu_item in restaurant.get("menu", [])
    ]


async def __generate_add_to_cart_modal_open_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    constraints_list = []
    restaurant_data = await _ensure_restaurant_dataset(task_url, dataset)
    if not restaurant_data:
        return [], {}
    restaurant = random.choice(restaurant_data)
    menu_items = _get_menu_items_for_restaurant(restaurant)
    if not menu_items:
        return [], {}
    item = random.choice(menu_items)
    menu_dataset = await _get_menu_items(task_url=task_url, dataset=restaurant_data)
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
        if field == "item" and operator == ComparisonOperator.CONTAINS:
            retries = 0
            value = _generate_constraint_value(operator, field_value, field, dataset=menu_dataset)
            while value is not None and value.strip() == "&" and retries < 5:
                value = _generate_constraint_value(operator, field_value, field, dataset=menu_dataset)
                retries += 1
            if value is not None and value.strip() == "&":
                value = None
        else:
            value = _generate_constraint_value(operator, field_value, field, dataset=menu_dataset)

        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list, item


async def generate_add_to_cart_modal_open_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected_restaurant = random.choice(restaurants)
        menu_items = _get_menu_items_for_restaurant(selected_restaurant)
        if not menu_items:
            return []
        item = random.choice(menu_items)
        raw_price = item.get("price", "")
        formatted_price = _format_price_for_ui(raw_price)

        selected_item = {
            "restaurant_name": selected_restaurant.get("name"),
            "item_name": item.get("item"),
            "price": formatted_price,
            "item_description": item.get("description"),
            "cuisine": selected_restaurant.get("cuisine"),
        }
        # Pick verify_field randomly
        all_menu_fields = ["item_name", "price", "item_description"]
        available_verify_fields = [f for f in all_menu_fields if selected_item.get(f) is not None]
        if not available_verify_fields:
            return []
        verify_field = random.choice(available_verify_fields)
        # Pick question fields that do NOT include verify_field
        remaining_fields = [f for f in all_menu_fields if f != verify_field and selected_item.get(f) is not None]
        num_question_fields = random.randint(1, len(remaining_fields)) if remaining_fields else 0
        question_fields_override = random.sample(remaining_fields, num_question_fields) if num_question_fields else []
        question_fields_override.extend(["restaurant_name"])
        result = _build_data_extraction_result(selected_item, VISIBLE_FIELDS_MENU_ITEM_DETAIL, question_fields_override=question_fields_override, verify_field=verify_field)
        return result if result is not None else []

    constraints_list, _ = await __generate_add_to_cart_modal_open_constraints(task_url=task_url, dataset=dataset)
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
        return random.randint(3, 9)
    elif operator == ComparisonOperator.LESS_THAN:
        # Must be at most 9 (since can't be 1)
        return random.randint(2, 9)
    elif operator == ComparisonOperator.GREATER_EQUAL or operator == ComparisonOperator.LESS_EQUAL:
        return random.randint(2, 10)
    else:
        return random.randint(2, 10)


async def __generate_add_to_cart_options_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    model_constraints, _ = await __generate_add_to_cart_modal_open_constraints(task_url, dataset=dataset)
    field = "quantity"

    allowed_ops = FIELD_OPERATORS_INCREMENT_QUANTITY_MAP.get(field, [])
    if not allowed_ops:
        return []
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = _get_new_quantity_value(operator)
    constraints_list.append(create_constraint_dict(field, operator, field_value))
    constraints_list.extend(model_constraints)
    return constraints_list


async def generate_increment_item_restaurant_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict]:
    constraints_list = await __generate_add_to_cart_options_constraints(task_url, dataset=dataset)
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


async def generate_delete_review_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected_restaurant = random.choice(restaurants)
        review_rows = __get_delete_review_fields([selected_restaurant])
        if not review_rows:
            return []
        selected = random.choice(review_rows)

        # Normalize rating representation
        rating = selected.get("review_rating")
        if rating is not None:
            try:
                # Convert string to float if possible
                rating_float = float(rating)
                # If it is an integer (e.g., 1.0, 5.0), keep decimal format
                if rating_float.is_integer():
                    rating_float = float(int(rating_float))  # ensures 5 -> 5.0
                selected["review_rating"] = rating_float
            except ValueError:
                # If rating cannot be converted to float, keep original
                pass

        # Pick verify_field randomly
        all_review_fields = ["author", "review_rating", "comment", "date"]
        verify_field = random.choice(all_review_fields)
        # Pick question fields that do NOT include verify_field
        remaining_fields = [f for f in all_review_fields if f != verify_field]
        num_question_fields = random.randint(1, len(remaining_fields))  # at least 1
        question_fields_override = random.sample(remaining_fields, num_question_fields)
        question_fields_override.extend(["name"])

        result = _build_data_extraction_result(selected, VISIBLE_FIELDS_DELETE_RESTAURANT_REVIEW, question_fields_override=question_fields_override, verify_field=verify_field)
        return result if result is not None else []

    constraints_list, restaurant = await __generate_view_restaurant_constraints(task_url, dataset=dataset)
    delete_review_dict = __get_delete_review_fields([restaurant])
    fields = ["author", "review_rating", "comment"]  # , "date"]
    num_constraints = random.randint(1, len(fields))
    selected_fields = random.sample(fields, num_constraints)
    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_DELETE_REVIEW_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        # Use get() to avoid KeyError when some entries lack the field
        field_values = [d.get(field) for d in delete_review_dict if d.get(field) is not None]
        if not field_values:
            continue
        field_value = random.choice(field_values)
        dataset = [{field: d.get(field)} for d in delete_review_dict if d.get(field) is not None]
        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


async def generate_add_to_cart_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected_restaurant = random.choice(restaurants)
        menu_items = _get_menu_items_for_restaurant(selected_restaurant)
        if not menu_items:
            return []
        item = random.choice(menu_items)
        raw_price = item.get("price", "")
        formatted_price = _format_price_for_ui(raw_price)

        selected_item = {
            "restaurant_name": selected_restaurant.get("name"),
            "item_name": item.get("item"),
            "price": formatted_price,
            "item_description": item.get("description"),
            "cuisine": selected_restaurant.get("cuisine"),
        }
        # Pick verify_field randomly
        all_menu_fields = ["item_name", "price", "item_description"]
        available_verify_fields = [f for f in all_menu_fields if selected_item.get(f) is not None]
        if not available_verify_fields:
            return []
        verify_field = random.choice(available_verify_fields)
        # Pick question fields that do NOT include verify_field
        remaining_fields = [f for f in all_menu_fields if f != verify_field and selected_item.get(f) is not None]
        num_question_fields = random.randint(1, len(remaining_fields)) if remaining_fields else 0
        question_fields_override = random.sample(remaining_fields, num_question_fields) if num_question_fields else []
        question_fields_override.extend(["restaurant_name"])
        result = _build_data_extraction_result(selected_item, VISIBLE_FIELDS_MENU_ITEM_DETAIL, question_fields_override=question_fields_override, verify_field=verify_field)
        return result if result is not None else []

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
    common_add_to_cart_constraints = await __generate_add_to_cart_options_constraints(task_url, dataset=dataset)
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


async def generate_dropoff_option_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict]:
    constraints_list = await __generate_add_to_cart_options_constraints(task_url, dataset=dataset)
    dropoff_options = ["Leave it at my door", "Hand it to me", "Meet outside", "Meet in the lobby", "Call upon arrival", "Text when arriving"]

    field = "delivery_preference"
    allowed_ops = FIELD_OPERATORS_DROPOFF_OPTION_MAP[field]
    operator = ComparisonOperator(random.choice(allowed_ops))
    field_value = random.choice(dropoff_options)
    dataset = [{"delivery_preference": opt} for opt in dropoff_options]
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


async def generate_address_added_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict]:
    constraints_list = []
    add_to_cart_constraint = await generate_add_to_cart_constraints(task_url, dataset=dataset)

    field = "address"
    operator = ComparisonOperator(random.choice(FIELD_OPERATORS_ADDRESS_ADDED_MAP[field]))
    field_value = random.choice(ADDRESSES)
    dataset = _get_address_dataset()
    value = _generate_constraint_value(operator, field_value, field, dataset)
    constraints_list.append(create_constraint_dict(field, operator, value))
    constraints_list.extend(add_to_cart_constraint)
    return constraints_list


async def generate_place_order_constraints(task_url: str | None = None) -> list[dict]:
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
        dataset = []
        if field == "username":
            dataset = [{"username": v} for v in names if v is not None]
        elif field == "phone":
            dataset = [{"phone": v} for v in phones if v is not None]
        elif field == "address":
            dataset = _get_address_dataset()
        elif field == "mode":
            dataset = [{"mode": v} for v in ["delivery", "pickup"]]

        value = _generate_constraint_value(operator, field_value, field, dataset)
        if value:
            constraints.append(create_constraint_dict(field, operator, value))
    add_to_cart_constraint = await generate_add_to_cart_constraints(task_url)
    constraints.extend(add_to_cart_constraint)
    return constraints


async def generate_restaurant_filter_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected = random.choice(restaurants)
        # Pick verify_field randomly from 'cuisine' or 'rating'
        verify_field = random.choice(["cuisine", "rating"])
        result = _build_data_extraction_result(selected, VISIBLE_FIELDS_RESTAURANT_DETAIL, question_fields_override=["name"], verify_field=verify_field)
        return result if result is not None else []

    constraints_list: list[dict[str, Any]] = []
    restaurants = await _ensure_restaurant_dataset(task_url, dataset)
    if not restaurants:
        return constraints_list
    restaurant = random.choice(restaurants)
    # candidate_fields = ["cuisine", "rating"]
    candidate_fields = list(FIELD_OPERATORS_RESTAURANT_FILTER_MAP.keys())
    num_constraints = random.randint(1, len(candidate_fields))
    for field in random.sample(candidate_fields, num_constraints):
        allowed_ops = FIELD_OPERATORS_RESTAURANT_FILTER_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        field_value = restaurant.get(field)
        value = _generate_constraint_value(operator, field_value, field, restaurants)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


async def generate_quick_reorder_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        restaurants = await _ensure_restaurant_dataset(task_url, dataset)
        if not restaurants:
            return []
        selected = random.choice(restaurants)
        result = _build_data_extraction_result(selected, VISIBLE_FIELD_QUICK_REORDER, question_fields_override=["name"])
        return result if result is not None else []

    constraints_list: list[dict[str, Any]] = []
    restaurants = await _ensure_restaurant_dataset(task_url, dataset)
    if not restaurants:
        return constraints_list
    restaurant = random.choice(restaurants)
    menu = restaurant.get("menu", [])
    if not menu:
        return constraints_list
    menu_item = random.choice(menu)

    # Build dataset of menu items from all restaurants for "item" field
    all_menu_items = []
    for r in restaurants:
        r_menu = r.get("menu", [])
        for item in r_menu:
            if item.get("name"):
                all_menu_items.append({"item": item.get("name")})

    for field in ["item", "restaurant"]:
        allowed_ops = FIELD_OPERATORS_QUICK_REORDER_MAP.get(field, [])
        if not allowed_ops:
            continue
        operator = ComparisonOperator(random.choice(allowed_ops))
        value_source = menu_item.get("name") if field == "item" else restaurant.get("name")
        # Use menu items dataset for "item" field, and normalized restaurant-name dataset for "restaurant" field
        if field == "item":
            field_dataset = all_menu_items
        elif field == "restaurant":
            field_dataset = [{"restaurant": r.get("name")} for r in restaurants if r.get("name")]
        else:
            field_dataset = restaurants
        value = _generate_constraint_value(operator, value_source, field, field_dataset)
        if value is not None:
            constraints_list.append(create_constraint_dict(field, operator, value))
    return constraints_list


async def generate_review_submitted_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    constraint_list = []
    restaurants = await _ensure_restaurant_dataset(task_url, dataset)
    if not restaurants:
        return []
    NAMES = ["Alex", "John", "Michael", "Sarah", "Emily", "David", "Sophia", "Daniel", "Olivia", "James", "Emma", "Liam", "Ava", "Noah", "Mia"]
    COMMENTS = [
        "Had a wonderful stay! The staff was polite and the rooms were spotless.",
        "Comfortable stay overall, but the breakfast could be improved.",
        "Amazing experience! Loved the view from my balcony and the service was top-notch.",
        "Good hotel for the price. Check-in was smooth and quick.",
        "Room was spacious and clean, but the wifi was a bit slow.",
        "Excellent hospitality! Will definitely visit again.",
        "The location was perfect—close to all major attractions.",
        "Nice stay, but the AC was slightly noisy at night.",
        "Super friendly staff and delicious food at the hotel restaurant.",
        "Enjoyed my stay! The bed was very comfortable and everything was well maintained.",
        "Hotel was clean and cozy, though parking was limited.",
        "Loved the rooftop pool! One of the best experiences.",
        "Great value for money. Staff helped us with local travel tips.",
        "Room service was quick and efficient. Highly satisfied.",
        "Beautiful interiors and relaxing environment—highly recommended!",
    ]
    RATINGS = [1, 2, 3, 4, 5]
    NAME_DATA = [{"name": n} for n in NAMES]
    COMMENT_DATA = [{"comment": c} for c in COMMENTS]
    restaurant = random.choice(restaurants)
    possible_fields = list(FIELD_OPERATORS_REVIEW_SUBMIT_MAP.keys())
    selected_fields = random.sample(possible_fields, random.randint(1, len(possible_fields)))
    field_mapping = {
        "restaurant_name": "name",
        "restaurant_rating": "rating",
        "cuisine": "cuisine",
    }

    for field in selected_fields:
        allowed_ops = FIELD_OPERATORS_REVIEW_SUBMIT_MAP.get(field, [])
        op = ComparisonOperator(random.choice(allowed_ops))
        if field == "author":
            field_value = random.choice(NAMES)
            value = _generate_constraint_value(op, field_value, field, NAME_DATA)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        elif field == "comment":
            field_value = random.choice(COMMENTS)
            value = _generate_constraint_value(op, field_value, field, COMMENT_DATA)
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)
        elif field == "rating":
            field_value = random.choice(RATINGS)
            value = _generate_constraint_value(op, field_value, field, [{"rating": r} for r in RATINGS])
            constraint = create_constraint_dict(field, op, value)
            constraint_list.append(constraint)

        else:
            field_value = restaurant.get(field_mapping[field])
            value = _generate_constraint_value(op, field_value, field, restaurants)
            constraint = create_constraint_dict(field_mapping[field], op, value)
            constraint_list.append(constraint)

    return constraint_list


async def generate_delivery_priority_constraints(task_url: str | None = None, dataset: list[dict[str, Any]] | None = None, test_types: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
    if test_types == "data_extraction_only":
        _, item = await __generate_add_to_cart_modal_open_constraints(task_url=task_url, dataset=dataset)
        if not item:
            return []
        selected = {**item, "priority": random.choice(["normal", "priority"])}
        result = _build_data_extraction_result(selected, [*VISIBLE_FIELDS_MENU_ITEM_DETAIL, "priority"], question_fields_override=["item"])
        return result if result is not None else []

    constraints = []
    constraints = await generate_add_to_cart_constraints(task_url, dataset)
    field = "priority"
    priority_value = random.choice(["normal", "priority"])
    operator = ComparisonOperator(random.choice(["equals", "not_equals"]))
    constraint = create_constraint_dict(field, operator, priority_value)
    constraints.append(constraint)

    return constraints
