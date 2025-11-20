import contextlib
import random
import traceback
from typing import Any

from loguru import logger

from autoppia_iwa.src.demo_webs.projects.data_provider import extract_v2_seed_from_url, load_dataset_data

from ..criterion_helper import ComparisonOperator
from ..shared_utils import create_constraint_dict, parse_price
from .data import FIELD_OPERATORS_MAP_PRODUCTS


async def _get_data(seed_value: int | None = None, count: int = 100) -> list[dict]:
    from .main import FRONTEND_PORT_INDEX, omnizone_project

    project_key = f"web_{FRONTEND_PORT_INDEX + 1}_{omnizone_project.id}"

    items = await load_dataset_data(
        backend_url=omnizone_project.backend_url,
        project_key=project_key,
        entity_type="products",
        seed_value=seed_value if seed_value is not None else 1,
        limit=count,
    )
    if items:
        return items
    return []


def generate_constraint_value(field: str, operator: ComparisonOperator, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]] | None = None) -> Any:
    """
    Generates the value part for a single constraint based on field, operator, and data.
    Returns None if a value cannot be generated for the given criteria combination.
    """
    source_value = product_data_source.get(field)
    if field == "price":
        source_value = parse_price(source_value)
    generated_value = None

    value_pool = []
    # Caller should pass all_products_data to avoid await inside
    if all_products_data is None:
        return None
    try:
        if field in ["id", "title", "category", "brand", "affiliation", "currency", "coupon"]:
            value_pool = [p.get(field) for p in all_products_data if isinstance(p.get(field), str) and p.get(field) is not None]
        elif field in ["price", "rating", "quantity", "items", "total_items", "total_amount", "tax", "shipping", "order_total", "previous_quantity", "new_quantity", "value"]:
            # For numeric fields, pool from relevant source (all products for item attributes, source data for totals)
            pool_source = all_products_data if field in ["price", "rating"] else [product_data_source]
            for item in pool_source:
                val = item.get(field)
                if field in ["price", "value", "total_amount", "tax", "shipping", "order_total", "rating"]:
                    # Ensure input to parse_price is a string
                    parsed_val = parse_price(str(val)) if val is not None else None
                    if parsed_val is not None:
                        value_pool.append(parsed_val)
                elif val is not None:
                    with contextlib.suppress(ValueError, TypeError):
                        value_pool.append(float(val))

            if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"]:
                # Ensure integers for quantity/count fields
                value_pool = [int(v) for v in value_pool if v is not None]
                if source_value is not None:
                    try:
                        # Also cast source value to int if it's a quantity field
                        source_value = int(source_value)
                    except (ValueError, TypeError):
                        source_value = None  # Invalid source value for int field
        elif field == "query":
            all_terms_list = []
            for p in all_products_data:
                all_terms_list.extend(str(p.get("title", "")).split())
                category = p.get("category", "")
                if isinstance(category, str) and category:
                    all_terms_list.append(category)
                brand = p.get("brand", "")
                if isinstance(brand, str) and brand:
                    all_terms_list.append(brand)
            value_pool = list(set(term for term in all_terms_list if term and isinstance(term, str)))

    except Exception as e:
        logger.error(f"Error building value pool for field '{field}': {e}")
        traceback.print_exc()
        return None

    valid_pool = [v for v in value_pool if v is not None]

    if operator == ComparisonOperator.EQUALS:
        if source_value is not None:
            generated_value = source_value
        elif valid_pool:
            generated_value = random.choice(valid_pool)
        else:
            return None

    elif operator in [ComparisonOperator.NOT_EQUALS]:
        if source_value is not None:
            other_values = list(set(v for v in valid_pool if v != source_value))
            # Return None if no other value can be found
            generated_value = random.choice(other_values) if other_values else None
        elif valid_pool:
            generated_value = random.choice(valid_pool)
        else:
            return None  # Cannot generate a meaningful NOT_EQUALS constraint

    elif operator in [ComparisonOperator.GREATER_THAN, ComparisonOperator.LESS_THAN, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
        if source_value is not None:
            try:
                num_source_value = float(source_value)
            except (ValueError, TypeError):
                return None

            if num_source_value > 10:
                delta = random.uniform(1, min(10, num_source_value / 2))
            elif num_source_value > 1:
                delta = random.uniform(0.1, min(1, num_source_value / 2))
            else:
                delta = random.uniform(0.01, max(0.05, num_source_value / 2))

            if operator == ComparisonOperator.GREATER_THAN:
                generated_value = max(0.01, num_source_value - delta)
            elif operator == ComparisonOperator.LESS_THAN:
                generated_value = num_source_value + delta
            elif operator in [ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]:
                generated_value = num_source_value

            # Cast to int for integer fields
            generated_value = max(1, round(generated_value)) if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"] else round(generated_value, 2)
        else:
            # If no source_value, try to pick from pool or return None
            if valid_pool and all(isinstance(v, int | float) for v in valid_pool):
                generated_value = random.choice([float(v) for v in valid_pool])
                generated_value = max(1, round(generated_value)) if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"] else round(generated_value, 2)
            else:
                return None  # Cannot generate numeric comparison without a numeric base

    elif operator in [ComparisonOperator.CONTAINS, ComparisonOperator.NOT_CONTAINS]:
        # Prioritize string source_value, then string from pool
        string_source = None
        if isinstance(source_value, str):
            string_source = source_value
        elif valid_pool:
            string_source = random.choice([v for v in valid_pool if isinstance(v, str) and len(v) > 0])  # Ensure non-empty string

        if string_source is None:
            return None  # Cannot generate CONTAINS/NOT_CONTAINS without a string base

        if operator == ComparisonOperator.CONTAINS:
            if len(string_source) > 2:
                # Ensure substring has at least 2 characters unless string_source is very short
                min_len = min(2, len(string_source))
                start = random.randint(0, len(string_source) - min_len)
                end = random.randint(start + min_len, len(string_source))
                generated_value = string_source[start:end]
            else:
                # Use whole string if too short for meaningful substring
                generated_value = string_source
            if not generated_value:  # Fallback if empty string
                generated_value = "keyword"

        elif operator == ComparisonOperator.NOT_CONTAINS:
            generated_value = string_source + "XYZ" + str(random.randint(100, 999))  # Ensure it won't contain source

    elif operator == ComparisonOperator.IN_LIST:
        if valid_pool:
            # Ensure the list contains random elements, and if source_value exists, include it
            num_elements = random.randint(1, min(3, len(valid_pool)))
            list_values = random.sample(valid_pool, num_elements)
            if source_value is not None and source_value not in list_values:
                list_values.append(source_value)
                random.shuffle(list_values)
            generated_value = list_values
        else:
            return None

    else:
        logger.warning(f"Operator {operator} not explicitly handled for field '{field}' in _generate_constraint_value")
        generated_value = source_value if source_value is not None else (random.choice(valid_pool) if valid_pool else None)
        if generated_value is None:
            logger.warning(f"Could not generate value for field '{field}' with operator '{operator}' using fallback.")
            return None

    return generated_value


async def generate_autozone_products_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    fields = ["title", "category", "brand", "rating", "price"]
    v2_seed = extract_v2_seed_from_url(task_url) if task_url else None
    data_items = await _get_data(seed_value=v2_seed)
    if not data_items:
        return []

    selected_criteria_fields = random.sample(fields, random.randint(1, min(3, len(fields))))
    product = random.choice(data_items)

    for criteria_field in selected_criteria_fields:
        allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[criteria_field]
        op = ComparisonOperator(random.choice(allowed_operators))
        constraint_value = generate_constraint_value(criteria_field, op, product, all_products_data=data_items)
        if constraint_value is not None:
            constraint_dict = create_constraint_dict(criteria_field, op, constraint_value)
            constraints_list.append(constraint_dict)
        else:
            logger.warning(f"Could not select operator for criteria field '{criteria_field}'. Skipping constraint generation.")

    return constraints_list


async def generate_search_query_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    query_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.CONTAINS,
    ]

    op = random.choice(query_operators)
    # Pass a mock product_data_source even if not directly used, as generate_constraint_value expects it
    v2_seed = extract_v2_seed_from_url(task_url) if task_url else None
    data_items = await _get_data(seed_value=v2_seed)
    constraint_value = generate_constraint_value("query", op, {}, all_products_data=data_items)
    if constraint_value is not None:
        constraints_list.append(create_constraint_dict("query", op, constraint_value))

    # Fallback
    return constraints_list if constraints_list else [create_constraint_dict("query", ComparisonOperator.CONTAINS, "products")]


async def generate_quantity_change_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    constraints_list = []
    v2_seed = extract_v2_seed_from_url(task_url) if task_url else None
    data_items = await _get_data(seed_value=v2_seed)
    if not data_items:
        return []

    product = random.choice(data_items)
    product_key = "title"

    allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
    op = ComparisonOperator(random.choice(allowed_operators))
    constraint_value = generate_constraint_value(product_key, op, product, all_products_data=data_items)
    if constraint_value is not None:
        constraints_list.append(create_constraint_dict(product_key, op, constraint_value))

    quantity_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_THAN,
    ]
    op = random.choice(quantity_operators)
    threshold = None
    if op == ComparisonOperator.EQUALS:
        threshold = random.randint(1, 10)

    elif op == ComparisonOperator.GREATER_EQUAL:
        # choose a threshold such that it's ≤ 9 to allow room for GREATER values
        threshold = random.randint(1, 9)

    elif op == ComparisonOperator.LESS_EQUAL:
        # choose a threshold ≥ 2 to allow some values below it
        threshold = random.randint(2, 10)

    elif op == ComparisonOperator.GREATER_THAN:
        # choose a threshold < 10
        threshold = random.randint(1, 9)

    elif op == ComparisonOperator.LESS_THAN:
        # choose a threshold > 1
        threshold = random.randint(2, 10)

    value = threshold

    # Ensure final value is always in 1-10 range
    if value is not None and 1 <= value <= 10:
        constraints_list.append(create_constraint_dict("new_quantity", op, value))
    else:
        logger.warning(f"Invalid quantity generated: {value} with operator {op}")

    return constraints_list


async def generate_checkout_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """Generate randomized checkout constraints based on product data."""
    constraints: list[dict[str, Any]] = []
    field = "total_amount"
    operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]
    v2_seed = extract_v2_seed_from_url(task_url) if task_url else None
    data_items = await _get_data(seed_value=v2_seed)
    if not data_items:
        return constraints

    try:
        product = random.choice(data_items)
        price_str = product["price"]
        price = parse_price(price_str)

        operator = random.choice(operators)
        value = generate_constraint_value(field, operator, {field: price}, data_items)

        if value is not None:
            constraints.append(create_constraint_dict(field, operator, value))

    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.warning(f"Failed to generate checkout constraint: {e}")

    return constraints


async def generate_order_completed_constraints(task_url: str | None = None) -> list[dict[str, Any]]:
    """
    Generate constraints for the ORDER_COMPLETED event,
    focused on the `items` list with ProductSummary fields like title, id, and quantity.
    """
    constraints_list = []
    v2_seed = extract_v2_seed_from_url(task_url) if task_url else None
    data_items = await _get_data(seed_value=v2_seed)
    if not data_items:
        return []

    product = random.choice(data_items)

    # Choose one or more fields from ProductSummary to apply as criteria
    product_fields = ["title", "quantity"]

    for field in product_fields:
        # Map field to appropriate operators
        allowed_ops = FIELD_OPERATORS_MAP_PRODUCTS.get(field, [ComparisonOperator.EQUALS])
        op = ComparisonOperator(random.choice(allowed_ops))

        val = generate_constraint_value(field, op, product, all_products_data=data_items)
        if val is not None:
            constraints_list.append(create_constraint_dict(field, op, val))

    return constraints_list


def generate_carousel_scroll_constraints() -> list[dict[str, Any]]:
    constraints_list = []

    selected_fields = random.choice([["direction"], ["title"], ["direction", "title"]])

    direction_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]
    title_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]

    for field in selected_fields:
        if field == "direction":
            op = random.choice(direction_operators)
            constraint_value = random.choice(["LEFT", "RIGHT"])
        elif field == "title":
            op = random.choice(title_operators)
            title = random.choice(["Technology", "Home", "Electronics", "Kitchen", "Fitness"])
            constraint_value = f"Top Sellers In {title}"
        else:
            continue

        constraints_list.append(create_constraint_dict(field, op, constraint_value))

    return constraints_list
