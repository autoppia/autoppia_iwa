import contextlib
import random
import traceback
from typing import Any

from loguru import logger

from ..criterion_helper import ComparisonOperator
from ..shared_data import FIELD_OPERATORS_MAP_PRODUCTS
from ..shared_utils import create_constraint_dict, parse_price
from .data import PRODUCTS_DATA


def generate_constraint_value(field: str, operator: ComparisonOperator, product_data_source: dict[str, Any], all_products_data: list[dict[str, Any]] = PRODUCTS_DATA) -> Any:
    """
    Generates the value part for a single constraint based on field, operator, and data.
    Returns None if a value cannot be generated for the given criteria combination.
    """
    source_value = product_data_source.get(field)
    generated_value = None

    value_pool = []
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
                value_pool = [int(v) for v in value_pool if v is not None]  # Ensure integers for quantity/count fields
                if source_value is not None:
                    try:
                        source_value = int(source_value)  # Also cast source value to int if it's a quantity field
                    except (ValueError, TypeError):
                        source_value = None  # Invalid source value for int field
        elif field == "direction":
            value_pool = ["LEFT", "RIGHT"]
        elif field == "title":
            value_pool = ["Featured Products", "Best Sellers", "Electronics", "Kitchenware"]
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
            generated_value = random.choice(other_values) if other_values else None  # Return None if no other value can be found
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
            numeric_pool = [float(v) for v in valid_pool if v is not None]

            if operator == ComparisonOperator.GREATER_THAN:
                candidates = [v for v in numeric_pool if v > num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value + random.randint(1, 5)

            elif operator == ComparisonOperator.LESS_THAN:
                candidates = [v for v in numeric_pool if v < num_source_value]
                generated_value = random.choice(candidates) if candidates else max(0, num_source_value - random.randint(1, 5))

            elif operator == ComparisonOperator.GREATER_EQUAL:
                candidates = [v for v in numeric_pool if v >= num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value
            elif operator == ComparisonOperator.LESS_EQUAL:
                candidates = [v for v in numeric_pool if v <= num_source_value]
                generated_value = random.choice(candidates) if candidates else num_source_value
                if generated_value < 0 and field not in ["rating"]:
                    generated_value = 0

            generated_value = int(generated_value) if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"] else round(generated_value, 2)
        else:
            # If no source_value, try to pick from pool or return None
            if valid_pool and all(isinstance(v, int | float) for v in valid_pool):
                generated_value = random.choice([float(v) for v in valid_pool])
                generated_value = int(generated_value) if field in ["quantity", "items", "total_items", "previous_quantity", "new_quantity"] else round(generated_value, 2)
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
                generated_value = string_source  # Use whole string if too short for meaningful substring
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


def generate_autozone_products_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    mappable_criteria_fields = ["item_name", "item_category", "item_brand", "item_rating", "item_price"]
    criteria_to_product_key = {
        "item_name": "title",
        "item_category": "category",
        "item_brand": "brand",
        "item_rating": "rating",
        "item_price": "price",
    }

    if not PRODUCTS_DATA:  # Handle empty PRODUCTS_DATA early
        return []

    # Determine which criteria fields we can generate constraints for based on PRODUCTS_DATA
    applicable_criteria_fields = [
        cf
        for cf in mappable_criteria_fields
        if criteria_to_product_key[cf] in PRODUCTS_DATA[0]  # Check if product data contains the key
    ]

    if not applicable_criteria_fields:
        return []

    selected_criteria_fields = random.sample(applicable_criteria_fields, random.randint(1, min(3, len(applicable_criteria_fields))))
    product = random.choice(PRODUCTS_DATA)  # Product guaranteed to exist due to earlier check

    for criteria_field in selected_criteria_fields:
        product_key = criteria_to_product_key.get(criteria_field)

        op = None
        if product_key and product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)
            else:
                logger.warning(f"No allowed operators defined for product key '{product_key}' in FIELD_OPERATORS_MAP_PRODUCTS.")
                continue

        if op:
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)
            if constraint_value is not None:
                constraint_dict = create_constraint_dict(criteria_field, op, constraint_value)
                constraints_list.append(constraint_dict)
        else:
            logger.warning(f"Could not select operator for criteria field '{criteria_field}'. Skipping constraint generation.")

    return constraints_list


def generate_search_query_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    query_operators = [ComparisonOperator.EQUALS, ComparisonOperator.CONTAINS]

    if query_operators:
        op = random.choice(query_operators)
        # Pass a mock product_data_source even if not directly used, as generate_constraint_value expects it
        constraint_value = generate_constraint_value("query", op, {}, all_products_data=PRODUCTS_DATA)
        if constraint_value is not None:
            constraints_list.append(create_constraint_dict("query", op, constraint_value))

    return constraints_list if constraints_list else [create_constraint_dict("query", ComparisonOperator.CONTAINS, "products")]  # Fallback


def generate_cart_operation_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    if not PRODUCTS_DATA:
        return []

    product = random.choice(PRODUCTS_DATA)

    item_identification_fields = ["name"]
    criterion_alias_to_product_key = {"name": "title"}

    selected_id_field = random.choice(item_identification_fields)
    product_key = criterion_alias_to_product_key.get(selected_id_field)

    if product_key and product_key in product:
        op = None
        if product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)

        if op:
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)
            if constraint_value is not None:
                constraints_list.append(create_constraint_dict(selected_id_field, op, constraint_value))
        else:
            logger.warning(f"Could not select operator for product key '{product_key}' in cart operation constraints.")
    else:
        return []  # Need at least name or id that maps to product data

    criterion_alias_to_product_key_attributes = {
        "category": "category",
        "brand": "brand",
        "price": "price",
        "rating": "rating",
    }

    # Filter product keys based on presence in the chosen product and allowed operators map
    applicable_product_keys = [pk for pk in criterion_alias_to_product_key_attributes.values() if pk in product and pk in FIELD_OPERATORS_MAP_PRODUCTS]

    selected_product_keys = random.sample(applicable_product_keys, random.randint(0, min(2, len(applicable_product_keys))))

    for product_key in selected_product_keys:
        criterion_alias = next(alias for alias, key in criterion_alias_to_product_key_attributes.items() if key == product_key)

        allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS.get(product_key)
        if not allowed_operators:
            continue

        op_str = random.choice(allowed_operators)
        op = ComparisonOperator(op_str)

        constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)

        if constraint_value is not None:
            constraints_list.append(create_constraint_dict(criterion_alias, op, constraint_value))

    # quantity_operators = [
    #     ComparisonOperator.EQUALS,
    #     ComparisonOperator.GREATER_EQUAL,
    #     ComparisonOperator.LESS_EQUAL,
    # ]
    # if random.random() > 0.3 and quantity_operators:
    #     op = random.choice(quantity_operators)
    #     # Use a more realistic mock source value for quantity
    #     quantity_value = generate_constraint_value("quantity", op, {"quantity": random.randint(1, 5)})
    #     if quantity_value is not None:
    #         constraints_list.append(create_constraint_dict("quantity", op, quantity_value))

    return constraints_list


def generate_quantity_change_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    if not PRODUCTS_DATA:
        return []

    product = random.choice(PRODUCTS_DATA)

    item_identification_fields = ["name"]
    product_key_map = {"name": "title"}

    selected_id_field = random.choice(item_identification_fields)
    product_key = product_key_map.get(selected_id_field)

    if product_key and product_key in product:
        op = None
        if product_key in FIELD_OPERATORS_MAP_PRODUCTS:
            allowed_operators = FIELD_OPERATORS_MAP_PRODUCTS[product_key]
            if allowed_operators:
                op_str = random.choice(allowed_operators)
                op = ComparisonOperator(op_str)
        if op:
            constraint_value = generate_constraint_value(product_key, op, product, all_products_data=PRODUCTS_DATA)
            if constraint_value is not None:
                constraints_list.append(create_constraint_dict(selected_id_field, op, constraint_value))
        else:
            logger.warning(f"Could not select operator for product key '{product_key}' in quantity change constraints.")

    quantity_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_THAN,
    ]

    new_qty = random.randint(2, 9)  # avoid edge-only scenarios for better range
    op = random.choice(quantity_operators)
    constraint_value_new = None

    if op == ComparisonOperator.EQUALS:
        constraint_value_new = new_qty
    elif op == ComparisonOperator.GREATER_EQUAL:
        constraint_value_new = random.randint(1, new_qty)
    elif op == ComparisonOperator.LESS_EQUAL:
        constraint_value_new = random.randint(new_qty, 10)
    elif op == ComparisonOperator.GREATER_THAN:
        constraint_value_new = random.randint(new_qty + 1, 10) if new_qty < 10 else 10
        if constraint_value_new == 10:
            constraint_value_new = random.randint(1, 9)
    elif op == ComparisonOperator.LESS_THAN:
        constraint_value_new = random.randint(1, new_qty - 1) if new_qty > 1 else 1

    if constraint_value_new is not None:
        constraints_list.append(create_constraint_dict("new_quantity", op, constraint_value_new))
    else:
        logger.warning(f"Could not generate valid constraint value for new_quantity with operator {op}.")

    return constraints_list


def generate_checkout_constraints() -> list[dict[str, Any]]:
    """Generate randomized checkout constraints based on product data."""
    constraints: list[dict[str, Any]] = []
    field = "total_amount"
    operators = [ComparisonOperator.EQUALS, ComparisonOperator.GREATER_EQUAL, ComparisonOperator.LESS_EQUAL]

    if not PRODUCTS_DATA:
        return constraints

    try:
        product = random.choice(PRODUCTS_DATA)
        price_str = product["price"]
        price = parse_price(price_str)

        operator = random.choice(operators)
        value = generate_constraint_value(field, operator, {field: price})

        if value is not None:
            constraints.append(create_constraint_dict(field, operator, value))

    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.warning(f"Failed to generate checkout constraint: {e}")

    return constraints


def generate_order_completion_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    # Fields available in ValidationCriteria and generators: order_id, affiliation, value, tax, shipping, order_total, currency, coupon
    available_fields = ["items", "order_total"]
    selected_fields = random.sample(available_fields, random.randint(1, min(3, len(available_fields))))

    order_numeric_operators = [
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN,
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.GREATER_EQUAL,
        ComparisonOperator.LESS_EQUAL,
    ]

    # Mock some plausible order data for calculations and generating values
    random.randint(1, 10)
    mock_subtotal = round(random.uniform(20.0, 1000.0), 2)
    mock_order_total = round(mock_subtotal, 2)
    mock_order_data = {
        "items": mock_subtotal,
        "order_total": mock_order_total,
    }

    for field in selected_fields:
        value = mock_order_data.get(field)  # Get value from mock data
        if value is None:
            continue  # Skip if mock data doesn't have it

        op = random.choice(order_numeric_operators)

        # Generate constraint value using the mock order data for the specific field
        constraint_value = generate_constraint_value(field, op, mock_order_data, all_products_data=PRODUCTS_DATA)
        if constraint_value is not None:
            constraints_list.append(create_constraint_dict(field, op, constraint_value))  # Use the field name

    return constraints_list


def generate_carousel_scroll_constraints() -> list[dict[str, Any]]:
    constraints_list = []
    available_fields = ["direction", "title"]
    selected_fields = random.sample(available_fields, random.randint(1, len(available_fields)))

    direction_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]
    title_operators = [ComparisonOperator.EQUALS, ComparisonOperator.NOT_EQUALS]

    direction = random.choice(["LEFT", "RIGHT"])
    title = random.choice(["Technology", "Home", "Electronics", "Kitchen", "Fitness"])
    complete_title = f"Top Sellers In {title}"
    data = {"direction": direction, "title": complete_title}

    for field in selected_fields:
        op = None
        if field == "direction" and direction_operators:
            op = random.choice(direction_operators)
        elif field == "title" and title_operators:
            op = random.choice(title_operators)
        else:
            continue

        if op:
            constraint_value = generate_constraint_value(field, op, data)
            if constraint_value is not None:
                constraints_list.append(create_constraint_dict(field, op, constraint_value))

    return constraints_list
